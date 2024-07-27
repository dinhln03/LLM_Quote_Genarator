from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from utils import get_conversation

app = FastAPI()
security = HTTPBasic()

@app.get("/metadata")
def get_metadata():
    return {"my_metadata": "Quote generator version 1"}


# Please read more about this here
# https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
@app.post("/chat-auth")
async def chat(text: str, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username != "dinhln" or credentials.password != "ahihi":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    logger.info(f"User: {text}")
    response = await get_conversation(text)
    return {"response": response}

