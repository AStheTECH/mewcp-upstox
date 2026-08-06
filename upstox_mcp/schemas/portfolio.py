"""Portfolio group schemas: get_positions, get_holdings."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- get_positions -----------------------------------------------------------

class PositionEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    exchange: str | None = None
    multiplier: float | None = None
    value: float | None = None
    pnl: float | None = None
    product: str | None = None
    instrument_token: str | None = None
    average_price: float | None = None
    buy_value: float | None = None
    overnight_quantity: int | None = None
    day_buy_value: float | None = None
    day_buy_price: float | None = None
    overnight_buy_amount: float | None = None
    overnight_buy_quantity: int | None = None
    day_buy_quantity: int | None = None
    day_sell_value: float | None = None
    day_sell_price: float | None = None
    overnight_sell_amount: float | None = None
    overnight_sell_quantity: int | None = None
    day_sell_quantity: int | None = None
    quantity: int | None = None
    last_price: float | None = None
    unrealised: float | None = None
    realised: float | None = None
    sell_value: float | None = None
    trading_symbol: str | None = None
    close_price: float | None = None
    buy_price: float | None = None
    sell_price: float | None = None


class GetPositionsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    positions: list[PositionEntry]


class GetPositionsResult(ToolResult):
    data: GetPositionsData | None = None


# --- get_holdings --------------------------------------------------------------

class HoldingEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    isin: str | None = None
    cnc_used_quantity: int | None = None
    collateral_type: str | None = None
    company_name: str | None = None
    haircut: float | None = None
    product: str | None = None
    quantity: int | None = None
    trading_symbol: str | None = None
    last_price: float | None = None
    close_price: float | None = None
    pnl: float | None = None
    day_change: float | None = None
    day_change_percentage: float | None = None
    instrument_token: str | None = None
    average_price: float | None = None
    collateral_quantity: int | None = None
    collateral_update_quantity: int | None = None
    t1_quantity: int | None = None
    exchange: str | None = None


class GetHoldingsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    holdings: list[HoldingEntry]


class GetHoldingsResult(ToolResult):
    data: GetHoldingsData | None = None
