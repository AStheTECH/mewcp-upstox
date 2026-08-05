"""Orders group schemas: get_order_book, get_trade_history."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- get_order_book ----------------------------------------------------------

class OrderEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    exchange: str | None = None
    product: str | None = None
    price: float | None = None
    quantity: int | None = None
    status: str | None = None
    tag: str | None = None
    instrument_token: str | None = None
    placed_by: str | None = None
    trading_symbol: str | None = None
    order_type: str | None = None
    validity: str | None = None
    trigger_price: float | None = None
    disclosed_quantity: int | None = None
    transaction_type: str | None = None
    average_price: float | None = None
    filled_quantity: int | None = None
    pending_quantity: int | None = None
    status_message: str | None = None
    status_message_raw: str | None = None
    exchange_order_id: str | None = None
    parent_order_id: str | None = None
    order_id: str | None = None
    variety: str | None = None
    order_timestamp: str | None = None
    exchange_timestamp: str | None = None
    is_amo: bool | None = None
    order_request_id: str | None = None
    order_ref_id: str | None = None


class OrderBookData(BaseModel):
    model_config = ConfigDict(extra="allow")

    orders: list[OrderEntry]


class OrderBookResult(ToolResult):
    data: OrderBookData | None = None


# --- get_trade_history ---------------------------------------------------------

class TradeEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    exchange: str | None = None
    segment: str | None = None
    option_type: str | None = None
    quantity: int | None = None
    amount: float | None = None
    trade_id: str | None = None
    trade_date: str | None = None
    transaction_type: str | None = None
    scrip_name: str | None = None
    strike_price: float | None = None
    expiry: str | None = None
    price: float | None = None
    isin: str | None = None
    symbol: str | None = None
    instrument_token: str | None = None


class PageMetaData(BaseModel):
    model_config = ConfigDict(extra="allow")

    page_number: int | None = None
    page_size: int | None = None
    total_records: int | None = None
    total_pages: int | None = None


class TradeHistoryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    trades: list[TradeEntry]
    meta_data: PageMetaData | None = None


class TradeHistoryResult(ToolResult):
    data: TradeHistoryData | None = None
