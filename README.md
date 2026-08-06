**Trade, check margins, and review orders, portfolio, and fundamentals on Upstox — without leaving your agent.**

A Model Context Protocol (MCP) server that exposes Upstox's API for retrieving user profile and fund details, estimating trade margins, and reviewing orders, portfolio, company fundamentals, and profit and loss.


## Overview

The mewcp-upstox MCP Server provides:

- Authenticated user profile and fund/margin balance retrieval
- Pre-trade margin estimation across multiple instruments in a single call
- Order book and historical trade record lookups with date-range filtering
- Portfolio position and holding retrieval
- Company fundamentals lookup (profile and balance sheet) by ISIN
- Trade-wise profit and loss reporting by segment and financial year

Perfect for:

- Trading assistants that need to check available balance before placing orders
- Portfolio and risk tools that estimate margin requirements ahead of execution
- Reporting agents that reconcile the day's orders, trade history, or profit and loss
- Research tools that pull company fundamentals alongside portfolio data


## Tools


<details>
<summary><code>get_profile</code> — Retrieve the authenticated user's profile</summary>

Retrieves the authenticated user's account profile — email, exchanges, products, broker, user ID, order types, and account status flags. Does not include fund, margin, or balance data.

**Inputs:** None

**Output `data` schema:**

```typescript
{
  email: string | null;
  exchanges: string[] | null;
  products: string[] | null;
  broker: string | null;
  user_id: string | null;
  user_name: string | null;
  order_types: string[] | null;
  user_type: string | null;
  poa: boolean | null;
  ddpi: boolean | null;
  is_active: boolean | null;
}
```

</details>


<details>
<summary><code>get_fund_and_margin_v3</code> — Retrieve fund and margin balance details</summary>

Retrieves the user's current cash and pledged margin balance, broken down into amounts available and unavailable to trade. Unavailable daily from 12:00 AM to 5:30 AM IST, when it returns a 423 error instead of data.

**Inputs:** None

**Output `data` schema:**

```typescript
{
  available_to_trade: {
    total: number | null;
    cash_available_to_trade: {
      total: number | null;
      cash: {
        opening_balance: number | null;
        added_today: number | null;
        withdrawn_today: number | null;
        amount_from_stock_sale: number | null;
        unpaid_charges: number | null;
      } | null;
      margin_used: {
        total: number | null;
        span_exposure: number | null;
        cash_margin_var_elm: number | null;
        premium_present: number | null;
        delivery_margin: {
          total: number | null;
          equity: number | null;
          fo_settlement: number | null;
        } | null;
        mtf: number | null;
        loss: {
          total: number | null;
          realised: number | null;
          unrealised: number | null;
        } | null;
      } | null;
    } | null;
    pledge_available_to_trade: {
      total: number | null;
      margin_from_pledge: {
        total: number | null;
        equity: number | null;
        mutual_funds: number | null;
      } | null;
      margin_used: {
        total: number | null;
        span_exposure: number | null;
        cash_margin_var_elm: number | null;
        premium_present: number | null;
        delivery_margin: {
          total: number | null;
          equity: number | null;
          fo_settlement: number | null;
        } | null;
        mtf: number | null;
      } | null;
    } | null;
  } | null;
  unavailable_to_trade: {
    cash_unavailable_to_trade: {
      unsettled_profit: {
        todays_profit: number | null;
        previous_days: number | null;
      } | null;
    } | null;
    pledge_unavailable_to_trade: {
      equity: number | null;
      mutual_funds: number | null;
    } | null;
  } | null;
}
```

</details>


<details>
<summary><code>get_margin_details</code> — Estimate margin for a proposed trade</summary>

Computes and returns the estimated margin required for a proposed trade of up to 20 instruments. Does not place, modify, or persist any order.

**Inputs:**
```
- `instruments` (array of object, required) — Instruments to request margin details for (maximum 20 per request). Each item requires `instrument_key`, `quantity` (a multiple of lot size), `product` (`I`, `D`, `CO`, or `MTF`), and `transaction_type` (`BUY` or `SELL`); `price` is optional.
```

Each item in `instruments`:
```
- `instrument_key` (string, required) — Key of the instrument.
- `quantity` (integer, required) — Order quantity — must be a multiple of lot size.
- `product` (string, required) — Product the order would use.
- `transaction_type` (string, required) — BUY or SELL.
- `price` (number, optional, default: null) — Price the order would be placed at. Omit for a market-price estimate.
```

**Output `data` schema:**

