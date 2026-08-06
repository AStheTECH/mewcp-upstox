"""Portfolio group: get_positions, get_holdings."""

import logging

import upstox_client
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.portfolio import (
    GetHoldingsData,
    GetHoldingsResult,
    GetPositionsData,
    GetPositionsResult,
)
from ._helpers import _handle_request_exc

logger = logging.getLogger("upstox-mcp.tools.portfolio")


def register_portfolio_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_positions",
        description=(
            "Retrieves the positions currently held in the account and returns them as a "
            "list. Positions remain in this portfolio until sold or, for derivatives, until "
            "expiry (max three months); equity positions carried overnight are automatically "
            "shifted to the holdings portfolio the following trading day."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_positions() -> GetPositionsResult:
        tlog = ToolLogger(logger, "get_positions")

        try:
            api_instance = upstox_client.PortfolioApi(service.get_service())
            api_response = api_instance.get_positions(api_version="2.0")
            tlog.success()
            positions = [position.to_dict() for position in (api_response.data or [])]
            return GetPositionsResult(
                success=True,
                statusCode=200,
                data=GetPositionsData(positions=positions),
            )
        except Exception as exc:
            return _handle_request_exc(GetPositionsResult, tlog, exc)

    @mcp.tool(
        name="get_holdings",
        description=(
            "Retrieves the holdings currently held in the account and returns them as a "
            "list. A holding stays in place indefinitely — it's only removed when divested, "
            "delisted, or modified by exchange action."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_holdings() -> GetHoldingsResult:
        tlog = ToolLogger(logger, "get_holdings")

        try:
            api_instance = upstox_client.PortfolioApi(service.get_service())
            api_response = api_instance.get_holdings(api_version="2.0")
            tlog.success()
            holdings = [holding.to_dict() for holding in (api_response.data or [])]
            return GetHoldingsResult(
                success=True,
                statusCode=200,
                data=GetHoldingsData(holdings=holdings),
            )
        except Exception as exc:
            return _handle_request_exc(GetHoldingsResult, tlog, exc)
