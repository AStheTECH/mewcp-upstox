"""Upstream API client for MewCP Upstox MCP Server."""

import logging
import os
from typing import Any

import requests
import upstox_client
from fastmcp_credentials import get_credentials

from .config import UPSTOX_API_BASE, CONNECT_TIMEOUT, READ_TIMEOUT

logger = logging.getLogger("upstox-mcp.service")

# Vercel's Python builder does not reliably ship certifi's cacert.pem data file
# alongside the package, which makes the upstox_client SDK's urllib3 pool fail
# with FileNotFoundError at request time (certifi.where() resolves to a path
# that doesn't exist in the deployed bundle). Vendoring our own copy inside the
# app's own source tree sidesteps that, since Vercel deploys the repo as-is.
_CA_BUNDLE = os.path.join(os.path.dirname(__file__), "certs", "cacert.pem")


def _get_credential() -> str:
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")
    return cred.access_token


def get_service() -> upstox_client.ApiClient:
    configuration = upstox_client.Configuration()
    configuration.access_token = _get_credential()
    configuration.ssl_ca_cert = _CA_BUNDLE
    return upstox_client.ApiClient(configuration)


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_credential()}",
        "Content-Type": "application/json",
    }


def _parse_retry_after(header: str | None) -> int | None:
    if not header:
        return None
    try:
        return int(header)
    except ValueError:
        return None


def api_request(
    method: str,
    endpoint: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: tuple[int, int] | None = None,
) -> tuple[dict[str, Any], int, int | None]:
    if timeout is None:
        timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)
    url = f"{UPSTOX_API_BASE}{endpoint}"
    resp = requests.request(method=method, url=url, headers=_auth_headers(),
                            json=body, params=params, timeout=timeout)
    try:
        data = resp.json()
    except Exception:
        data = {"error": resp.text or "Empty response body"}
    return data, resp.status_code, _parse_retry_after(resp.headers.get("Retry-After"))
