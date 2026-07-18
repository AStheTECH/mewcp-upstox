# Upstox MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes the
[Upstox](https://upstox.com/developer/api-documentation) trading API for AI workflows —
authentication, account info, NSE instrument search, live quotes and historical market
data.

Built with [FastMCP](https://github.com/jlowin/fastmcp). Every tool returns a
standardized envelope:

```json
{ "success": true, "statusCode": 200, "error": null, "data": { } }
```

## Project structure

```
upstox-mcp/
├── server.py                 # entrypoint (stdio / sse / http transports)
├── upstox_mcp/               # core module
│   ├── auth.py               # OAuth flow + token resolution
│   ├── client.py             # Upstox HTTP client + instrument search
│   ├── envelope.py           # standardized response envelope
│   └── tools.py              # MCP tool definitions
├── tests/test_server.py      # in-process smoke tests
├── scrip_mapping.csv         # NSE company → ISIN mapping (search index)
├── claude_desktop_config.json# sample client config
├── requirements.txt · Dockerfile · .env.example · LICENSE.md
```

## Setup

```bash
cd upstox-mcp
cp .env.example .env          # fill in UPSTOX_API_KEY / UPSTOX_API_SECRET
pip install -r requirements.txt
python server.py              # stdio transport (default)
```

**Claude Desktop / Claude Code** — merge `claude_desktop_config.json` into your MCP
config (or `claude mcp add upstox -- /path/to/venv/bin/python /path/to/server.py`).

**HTTP / SSE** — set `MCP_TRANSPORT=http` (or `sse`), `MCP_SERVER_HOST`,
`MCP_SERVER_PORT` in `.env`.

**Docker**

```bash
docker build -t upstox-mcp .
docker run --env-file .env -p 8080:8080 upstox-mcp
```

## Authentication

Upstox access tokens **expire daily** (~3:30 AM IST) and require an interactive
login — there is no refresh token. The flow, as tools:

1. `get_auth_url` → user opens the URL and logs in to Upstox
2. Upstox redirects to `UPSTOX_REDIRECT_URI` with `?code=...`
3. `exchange_code_for_token` (accepts the code *or* the whole redirect URL) →
   token saved to `token.json`
4. `get_token_status` → confirm source + expiry

Token resolution order (first valid, unexpired JWT wins):
`token.json` (this server) → `../strats/strategy_hub/token.json` (shared with the
Strategy Hub, so one login serves both) → `UPSTOX_ACCESS_TOKEN` env var.

## Tool reference

### Auth

| Tool | Input | Output `data` |
|---|---|---|
| `get_auth_url` | — | `auth_url`, `next_step` |
| `exchange_code_for_token` | `code` (auth code or full redirect URL) | token status |
| `get_token_status` | — | `authenticated`, `source`, `expires_at` |
| `set_access_token` | `access_token` (JWT) | token status |

### Account

| Tool | Input | Output `data` |
|---|---|---|
| `get_profile` | — | user name, id, enabled exchanges/products |
| `get_funds_and_margin` | — | equity & commodity funds/margin |

### Instruments

| Tool | Input | Output `data` |
|---|---|---|
| `search_instruments` | `query`, `limit` (1-20, default 5) | fuzzy matches: `company_name`, `isin`, `instrument_key`, `match_score` |

Instrument keys have the form **`NSE_EQ|<ISIN>`** (e.g. `NSE_EQ|INE155A01022` for
Tata Motors) — always obtain them from `search_instruments`.

### Market data

| Tool | Input | Output `data` |
|---|---|---|
| `get_quotes` | `instrument_keys` (list, ≤50) | full quotes: LTP, OHLC, net change, depth |
| `get_ltp` | `instrument_keys` (list, ≤50) | last traded price only |
| `get_historical_candles` | `instrument_key`, `from_date`, `to_date` (YYYY-MM-DD), `unit` (minutes/hours/days/weeks/months), `interval` | `candles`: `[ts, open, high, low, close, volume, oi]`, newest first |
| `get_intraday_candles` | `instrument_key`, `unit`, `interval` | today's candles, same shape |
| `get_market_holidays` | `date` (optional YYYY-MM-DD) | holiday list / date status |

### Conventions

- **Dates**: `YYYY-MM-DD`. Candle timestamps are ISO 8601 with IST offset (`+05:30`).
- **Errors**: `success: false` with `statusCode` mirroring the HTTP status and a
  human-readable `error`. `401` always means "re-run the auth flow".
- **Read-only**: this server intentionally exposes no order-placement tools.

## Testing

```bash
python tests/test_server.py
```

Runs an in-process MCP client against the server: tool registration, envelope
shape, auth-error paths, and (when a valid token exists) live profile/quote/candle
calls.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Not authenticated` / `statusCode: 401` | Run `get_auth_url` → `exchange_code_for_token`; tokens expire daily |
| `Upstox rejected the code: Invalid Auth code` | Codes are single-use and short-lived — redo the login |
| `Invalid Instrument key` | Use `search_instruments`; ISINs change after corporate actions (splits) |
| Redirect lands on an error page | `UPSTOX_REDIRECT_URI` must exactly match the URI registered on the Upstox app |
| Search returns nothing | `scrip_mapping.csv` must sit next to `server.py` |

## Legacy

The previous flat prototype (agents, SSE experiments) is preserved untouched in
`legacy/` (gitignored).
