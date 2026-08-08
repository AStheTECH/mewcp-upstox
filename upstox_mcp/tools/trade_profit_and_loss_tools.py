"""Trade profit and loss group: get_report_meta_data, get_profit_loss_report."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.trade_profit_and_loss import (
    ProfitLossReportData,
    ProfitLossReportResult,
    ReportMetaDataData,
    ReportMetaDataResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("upstox-mcp.tools.trade_profit_and_loss")


def register_trade_profit_and_loss_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_report_meta_data",
        description=(
            "Retrieves metadata for the trade-wise profit and loss report for a given "
            "segment and financial year, optionally narrowed to a date range. Returns "
            "the total trade count and the maximum page_size accepted by "
            "get_profit_loss_report."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_report_meta_data(
        segment: str = Field(
            description=(
                "Segment to request data for. Possible values: EQ (Equity), FO (Futures "
                "and Options), COM (Commodity), CD (Currency Derivatives)."
            )
        ),
        financial_year: str = Field(
            description=(
                "Financial year to request data for — concatenation of the last 2 "
                "digits of the from-year and to-year, e.g. 2021-2022 -> 2122."
            )
        ),
        from_date: str | None = Field(
            default=None,
            description=(
                "Start of the date range, dd-mm-yyyy. Must fall within the same "
                "financial year as financial_year. Omit to cover the full financial year."
            ),
        ),
        to_date: str | None = Field(
            default=None,
            description=(
                "End of the date range, dd-mm-yyyy. Must fall within the same financial "
                "year as financial_year, and >= from_date. Omit to cover the full "
                "financial year."
            ),
        ),
    ) -> ReportMetaDataResult:
        tlog = ToolLogger(logger, "get_report_meta_data")

        try:
            params: dict[str, str] = {
                "segment": segment,
                "financial_year": financial_year,
            }
            if from_date is not None:
                params["from_date"] = from_date
            if to_date is not None:
                params["to_date"] = to_date

            data, status, retry_after = service.api_request(
                "GET", "/v2/trade/profit-loss/metadata",
                params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ReportMetaDataResult(
                    success=True,
                    statusCode=status,
                    data=ReportMetaDataData(**(data.get("data") or {})),
                )
            return _upstream_err(ReportMetaDataResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ReportMetaDataResult, tlog, exc)

    @mcp.tool(
        name="get_profit_loss_report",
        description=(
            "Retrieves the trade-wise profit and loss report entries for a given "
            "segment and financial year, optionally narrowed to a date range, paginated "
            "by page_number and page_size. The maximum accepted page_size is returned "
            "as data.page_size_limit by get_report_meta_data."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_profit_loss_report(
        segment: str = Field(
            description=(
                "Segment to request data for. Possible values: EQ (Equity), FO (Futures "
                "and Options), COM (Commodity), CD (Currency Derivatives)."
            )
        ),
        financial_year: str = Field(
            description=(
                "Financial year to request data for — concatenation of the last 2 "
                "digits of the from-year and to-year, e.g. 2021-2022 -> 2122."
            )
        ),
        page_number: int = Field(description="Page number, starting from 1."),
        page_size: int = Field(
            description=(
                "Page size for pagination (max 5000; the actual max for this account is "
                "obtained from get_report_meta_data's data.page_size_limit)."
            )
        ),
        from_date: str | None = Field(
            default=None,
            description=(
                "Start of the date range, dd-mm-yyyy. Must fall within the same "
                "financial year as financial_year. Omit to cover the full financial year."
            ),
        ),
        to_date: str | None = Field(
            default=None,
            description=(
                "End of the date range, dd-mm-yyyy. Must fall within the same financial "
                "year as financial_year, and >= from_date. Omit to cover the full "
                "financial year."
            ),
        ),
    ) -> ProfitLossReportResult:
        tlog = ToolLogger(logger, "get_profit_loss_report")

        try:
            params: dict[str, str] = {
                "segment": segment,
                "financial_year": financial_year,
                "page_number": str(page_number),
                "page_size": str(page_size),
            }
            if from_date is not None:
                params["from_date"] = from_date
            if to_date is not None:
                params["to_date"] = to_date

            data, status, retry_after = service.api_request(
                "GET", "/v2/trade/profit-loss/data",
                params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                metadata = data.get("metadata") or {}
                return ProfitLossReportResult(
                    success=True,
                    statusCode=status,
                    data=ProfitLossReportData(
                        entries=data.get("data") or [],
                        meta_data=metadata.get("page"),
                    ),
                )
            return _upstream_err(ProfitLossReportResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ProfitLossReportResult, tlog, exc)
