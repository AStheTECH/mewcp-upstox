"""MewCP Upstox tool registration."""

from fastmcp import FastMCP

from .user_tools import register_user_tools
from .margins_tools import register_margins_tools
from .orders_tools import register_orders_tools


def register_tools(mcp: FastMCP) -> None:
    register_user_tools(mcp)
    register_margins_tools(mcp)
    register_orders_tools(mcp)
