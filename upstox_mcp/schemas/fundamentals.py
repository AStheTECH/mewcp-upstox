"""Fundamentals group schemas: get_company_profile, get_balance_sheet."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


# --- get_company_profile ----------------------------------------------------

class SectorMarketCap(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: float | None = None
    unit: str | None = None
    formatted: str | None = None


class CompanyProfileData(BaseModel):
    model_config = ConfigDict(extra="allow")

    company_profile: str | None = None
    sector: str | None = None
    sector_market_cap_inr: SectorMarketCap | None = None
    sector_market_cap_usd: SectorMarketCap | None = None


class CompanyProfileResult(ToolResult):
    data: CompanyProfileData | None = None


# --- get_balance_sheet -------------------------------------------------------

class BalanceSheetHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_asset: float | None = None
    total_liability: float | None = None
    period: str | None = None


class BalanceSheetFullStatementHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    period: str | None = None
    value: float | None = None


class BalanceSheetFullStatementEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    particular: str | None = None
    history: list[BalanceSheetFullStatementHistoryEntry] | None = None


class BalanceSheetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None
    time_period: str | None = None
    units_in: str | None = None
    history: list[BalanceSheetHistoryEntry] | None = None
    full_statement: list[BalanceSheetFullStatementEntry] | None = None


class BalanceSheetResult(ToolResult):
    data: BalanceSheetData | None = None
