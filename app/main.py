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

app = FastAPI()
security = HTTPBasic()


@app.get("/metadata")
def get_metadata():
    return {"my_metadata": "Quote generator version 1"}


@app.post("/chat-auth")
async def chat(
    text: str, credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    with tracer.start_as_current_span("chat-auth") as span:
        if credentials.username != "dinhln" or credentials.password != "ahihi":
            span.set_attribute("auth.success", False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        span.set_attribute("auth.success", True)
        logger.info(f"User: {text}")
        response = await get_conversation(text)
        span.set_attribute("response", response)
        return {"response": response}
