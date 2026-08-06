"""Configuration for MewCP Upstox MCP Server."""

import logging
import os

SERVER_VERSION = "v1.1.0"
BREAKING_CHANGES: list[dict] = []

# OAuth server, but Upstox's OAuth docs define no `scope` parameter on either the
# Authorize or Token requests — there is nothing to list here.
SCOPES = []

# Used only by the raw-HTTP fallback path in service.py; SDK-covered calls don't touch
# this constant. Upstox's endpoints carry their own API-version segment in the path
# itself (e.g. /v2/..., /v3/...), it's not part of this base.
UPSTOX_API_BASE = "https://api.upstox.com"

CONNECT_TIMEOUT = 5    # TCP connection — fixed across all servers
# Upstox has no documented SLA figure; 30s is the standard default used for trading
# APIs without a stated timeout.
READ_TIMEOUT = 30


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
