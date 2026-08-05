"""User group: get_profile, get_fund_and_margin_v3."""

import logging

import upstox_client
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.user import (
    FundAndMarginV3Data,
    FundAndMarginV3Result,
    ProfileData,
    ProfileResult,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("upstox-mcp.tools.user")


def register_user_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_profile",
        description=(
            "Retrieves the authenticated user's profile information, returning email, "
            "exchanges, products, broker, user ID, order types, user type, and "
            "account/authorization flags."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_profile() -> ProfileResult:
        tlog = ToolLogger(logger, "get_profile")

        try:
            api_instance = upstox_client.UserApi(service.get_service())
            api_response = api_instance.get_profile(api_version="2.0")
            tlog.success()
            return ProfileResult(
                success=True,
                statusCode=200,
                data=ProfileData(**api_response.data.to_dict()),
            )
        except Exception as exc:
            return _handle_request_exc(ProfileResult, tlog, exc)

    @mcp.tool(
        name="get_fund_and_margin_v3",
        description=(
            "Retrieves the authenticated user's fund and margin details via the V3 "
            "endpoint, returning a detailed balance breakdown of cash and pledged "
            "margin available and unavailable to trade."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_fund_and_margin_v3() -> FundAndMarginV3Result:
        tlog = ToolLogger(logger, "get_fund_and_margin_v3")

        try:
            data, status, retry_after = service.api_request(
                "GET", "/v3/user/get-funds-and-margin",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return FundAndMarginV3Result(
                    success=True,
                    statusCode=status,
                    data=FundAndMarginV3Data(**data.get("data", {})),
                )
            return _upstream_err(FundAndMarginV3Result, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(FundAndMarginV3Result, tlog, exc)
