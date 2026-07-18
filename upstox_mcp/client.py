"""Thin Upstox HTTP client returning the standardized envelope."""
import csv
import os

import requests
from rapidfuzz import fuzz, process

from . import auth
from .envelope import err, ok

API_BASE = "https://api.upstox.com"
SCRIP_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "scrip_mapping.csv")

_scrips = None


def _headers():
    token = auth.get_token()
    if not token:
        return None
    return {"Accept": "application/json", "Authorization": f"Bearer {token}",
            "x-api-key": auth.API_KEY}


def request(method, path, params=None):
    """Call an Upstox endpoint; always returns the envelope."""
    headers = _headers()
    if headers is None:
        return err("Not authenticated — call get_auth_url, then exchange_code_for_token.", 401)
    try:
        resp = requests.request(method, f"{API_BASE}{path}", headers=headers,
                                params=params, timeout=30)
    except requests.RequestException as e:
        return err(f"Network error: {e}", 502)
    if resp.status_code in (401, 403):
        return err("Upstox rejected the token — re-authenticate via get_auth_url.",
                   resp.status_code)
    try:
        body = resp.json()
    except ValueError:
        return err(f"Non-JSON response (HTTP {resp.status_code})", resp.status_code)
    if resp.status_code != 200 or body.get("status") == "error":
        errors = body.get("errors") or []
        detail = errors[0].get("message") if errors and isinstance(errors[0], dict) \
            else body.get("message", f"HTTP {resp.status_code}")
        return err(detail, resp.status_code, data=body)
    return ok(body.get("data", body), resp.status_code)


def load_scrips():
    global _scrips
    if _scrips is None:
        _scrips = []
        with open(SCRIP_CSV, newline="") as f:
            for row in csv.DictReader(f):
                isin, name = row.get("symbol", "").strip(), row.get("company_name", "").strip()
                if isin and name:
                    _scrips.append({"company_name": name, "isin": isin,
                                    "instrument_key": f"NSE_EQ|{isin}"})
    return _scrips


def search_instruments(query, limit=5):
    if not query or not query.strip():
        return err("query is required", 400)
    scrips = load_scrips()
    matches = process.extract(query.strip(), [s["company_name"] for s in scrips],
                              scorer=fuzz.WRatio, processor=lambda s: s.lower(),
                              limit=max(1, min(limit, 20)))
    results = []
    for _, score, idx in matches:
        hit = dict(scrips[idx])
        hit["match_score"] = round(score, 1)
        results.append(hit)
    return ok(results)