```typescript
{
  required_margin: number;
  final_margin: number;
  margins: {
    equity_margin: number | null;
    total_margin: number | null;
    exposure_margin: number | null;
    tender_margin: number | null;
    span_margin: number | null;
    net_buy_premium: number | null;
    additional_margin: number | null;
  }[];
}
```

</details>


<details>
<summary><code>get_order_book</code> — Retrieve today's order book</summary>

Retrieves all orders placed during the current trading day, each with its latest status. Does not return orders from previous days — those are cleared at end of session.

**Inputs:** None

**Output `data` schema:**

```typescript
{
  orders: {
    exchange: string | null;
    product: string | null;
    price: number | null;
    quantity: number | null;
    status: string | null;
    tag: string | null;
    instrument_token: string | null;
    placed_by: string | null;
    trading_symbol: string | null;
    order_type: string | null;
    validity: string | null;
    trigger_price: number | null;
    disclosed_quantity: number | null;
    transaction_type: string | null;
    average_price: number | null;
    filled_quantity: number | null;
    pending_quantity: number | null;
    status_message: string | null;
    status_message_raw: string | null;
    exchange_order_id: string | null;
    parent_order_id: string | null;
    order_id: string | null;
    variety: string | null;
    order_timestamp: string | null;
    exchange_timestamp: string | null;
    is_amo: boolean | null;
    order_request_id: string | null;
    order_ref_id: string | null;
  }[];
}
```

</details>


<details>
<summary><code>get_trade_history</code> — Retrieve historical trade records</summary>

Retrieves executed trade records for a given date range and optional segment, limited to at most the last 3 financial years.

**Inputs:**
```
- `start_date` (string, required) — Start of the date range, YYYY-mm-dd. Must be within the last 3 financial years.
- `end_date` (string, required) — End of the date range, YYYY-mm-dd. Must be within the last 3 financial years and >= start_date.
- `page_number` (integer, required) — Page number, starting from 1.
- `page_size` (integer, required) — Page size for pagination (1-5000).
- `segment` (string, optional, default: null) — Segment to filter by. If omitted, all segments are included. Possible values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD (Currency Derivatives), MF (Mutual Funds).
```

**Output `data` schema:**

```typescript
{
  trades: {
    exchange: string | null;
    segment: string | null;
    option_type: string | null;
    quantity: number | null;
    amount: number | null;
    trade_id: string | null;
    trade_date: string | null;
    transaction_type: string | null;
    scrip_name: string | null;
    strike_price: number | null;
    expiry: string | null;
    price: number | null;
    isin: string | null;
    symbol: string | null;
    instrument_token: string | null;
  }[];
  meta_data: {
    page_number: number | null;
    page_size: number | null;
    total_records: number | null;
    total_pages: number | null;
  } | null;
}
```

</details>


<details>
<summary><code>get_positions</code> — Retrieve current portfolio positions</summary>

Retrieves the positions currently held in the account and returns them as a list. Positions remain in this portfolio until sold or, for derivatives, until expiry (max three months); equity positions carried overnight are automatically shifted to the holdings portfolio the following trading day.

**Inputs:** None

**Output `data` schema:**

```typescript
{
  positions: {
    exchange: string | null;
    multiplier: number | null;
    value: number | null;
    pnl: number | null;
    product: string | null;
    instrument_token: string | null;
    average_price: number | null;
    buy_value: number | null;
    overnight_quantity: number | null;
    day_buy_value: number | null;
    day_buy_price: number | null;
    overnight_buy_amount: number | null;
    overnight_buy_quantity: number | null;
    day_buy_quantity: number | null;
    day_sell_value: number | null;
    day_sell_price: number | null;
    overnight_sell_amount: number | null;
    overnight_sell_quantity: number | null;
    day_sell_quantity: number | null;
    quantity: number | null;
    last_price: number | null;
    unrealised: number | null;
    realised: number | null;
    sell_value: number | null;
    trading_symbol: string | null;
    close_price: number | null;
    buy_price: number | null;
    sell_price: number | null;
  }[];
}
```

</details>


<details>
<summary><code>get_holdings</code> — Retrieve current portfolio holdings</summary>

Retrieves the holdings currently held in the account and returns them as a list. A holding stays in place indefinitely — it's only removed when divested, delisted, or modified by exchange action.

**Inputs:** None

**Output `data` schema:**

