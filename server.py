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
    # Best-effort: if the standard-library file isn't where sysconfig says on some
    # unusual interpreter layout, fall through to normal import resolution rather
    # than crash the server with a new error on a platform where the shadow package
    # may not even be present.
    try:
        import importlib.util
        import sysconfig

        _stdlib_uuid_path = f"{sysconfig.get_path('stdlib')}/uuid.py"
        _spec = importlib.util.spec_from_file_location("uuid", _stdlib_uuid_path)
        if _spec is not None and _spec.loader is not None:
            _stdlib_uuid = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_stdlib_uuid)
            sys.modules["uuid"] = _stdlib_uuid
    except Exception as _guard_exc:
        # Logging isn't configured yet this early in the file — stderr is the only
        # channel available, but a swallowed failure here must still be visible.
        print(f"uuid shadow guard skipped: {_guard_exc!r}", file=sys.stderr)

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
