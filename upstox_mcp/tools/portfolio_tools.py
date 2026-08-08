"""Portfolio group: get_positions, get_holdings."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.portfolio import (
    GetHoldingsData,
    GetHoldingsResult,
    GetPositionsData,
    GetPositionsResult,
)
from ._helpers import _handle_request_exc, _upstream_err

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
            data, status, retry_after = service.api_request(
                "GET", "/v2/portfolio/short-term-positions",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetPositionsResult(
                    success=True,
                    statusCode=status,
                    data=GetPositionsData(positions=data.get("data") or []),
                )
            return _upstream_err(GetPositionsResult, tlog, status, data, retry_after)
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
            data, status, retry_after = service.api_request(
                "GET", "/v2/portfolio/long-term-holdings",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetHoldingsResult(
                    success=True,
                    statusCode=status,
                    data=GetHoldingsData(holdings=data.get("data") or []),
                )
            return _upstream_err(GetHoldingsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetHoldingsResult, tlog, exc)
