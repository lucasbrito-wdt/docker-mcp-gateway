import os
import secrets
from fastapi import Header, HTTPException


async def verify_token(authorization: str = Header(default=None)):
    auth_token = os.environ.get("MCP_AUTH_TOKEN")

    if not auth_token or len(auth_token) < 32:
        raise HTTPException(status_code=500, detail="MCP_AUTH_TOKEN is not configured or too short")

    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = parts[1]
    if not secrets.compare_digest(token, auth_token):
        raise HTTPException(status_code=401, detail="Invalid token")
