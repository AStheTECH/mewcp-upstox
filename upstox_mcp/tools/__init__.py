"""MewCP Upstox tool registration."""

from fastmcp import FastMCP

from .user_tools import register_user_tools
from .margins_tools import register_margins_tools
from .orders_tools import register_orders_tools
from .portfolio_tools import register_portfolio_tools
from .fundamentals_tools import register_fundamentals_tools
from .trade_profit_and_loss_tools import register_trade_profit_and_loss_tools


def register_tools(mcp: FastMCP) -> None:
    register_user_tools(mcp)
    register_margins_tools(mcp)
    register_orders_tools(mcp)
    register_portfolio_tools(mcp)
    register_fundamentals_tools(mcp)
    register_trade_profit_and_loss_tools(mcp)
