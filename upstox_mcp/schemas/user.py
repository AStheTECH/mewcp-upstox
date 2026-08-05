"""User group schemas: get_profile, get_fund_and_margin_v3."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- get_profile -----------------------------------------------------------

class ProfileData(BaseModel):
    model_config = ConfigDict(extra="allow")

    email: str | None = None
    exchanges: list[str] | None = None
    products: list[str] | None = None
    broker: str | None = None
    user_id: str | None = None
    user_name: str | None = None
    order_types: list[str] | None = None
    user_type: str | None = None
    poa: bool | None = None
    ddpi: bool | None = None
    is_active: bool | None = None


class ProfileResult(ToolResult):
    data: ProfileData | None = None


# --- get_fund_and_margin_v3 --------------------------------------------------

class FundAndMarginDeliveryMargin(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    equity: float | None = None
    fo_settlement: float | None = None


class FundAndMarginLoss(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    realised: float | None = None
    unrealised: float | None = None


class FundAndMarginCashDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    opening_balance: float | None = None
    added_today: float | None = None
    withdrawn_today: float | None = None
    amount_from_stock_sale: float | None = None
    unpaid_charges: float | None = None


class FundAndMarginCashMarginUsed(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    span_exposure: float | None = None
    cash_margin_var_elm: float | None = None
    premium_present: float | None = None
    delivery_margin: FundAndMarginDeliveryMargin | None = None
    mtf: float | None = None
    loss: FundAndMarginLoss | None = None


class FundAndMarginCashAvailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    cash: FundAndMarginCashDetail | None = None
    margin_used: FundAndMarginCashMarginUsed | None = None


class FundAndMarginFromPledge(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    equity: float | None = None
    mutual_funds: float | None = None


class FundAndMarginPledgeMarginUsed(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    span_exposure: float | None = None
    cash_margin_var_elm: float | None = None
    premium_present: float | None = None
    delivery_margin: FundAndMarginDeliveryMargin | None = None
    mtf: float | None = None


class FundAndMarginPledgeAvailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    margin_from_pledge: FundAndMarginFromPledge | None = None
    margin_used: FundAndMarginPledgeMarginUsed | None = None


class FundAndMarginAvailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: float | None = None
    cash_available_to_trade: FundAndMarginCashAvailableToTrade | None = None
    pledge_available_to_trade: FundAndMarginPledgeAvailableToTrade | None = None


class FundAndMarginUnsettledProfit(BaseModel):
    model_config = ConfigDict(extra="allow")

    todays_profit: float | None = None
    previous_days: float | None = None


class FundAndMarginCashUnavailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    unsettled_profit: FundAndMarginUnsettledProfit | None = None


class FundAndMarginPledgeUnavailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    equity: float | None = None
    mutual_funds: float | None = None


class FundAndMarginUnavailableToTrade(BaseModel):
    model_config = ConfigDict(extra="allow")

    cash_unavailable_to_trade: FundAndMarginCashUnavailableToTrade | None = None
    pledge_unavailable_to_trade: FundAndMarginPledgeUnavailableToTrade | None = None


class FundAndMarginV3Data(BaseModel):
    model_config = ConfigDict(extra="allow")

    available_to_trade: FundAndMarginAvailableToTrade | None = None
    unavailable_to_trade: FundAndMarginUnavailableToTrade | None = None


class FundAndMarginV3Result(ToolResult):
    data: FundAndMarginV3Data | None = None
