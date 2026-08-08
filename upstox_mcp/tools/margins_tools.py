"""Margins group: get_margin_details."""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.margins import MarginDetailsData, MarginDetailsResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("upstox-mcp.tools.margins")


class InstrumentInput(BaseModel):
    instrument_key: str = Field(description="Key of the instrument.")
    quantity: int = Field(description="Order quantity — must be a multiple of lot size.")
    product: Literal["I", "D", "CO", "MTF"] = Field(
        description="Product the order would use."
    )
    transaction_type: Literal["BUY", "SELL"] = Field(description="BUY or SELL.")
    price: float | None = Field(
        default=None,
        description="Price the order would be placed at. Omit for a market-price estimate.",
    )


def register_margins_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_margin_details",
        description=(
            "Computes and returns the estimated margin required for a proposed trade of "
            "up to 20 instruments. Does not place, modify, or persist any order."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_margin_details(
        instruments: list[InstrumentInput] = Field(
            description=(
                "Instruments to request margin details for (maximum 20 per request). Each "
                "item requires `instrument_key`, `quantity` (a multiple of lot size), "
                "`product` (`I`, `D`, `CO`, or `MTF`), and `transaction_type` (`BUY` or "
                "`SELL`); `price` is optional."
            ),
        ),
    ) -> MarginDetailsResult:
        tlog = ToolLogger(logger, "get_margin_details")

        # VALIDATION_ERROR guards — before the try block
        if len(instruments) > 20:
            return _err(
                MarginDetailsResult, tlog, "VALIDATION_ERROR",
                "A maximum of 20 instruments is allowed per request", 400,
            )

        try:
            body = {
                "instruments": [
                    inst.model_dump(exclude_none=True) for inst in instruments
                ]
            }

            data, status, retry_after = service.api_request(
                "POST", "/v2/charges/margin",
                body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return MarginDetailsResult(
                    success=True,
                    statusCode=status,
                    data=MarginDetailsData(**data.get("data", {})),
                )
            return _upstream_err(MarginDetailsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(MarginDetailsResult, tlog, exc)
