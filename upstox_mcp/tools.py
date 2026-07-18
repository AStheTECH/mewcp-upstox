"""MCP tool definitions. Every tool returns the standardized envelope:
{"success": bool, "statusCode": int, "error": str | None, "data": ...}
"""
from typing import Annotated

from pydantic import Field

from . import auth, client
from .envelope import err, ok


def register_tools(mcp):
    # ---------------- auth ----------------

    @mcp.tool
    def get_auth_url() -> dict:
        """Get the Upstox OAuth authorization URL. The user must open it, log in,
        and copy the `code` query parameter from the redirect URL. Upstox access
        tokens expire daily, so this flow repeats every trading day."""
        return ok({
            "auth_url": auth.login_url(),
            "next_step": "Open the URL, log in, then call exchange_code_for_token "
                         "with the `code` parameter (or the full redirect URL).",
        })

    @mcp.tool
    def exchange_code_for_token(
        code: Annotated[str, Field(description="Authorization code from the redirect URL, or the full redirect URL itself")],
    ) -> dict:
        """Exchange an Upstox authorization code for an access token and persist it
        for all subsequent tool calls."""
        token, error = auth.exchange_code(code)
        if error:
            return err(error, 400)
        return ok({"message": "Access token obtained and saved.",
                   **auth.token_status()})

    @mcp.tool
    def get_token_status() -> dict:
        """Check whether a valid Upstox access token is available, where it came
        from, and when it expires."""
        return ok(auth.token_status())

    @mcp.tool
    def set_access_token(
        access_token: Annotated[str, Field(description="A valid Upstox access token (JWT), e.g. generated on the developer dashboard")],
    ) -> dict:
        """Manually set an Upstox access token (alternative to the OAuth flow)."""
        saved, error = auth.set_token(access_token)
        if not saved:
            return err(error, 400)
        return ok(auth.token_status())

    # ---------------- account ----------------

    @mcp.tool
    def get_profile() -> dict:
        """Get the authenticated user's Upstox profile (name, user id, exchanges
        enabled, products allowed)."""
        return client.request("GET", "/v2/user/profile")

    @mcp.tool
    def get_funds_and_margin() -> dict:
        """Get available funds and margin for the equity and commodity segments."""
        return client.request("GET", "/v2/user/get-funds-and-margin")

    # ---------------- instruments ----------------

    @mcp.tool
    def search_instruments(
        query: Annotated[str, Field(description="Company name or fragment, e.g. 'reliance', 'tata motors'")],
        limit: Annotated[int, Field(description="Max matches to return (1-20)", ge=1, le=20)] = 5,
    ) -> dict:
        """Fuzzy-search NSE equities by company name. Returns instrument_key values
        (format 'NSE_EQ|<ISIN>') to use with the market-data tools."""
        return client.search_instruments(query, limit)

    # ---------------- market data ----------------

    @mcp.tool
    def get_quotes(
        instrument_keys: Annotated[list[str], Field(description="Instrument keys, e.g. ['NSE_EQ|INE155A01022'] (max 50)")],
    ) -> dict:
        """Full market quotes (last price, OHLC, net change, depth) for up to 50
        instruments."""
        if not instrument_keys:
            return err("instrument_keys is required", 400)
        return client.request("GET", "/v2/market-quote/quotes",
                              params={"instrument_key": ",".join(instrument_keys[:50])})

    @mcp.tool
    def get_ltp(
        instrument_keys: Annotated[list[str], Field(description="Instrument keys, e.g. ['NSE_EQ|INE155A01022']")],
    ) -> dict:
        """Last traded price for up to 50 instruments (lighter than get_quotes)."""
        if not instrument_keys:
            return err("instrument_keys is required", 400)
        return client.request("GET", "/v2/market-quote/ltp",
                              params={"instrument_key": ",".join(instrument_keys[:50])})

    @mcp.tool
    def get_historical_candles(
        instrument_key: Annotated[str, Field(description="e.g. 'NSE_EQ|INE155A01022' (from search_instruments)")],
        from_date: Annotated[str, Field(description="Start date, YYYY-MM-DD")],
        to_date: Annotated[str, Field(description="End date, YYYY-MM-DD")],
        unit: Annotated[str, Field(description="Candle unit: minutes | hours | days | weeks | months")] = "days",
        interval: Annotated[str, Field(description="Candle interval within the unit, e.g. '1', '5', '15'")] = "1",
    ) -> dict:
        """Historical OHLCV candles. Each candle is
        [timestamp, open, high, low, close, volume, open_interest], oldest last."""
        return client.request(
            "GET", f"/v3/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}")

    @mcp.tool
    def get_intraday_candles(
        instrument_key: Annotated[str, Field(description="e.g. 'NSE_EQ|INE155A01022'")],
        unit: Annotated[str, Field(description="minutes | hours | days")] = "minutes",
        interval: Annotated[str, Field(description="e.g. '1', '5', '15', '30'")] = "5",
    ) -> dict:
        """Today's intraday OHLCV candles for one instrument."""
        return client.request(
            "GET", f"/v3/historical-candle/intraday/{instrument_key}/{unit}/{interval}")

    @mcp.tool
    def get_market_holidays(
        date: Annotated[str, Field(description="Optional specific date YYYY-MM-DD; empty for the full year")] = "",
    ) -> dict:
        """NSE/BSE market holidays — the full year's list, or one date's status."""
        path = f"/v2/market/holidays/{date}" if date else "/v2/market/holidays"
        return client.request("GET", path)