```typescript
{
  holdings: {
    isin: string | null;
    cnc_used_quantity: number | null;
    collateral_type: string | null;
    company_name: string | null;
    haircut: number | null;
    product: string | null;
    quantity: number | null;
    trading_symbol: string | null;
    last_price: number | null;
    close_price: number | null;
    pnl: number | null;
    day_change: number | null;
    day_change_percentage: number | null;
    instrument_token: string | null;
    average_price: number | null;
    collateral_quantity: number | null;
    collateral_update_quantity: number | null;
    t1_quantity: number | null;
    exchange: string | null;
  }[];
}
```

</details>


<details>
<summary><code>get_company_profile</code> — Retrieve a company's profile by ISIN</summary>

Retrieves the company profile for a given ISIN — a business description, its sector, and the sector's total market capitalisation in both Indian Rupees and US Dollars.

**Inputs:**
```
- `isin` (string, required) — ISIN of the company, e.g. INE002A01018.
```

**Output `data` schema:**

```typescript
{
  company_profile: string | null;
  sector: string | null;
  sector_market_cap_inr: {
    value: number | null;
    unit: string | null;
    formatted: string | null;
  } | null;
  sector_market_cap_usd: {
    value: number | null;
    unit: string | null;
    formatted: string | null;
  } | null;
}
```

</details>


<details>
<summary><code>get_balance_sheet</code> — Retrieve a company's balance sheet by ISIN</summary>

Retrieves balance sheet statement data for a given ISIN — summary total assets and liabilities by reporting period, plus an optional detailed line-item breakdown when `fs=true`. All monetary values are in Indian Rupees (Crore).

**Inputs:**
```
- `isin` (string, required) — ISIN of the company, e.g. INE002A01018.
- `type` (string, optional, default: null) — Financial statement type. Possible values: consolidated, standalone. Defaults to consolidated when omitted.
- `fs` (boolean, optional, default: null) — When true, includes a detailed line-item breakdown in the full_statement field of the response. Omit or set to false to exclude it.
```

**Output `data` schema:**

```typescript
{
  type: string | null;
  time_period: string | null;
  units_in: string | null;
  history: {
    total_asset: number | null;
    total_liability: number | null;
    period: string | null;
  }[] | null;
  full_statement: {
    particular: string | null;
    history: {
      period: string | null;
      value: number | null;
    }[] | null;
  }[] | null;
}
```

</details>


<details>
<summary><code>get_report_meta_data</code> — Retrieve trade profit and loss report metadata</summary>

Retrieves metadata for the trade-wise profit and loss report for a given segment and financial year, optionally narrowed to a date range. Returns the total trade count and the maximum page_size accepted by get_profit_loss_report.

**Inputs:**
```
- `segment` (string, required) — Segment to request data for. Possible values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD (Currency Derivatives).
- `financial_year` (string, required) — Financial year to request data for — concatenation of the last 2 digits of the from-year and to-year, e.g. 2021-2022 -> 2122.
- `from_date` (string, optional, default: null) — Start of the date range, dd-mm-yyyy. Must fall within the same financial year as financial_year. Omit to cover the full financial year.
- `to_date` (string, optional, default: null) — End of the date range, dd-mm-yyyy. Must fall within the same financial year as financial_year, and >= from_date. Omit to cover the full financial year.
```

**Output `data` schema:**

```typescript
{
  trades_count: number | null;
  page_size_limit: number | null;
}
```

</details>


<details>
<summary><code>get_profit_loss_report</code> — Retrieve trade-wise profit and loss report entries</summary>

Retrieves the trade-wise profit and loss report entries for a given segment and financial year, optionally narrowed to a date range, paginated by page_number and page_size. The maximum accepted page_size is returned as data.page_size_limit by get_report_meta_data.

**Inputs:**
```
- `segment` (string, required) — Segment to request data for. Possible values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD (Currency Derivatives).
- `financial_year` (string, required) — Financial year to request data for — concatenation of the last 2 digits of the from-year and to-year, e.g. 2021-2022 -> 2122.
- `page_number` (integer, required) — Page number, starting from 1.
- `page_size` (integer, required) — Page size for pagination (max 5000; the actual max for this account is obtained from get_report_meta_data's data.page_size_limit).
- `from_date` (string, optional, default: null) — Start of the date range, dd-mm-yyyy. Must fall within the same financial year as financial_year. Omit to cover the full financial year.
- `to_date` (string, optional, default: null) — End of the date range, dd-mm-yyyy. Must fall within the same financial year as financial_year, and >= from_date. Omit to cover the full financial year.
```

**Output `data` schema:**

