import json
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .auth import verify_token
from .docker_client import get_client
from .registry import DISPATCHER, TOOLS


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth_token = os.environ.get("MCP_AUTH_TOKEN", "")
    if len(auth_token) < 32:
        raise RuntimeError("MCP_AUTH_TOKEN must be set and at least 32 characters long")

    get_client()
    yield


app = FastAPI(title="Docker MCP Gateway", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/mcp")
async def mcp_sse():
    async def event_stream():
        yield "data: {\"type\": \"connected\"}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/mcp", dependencies=[Depends(verify_token)])
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    method = body.get("method")
    params = body.get("params", {})

    if method == "tools/list":
        return JSONResponse({"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        handler = DISPATCHER.get(tool_name)
        if handler is None:
            return JSONResponse({"error": f"unknown tool: {tool_name}"})

        result = handler(arguments)
        return JSONResponse(result)

    return JSONResponse({"error": "method not found"})
