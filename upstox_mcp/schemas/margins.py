from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class MarginEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    equity_margin: float | None = None
    total_margin: float | None = None
    exposure_margin: float | None = None
    tender_margin: float | None = None
    span_margin: float | None = None
    net_buy_premium: float | None = None
    additional_margin: float | None = None


class MarginDetailsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    required_margin: float
    final_margin: float
    margins: list[MarginEntry]


class MarginDetailsResult(ToolResult):
    data: MarginDetailsData | None = None
