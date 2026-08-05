"""Margins group: get_margin_details."""

import logging
from typing import Literal

import upstox_client
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.margins import MarginDetailsData, MarginDetailsResult
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("upstox-mcp.tools.margins")


class InstrumentInput(BaseModel):
    instrument_key: str = Field(description="Key of the instrument.")
    quantity: int = Field(description="Order quantity — must be a multiple of lot size.")
    product: Literal["I", "D", "CO", "MTF"] = Field(
        description="Product the order would use."
    )
    transaction_type: Literal["BUY", "SELL"] = Field(description="BUY or SELL.")
    price: float | None = Field(
        default=None, description="Price the order would be placed at."
    )


def register_margins_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_margin_details",
        description=(
            "Computes and returns the estimated margin for a proposed trade across one or "
            "more instruments. This only calculates an estimate — it does not place or "
            "persist any order. A maximum of 20 instruments is allowed per request."
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
            api_instance = upstox_client.ChargeApi(service.get_service())
            sdk_instruments = [
                upstox_client.Instrument(
                    instrument_key=inst.instrument_key,
                    quantity=inst.quantity,
                    product=inst.product,
                    transaction_type=inst.transaction_type,
                    price=inst.price,
                )
                for inst in instruments
            ]
            margin_body = upstox_client.MarginRequest(sdk_instruments)
            api_response = api_instance.post_margin(margin_body)
            tlog.success()
            return MarginDetailsResult(
                success=True,
                statusCode=200,
                data=MarginDetailsData(**api_response.data.to_dict()),
            )
        except Exception as exc:
            return _handle_request_exc(MarginDetailsResult, tlog, exc)
