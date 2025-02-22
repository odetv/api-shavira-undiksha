import os
from fastapi import HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException
from dotenv import load_dotenv


load_dotenv()
bearer_token = os.getenv("API_SHAVIRA_BEARER_TOKEN")
header = APIKeyHeader(name="Authorization", auto_error=False)


#  Autherization bearer token API
def verify_bearer_token(request_http: Request, token: str = Depends(header)):
    if token is None or not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="No authentication")
    actual_token = token[7:]
    if actual_token != bearer_token:
        raise HTTPException(status_code=401, detail="Unauthorized authentication")