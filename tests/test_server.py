"""In-process smoke tests for the Upstox MCP server.

Run:  ../venv/bin/python tests/test_server.py
Live-API tests are skipped automatically when no valid token is available.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client  # noqa: E402

from server import mcp  # noqa: E402
from upstox_mcp import auth  # noqa: E402

EXPECTED_TOOLS = {
    "get_auth_url", "exchange_code_for_token", "get_token_status", "set_access_token",
    "get_profile", "get_funds_and_margin", "search_instruments",
    "get_quotes", "get_ltp", "get_historical_candles", "get_intraday_candles",
    "get_market_holidays",
}


def payload(result):
    blocks = result if isinstance(result, list) else result.content
    return json.loads(blocks[0].text)


async def main():
    async with Client(mcp) as c:
        tools = {t.name for t in await c.list_tools()}
        assert EXPECTED_TOOLS <= tools, f"missing tools: {EXPECTED_TOOLS - tools}"
        print(f"tools registered: {len(tools)} OK")

        r = payload(await c.call_tool("get_auth_url", {}))
        assert r["success"] and "authorization/dialog" in r["data"]["auth_url"]
        print("get_auth_url OK")

        r = payload(await c.call_tool("get_token_status", {}))
        assert r["success"]
        print("get_token_status:", r["data"])

        r = payload(await c.call_tool("search_instruments", {"query": "reliance industries"}))
        assert r["success"] and r["data"][0]["instrument_key"].startswith("NSE_EQ|")
        print("search_instruments:", r["data"][0])

        # envelope on bad input
        r = payload(await c.call_tool("search_instruments", {"query": " "}))
        assert not r["success"] and r["statusCode"] == 400
        print("error envelope OK")

        r = payload(await c.call_tool("exchange_code_for_token", {"code": "bogus"}))
        assert not r["success"]
        print("bogus code rejected:", r["error"][:60])

        if auth.get_token():
            r = payload(await c.call_tool("get_profile", {}))
            assert r["success"], r
            print("get_profile:", r["data"].get("user_name"))

            r = payload(await c.call_tool(
                "get_ltp", {"instrument_keys": ["NSE_EQ|INE155A01022"]}))
            assert r["success"], r
            print("get_ltp OK:", list(r["data"].values())[0])

            r = payload(await c.call_tool("get_historical_candles", {
                "instrument_key": "NSE_EQ|INE155A01022",
                "from_date": "2026-06-25", "to_date": "2026-07-03",
                "unit": "days", "interval": "1"}))
            assert r["success"] and r["data"]["candles"], r
            print(f"get_historical_candles: {len(r['data']['candles'])} candles OK")

            r = payload(await c.call_tool("get_market_holidays", {}))
            print("get_market_holidays:", "OK" if r["success"] else r["error"])
        else:
            print("no valid token — skipped live-API tests")

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
