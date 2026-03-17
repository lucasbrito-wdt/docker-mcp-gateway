import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

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


@app.post("/mcp", dependencies=[Depends(verify_token)])
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}, status_code=400)

    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "docker-mcp-gateway", "version": "1.0.0"},
            },
        })

    if method == "tools/list":
        return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        handler = DISPATCHER.get(tool_name)
        if handler is None:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            })

        result = handler(arguments)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": str(result)}]},
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    })
