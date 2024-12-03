import os
from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

from utils import get_conversation

# Configuration and Tracing Setup
try:
    app_user_name = os.environ["APP_USER_NAME"]
    app_password = os.environ["APP_PASSWORD"]
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")

set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "quote-gen"}))
)
tracer = get_tracer_provider().get_tracer("quote_gen", "0.1.2")
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.observability.svc.cluster.local",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
get_tracer_provider().add_span_processor(span_processor)

# FastAPI App
app = FastAPI()
security = HTTPBasic()


@app.get("/metadata")
def get_metadata():
    return {"my_metadata": "Quote generator version 1"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat-auth")
async def chat(
    text: str, credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    with tracer.start_as_current_span("chat-auth") as span:
        # More secure credential comparison
        if not (
            compare_digest(credentials.username, app_user_name)
            and compare_digest(credentials.password, app_password)
        ):
            span.set_attribute("auth.success", False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        # Input validation
        if not text :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input text"
            )

        span.set_attribute("auth.success", True)
        logger.info(f"User: {text}")

        try:
            response = await get_conversation(text)
            span.set_attribute("response", response)
            return {"response": response}
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
