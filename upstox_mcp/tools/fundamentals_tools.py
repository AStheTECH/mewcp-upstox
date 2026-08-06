"""Fundamentals group: get_company_profile, get_balance_sheet."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.fundamentals import (
    BalanceSheetData,
    BalanceSheetResult,
    CompanyProfileData,
    CompanyProfileResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("upstox-mcp.tools.fundamentals")


def register_fundamentals_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_company_profile",
        description=(
            "Retrieves the company profile for a given ISIN — a business description, its "
            "sector, and the sector's total market capitalisation in both Indian Rupees and "
            "US Dollars."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_company_profile(
        isin: str = Field(description="ISIN of the company, e.g. INE002A01018."),
    ) -> CompanyProfileResult:
        tlog = ToolLogger(logger, "get_company_profile")

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/v2/fundamentals/{isin}/profile",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return CompanyProfileResult(
                    success=True,
                    statusCode=status,
                    data=CompanyProfileData(**data.get("data", {})),
                )
            return _upstream_err(CompanyProfileResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CompanyProfileResult, tlog, exc)

    @mcp.tool(
        name="get_balance_sheet",
        description=(
            "Retrieves balance sheet statement data for a given ISIN — summary total assets "
            "and liabilities by reporting period, plus an optional detailed line-item "
            "breakdown when `fs=true`. All monetary values are in Indian Rupees (Crore)."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_balance_sheet(
        isin: str = Field(description="ISIN of the company, e.g. INE002A01018."),
        type: str | None = Field(
            default=None,
            description=(
                "Financial statement type. Possible values: consolidated, standalone. "
                "Defaults to consolidated when omitted."
            ),
        ),
        fs: bool | None = Field(
            default=None,
            description=(
                "When true, includes a detailed line-item breakdown in the full_statement "
                "field of the response. Omit or set to false to exclude it."
            ),
        ),
    ) -> BalanceSheetResult:
        tlog = ToolLogger(logger, "get_balance_sheet")

        try:
            params: dict[str, str] = {}
            if type is not None:
                params["type"] = type
            if fs is not None:
                params["fs"] = "true" if fs else "false"

            data, status, retry_after = service.api_request(
                "GET", f"/v2/fundamentals/{isin}/balance-sheet",
                params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return BalanceSheetResult(
                    success=True,
                    statusCode=status,
                    data=BalanceSheetData(**data.get("data", {})),
                )
            return _upstream_err(BalanceSheetResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(BalanceSheetResult, tlog, exc)
