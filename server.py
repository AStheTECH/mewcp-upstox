#!/usr/bin/env python3
"""Upstox MCP Server — entrypoint.

Exposes Upstox trading APIs (auth, profile, instrument search, quotes,
historical/intraday candles) as MCP tools for LLM agents.

Transports (MCP_TRANSPORT env var, default stdio):
    stdio  — for Claude Desktop / Claude Code (default)
    sse    — HTTP SSE on MCP_SERVER_HOST:MCP_SERVER_PORT
    http   — streamable HTTP on MCP_SERVER_HOST:MCP_SERVER_PORT
"""
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from upstox_mcp.tools import register_tools

load_dotenv()

mcp = FastMCP(
    "upstox-mcp",
    instructions=(
        "Tools for the Upstox (Indian stock broker) API. Call get_token_status first; "
        "if not authenticated, walk the user through get_auth_url → "
        "exchange_code_for_token. Instrument keys look like 'NSE_EQ|<ISIN>' — find "
        "them with search_instruments."
    ),
)
register_tools(mcp)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport in ("sse", "http", "streamable-http"):
        mcp.run(
            transport="sse" if transport == "sse" else "streamable-http",
            host=os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
            port=int(os.getenv("MCP_SERVER_PORT", "8080")),
        )
    else:
        mcp.run()  # stdio
