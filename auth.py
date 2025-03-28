import os
from fastapi import HTTPException, Security
from fastapi.security import api_key
from starlette import status
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

api_key_header = api_key.APIKeyHeader(name="X-API-KEY")


async def validate_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized - API Key is wrong"
        )
    return None
