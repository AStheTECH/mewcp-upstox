"""Orders group: get_order_book, get_trade_history."""

import logging

import upstox_client
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.orders import (
    OrderBookData,
    OrderBookResult,
    TradeHistoryData,
    TradeHistoryResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("upstox-mcp.tools.orders")


def register_orders_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_order_book",
        description=(
            "Retrieves the order book and returns all orders placed for the current day, "
            "each reflecting its latest status."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_order_book() -> OrderBookResult:
        tlog = ToolLogger(logger, "get_order_book")

        try:
            api_instance = upstox_client.OrderApi(service.get_service())
            api_response = api_instance.get_order_book(api_version="2.0")
            tlog.success()
            orders = [order.to_dict() for order in (api_response.data or [])]
            return OrderBookResult(
                success=True,
                statusCode=200,
                data=OrderBookData(orders=orders),
            )
        except Exception as exc:
            return _handle_request_exc(OrderBookResult, tlog, exc)

    @mcp.tool(
        name="get_trade_history",
        description=(
            "Retrieves historical trade records for a date range and returns the trade "
            "history the API reports, for at most the last 3 financial years."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_trade_history(
        segment: str | None = Field(
            default=None,
            description=(
                "Segment to filter by. If omitted, all segments are included. Possible "
                "values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD "
                "(Currency Derivatives), MF (Mutual Funds)."
            ),
        ),
        start_date: str = Field(
            description="Start of the date range, YYYY-mm-dd. Must be within the last 3 financial years."
        ),
        end_date: str = Field(
            description="End of the date range, YYYY-mm-dd. Must be within the last 3 financial years and >= start_date."
        ),
        page_number: int = Field(description="Page number, starting from 1."),
        page_size: int = Field(description="Page size for pagination (1-5000)."),
    ) -> TradeHistoryResult:
        tlog = ToolLogger(logger, "get_trade_history")

        # VALIDATION_ERROR guards — before the try block
        if page_size < 1 or page_size > 5000:
            return _err(TradeHistoryResult, tlog, "VALIDATION_ERROR", "page_size must be 1-5000", 400)

        try:
            api_instance = upstox_client.PostTradeApi(service.get_service())
            kwargs = {"segment": segment} if segment is not None else {}
            api_response = api_instance.get_trades_by_date_range(
                start_date, end_date, page_number, page_size, **kwargs
            )
            tlog.success()
            raw = api_response.to_dict()
            meta = raw.get("meta_data") or {}
            return TradeHistoryResult(
                success=True,
                statusCode=200,
                data=TradeHistoryData(
                    trades=raw.get("data") or [],
                    meta_data=meta.get("page"),
                ),
            )
        except Exception as exc:
            return _handle_request_exc(TradeHistoryResult, tlog, exc)
