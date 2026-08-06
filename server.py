#!/usr/bin/env python3
"""MewCP Upstox MCP Server."""

import sys

if "uuid" not in sys.modules:
    # upstox-python-sdk unconditionally depends on a defunct PyPI package literally
    # named "uuid" (Python 2-only, last released ~2009) that shadows Python's built-in
    # uuid module once installed and breaks pydantic's `from uuid import UUID` with a
    # SyntaxError (invalid decimal literal on legacy `1<<32L` syntax). Force-load the
    # real standard-library module first so every later `import uuid` — including
    # inside fastmcp/pydantic below — hits this cached copy instead of the shadow.
    import importlib.util
    import sysconfig

    _stdlib_uuid_path = f"{sysconfig.get_path('stdlib')}/uuid.py"
    _spec = importlib.util.spec_from_file_location("uuid", _stdlib_uuid_path)
    _stdlib_uuid = importlib.util.module_from_spec(_spec)
    sys.modules["uuid"] = _stdlib_uuid
    _spec.loader.exec_module(_stdlib_uuid)

import logging

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from fastmcp_credentials import CredentialMiddleware, HeaderCredentialBackend

from upstox_mcp.cli import parse_args
from upstox_mcp.config import BREAKING_CHANGES, SERVER_VERSION, configure_logging
from upstox_mcp.tools import register_tools

configure_logging()
logger = logging.getLogger("upstox-mcp")

# OAuth
backend = HeaderCredentialBackend()
mcp = FastMCP("MewCP Upstox MCP Server", version=SERVER_VERSION,
              middleware=[CredentialMiddleware(backend, "oauth")])

register_tools(mcp)


# /health MUST come before mcp.http_app() — routes are baked at http_app() time
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": mcp.name,
        "version": SERVER_VERSION,
        "breaking_changes": BREAKING_CHANGES,
    })


app = mcp.http_app(path="/mcp", transport="streamable-http", stateless_http=True)


if __name__ == "__main__":
    args = parse_args()
    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
    if args.host:
        run_kwargs["host"] = args.host
    if args.port:
        run_kwargs["port"] = args.port
    try:
        mcp.run(**run_kwargs)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server crashed: %s", e, exc_info=True)
        raise
