"""Trade profit and loss group schemas: get_report_meta_data, get_profit_loss_report."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- get_report_meta_data -----------------------------------------------------

class ReportMetaDataData(BaseModel):
    model_config = ConfigDict(extra="allow")

    trades_count: int | None = None
    page_size_limit: int | None = None


class ReportMetaDataResult(ToolResult):
    data: ReportMetaDataData | None = None


# --- get_profit_loss_report ----------------------------------------------------

class ProfitLossEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    quantity: float | None = None
    isin: str | None = None
    scrip_name: str | None = None
    trade_type: str | None = None
    buy_date: str | None = None
    buy_average: float | None = None
    sell_date: str | None = None
    sell_average: float | None = None
    buy_amount: float | None = None
    sell_amount: float | None = None


class ProfitLossPageMetaData(BaseModel):
    model_config = ConfigDict(extra="allow")

    page_number: int | None = None
    page_size: int | None = None


class ProfitLossReportData(BaseModel):
    model_config = ConfigDict(extra="allow")

    entries: list[ProfitLossEntry]
    meta_data: ProfitLossPageMetaData | None = None


class ProfitLossReportResult(ToolResult):
    data: ProfitLossReportData | None = None
