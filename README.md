**Trade, check margins, and review orders on Upstox — without leaving your agent.**

A Model Context Protocol (MCP) server that exposes Upstox's API for retrieving user profile and fund details, estimating trade margins, and reviewing order books and trade history.


## Overview

The mewcp-upstox MCP Server provides:

- Authenticated user profile and fund/margin balance retrieval
- Pre-trade margin estimation across multiple instruments in a single call
- Order book and historical trade record lookups with date-range filtering

Perfect for:

- Trading assistants that need to check available balance before placing orders
- Portfolio and risk tools that estimate margin requirements ahead of execution
- Reporting agents that reconcile the day's orders or past trade history


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
- `product` (string, required) — Product the order would use. One of `I`, `D`, `CO`, `MTF`.
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
- `segment` (string, optional, default: null) — Segment to filter by. If omitted, all segments are included. Possible values: EQ (Equity), FO (Futures and Options), COM (Commodity), CD (Currency Derivatives), MF (Mutual Funds).
- `start_date` (string, required) — Start of the date range, YYYY-mm-dd. Must be within the last 3 financial years.
- `end_date` (string, required) — End of the date range, YYYY-mm-dd. Must be within the last 3 financial years and >= start_date.
- `page_number` (integer, required) — Page number, starting from 1.
- `page_size` (integer, required) — Page size for pagination (1-5000).
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

- `page_number` — Page number for `get_trade_history`, starting from 1.
- `page_size` — Page size for `get_trade_history` pagination (1-5000).
- `segment` — Optional trade segment filter for `get_trade_history`: `EQ` (Equity), `FO` (Futures and Options), `COM` (Commodity), `CD` (Currency Derivatives), `MF` (Mutual Funds).

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
One of: I (Intraday), D (Delivery), CO (Cover Order), MTF (Margin Trading Facility).
Used as `product` in `get_margin_details`.
```

**Date (YYYY-mm-dd):**

```
Calendar date string, e.g. 2026-01-15.
Used for `start_date` and `end_date` in `get_trade_history`.
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