```typescript
{
  entries: {
    quantity: number | null;
    isin: string | null;
    scrip_name: string | null;
    trade_type: string | null;
    buy_date: string | null;
    buy_average: number | null;
    sell_date: string | null;
    sell_average: number | null;
    buy_amount: number | null;
    sell_amount: number | null;
  }[];
  meta_data: {
    page_number: number | null;
    page_size: number | null;
  } | null;
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Response Envelope</strong></summary>

Every tool returns the same top-level envelope. Only `data` varies per tool.

```json
// Success
{
  "success": true,
  "statusCode": 200,
  "retriable": false,
  "retry_after_seconds": null,
  "error": null,
  "data": { ... }
}

// Error
{
  "success": false,
  "statusCode": 400,
  "retriable": false,
  "retry_after_seconds": null,
  "error": { "code": "VALIDATION_ERROR", "message": "description", "details": {} },
  "data": null
}
```

- `retriable` — `true` when it is safe to retry (rate limit, network error, 503). `false` for validation and auth errors.
- `retry_after_seconds` — seconds to wait before retrying; present only when `retriable` is `true` and the upstream specifies a delay.
- `error.code` — machine-readable string: `VALIDATION_ERROR`, `AUTH_ERROR`, `UPSTREAM_ERROR`, `SERVER_ERROR`.

</details>

<details>
<summary><strong>Common Parameters</strong></summary>

- `segment` — Trade segment. Possible values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD (Currency Derivatives) in `get_report_meta_data` and `get_profit_loss_report`; `get_trade_history` additionally accepts MF (Mutual Funds) and treats the parameter as optional (all segments included when omitted).
- `page_number` — Page number, starting from 1. Used in `get_trade_history` and `get_profit_loss_report`.
- `page_size` — Page size for pagination. `get_trade_history` accepts 1-5000; `get_profit_loss_report` accepts up to 5000, with the account-specific maximum returned as `data.page_size_limit` by `get_report_meta_data`.
- `financial_year` — Financial year to request data for — concatenation of the last 2 digits of the from-year and to-year, e.g. 2021-2022 -> 2122. Used in `get_report_meta_data` and `get_profit_loss_report`.
- `from_date` / `to_date` — Date range, dd-mm-yyyy, that must fall within the given `financial_year`; `to_date` >= `from_date`. Omit both to cover the full financial year. Used in `get_report_meta_data` and `get_profit_loss_report`.
- `isin` — ISIN of the company, e.g. INE002A01018. Used in `get_company_profile` and `get_balance_sheet`.

</details>

<details>
<summary><strong>Resource Formats</strong></summary>

**Instrument Key:**

```
Upstox instrument identifier used to reference a specific tradable instrument.
Used as `instrument_key` in `get_margin_details`.
```

**Product:**

```
One of: I, D, CO, MTF.
Used as `product` in `get_margin_details`.
```

**ISIN:**

```
International Securities Identification Number for a company.
Example: INE002A01018
Used as `isin` in `get_company_profile` and `get_balance_sheet`.
```

**Date (YYYY-mm-dd):**

```
Calendar date string, e.g. 2026-01-15.
Used for `start_date` and `end_date` in `get_trade_history`.
```

**Date (dd-mm-yyyy):**

```
Calendar date string, e.g. 15-01-2026.
Used for `from_date` and `to_date` in `get_report_meta_data` and `get_profit_loss_report`.
```

**Financial Year:**

```
Concatenation of the last 2 digits of the from-year and to-year.
Example: 2021-2022 -> 2122
Used as `financial_year` in `get_report_meta_data` and `get_profit_loss_report`.
```

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** API key not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_API_KEY` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check API key is active in your MewCP account

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No Upstox credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Connect your Upstox account (OAuth) or add your API key (static)
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters are included
  3. Check parameter types match expected values

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>Upstox API Error</strong></summary>

- **Cause:** Upstream Upstox API returned an error
- **Solution:**
  1. Check the error code against [Upstox's error code reference](https://upstox.com/developer/api-documentation/error-codes)
  2. Verify your credential has the required permissions
  3. Review the error message for specific details

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Upstox Request Structure](https://upstox.com/developer/api-documentation/request-structure)** — General request format and headers
- **[Upstox Response Structure](https://upstox.com/developer/api-documentation/response-structure)** — Success/error envelope shape
- **[Upstox Error Codes](https://upstox.com/developer/api-documentation/error-codes)** — HTTP and Upstox-specific error codes
- **[Upstox Rate Limits](https://upstox.com/developer/api-documentation/rate-limiting)** — Per-endpoint-category rate limits
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling

</details>
