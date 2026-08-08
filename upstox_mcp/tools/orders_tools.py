"""Orders group: get_order_book, get_trade_history."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.orders import (
    OrderBookData,
    OrderBookResult,
    TradeHistoryData,
    TradeHistoryResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("upstox-mcp.tools.orders")


def register_orders_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_order_book",
        description=(
            "Retrieves all orders placed during the current trading day, each with its "
            "latest status. Does not return orders from previous days — those are "
            "cleared at end of session."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_order_book() -> OrderBookResult:
        tlog = ToolLogger(logger, "get_order_book")

        try:
            data, status, retry_after = service.api_request(
                "GET", "/v2/order/retrieve-all",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return OrderBookResult(
                    success=True,
                    statusCode=status,
                    data=OrderBookData(orders=data.get("data") or []),
                )
            return _upstream_err(OrderBookResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(OrderBookResult, tlog, exc)

    @mcp.tool(
        name="get_trade_history",
        description=(
            "Retrieves executed trade records for a given date range and optional "
            "segment, limited to at most the last 3 financial years."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_trade_history(
        start_date: str = Field(
            description="Start of the date range, YYYY-mm-dd. Must be within the last 3 financial years."
        ),
        end_date: str = Field(
            description="End of the date range, YYYY-mm-dd. Must be within the last 3 financial years and >= start_date."
        ),
        page_number: int = Field(description="Page number, starting from 1."),
        page_size: int = Field(description="Page size for pagination (1-5000)."),
        segment: str | None = Field(
            default=None,
            description=(
                "Segment to filter by. If omitted, all segments are included. Possible "
                "values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD "
                "(Currency Derivatives), MF (Mutual Funds)."
            ),
        ),
    ) -> TradeHistoryResult:
        tlog = ToolLogger(logger, "get_trade_history")

        # VALIDATION_ERROR guards — before the try block
        if page_size < 1 or page_size > 5000:
            return _err(TradeHistoryResult, tlog, "VALIDATION_ERROR", "page_size must be 1-5000", 400)

        try:
            params: dict[str, str] = {
                "start_date": start_date,
                "end_date": end_date,
                "page_number": str(page_number),
                "page_size": str(page_size),
            }
            if segment is not None:
                params["segment"] = segment

            data, status, retry_after = service.api_request(
                "GET", "/v2/charges/historical-trades",
                params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                meta = data.get("meta_data") or {}
                return TradeHistoryResult(
                    success=True,
                    statusCode=status,
                    data=TradeHistoryData(
                        trades=data.get("data") or [],
                        meta_data=meta.get("page"),
                    ),
                )
            return _upstream_err(TradeHistoryResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(TradeHistoryResult, tlog, exc)
