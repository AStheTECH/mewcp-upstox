"""Upstox OAuth 2.0 flow and access-token management.

Token resolution order (first valid JWT wins; validity = `exp` claim in the future):
  1. token.json next to this package (written by exchange_code_for_token)
  2. the Strategy Hub's token.json (../strats/strategy_hub/) — one login serves both
  3. UPSTOX_ACCESS_TOKEN from the environment / .env
"""
import base64
import json
import os
import time
import urllib.parse

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
HUB_TOKEN_FILE = os.path.normpath(
    os.path.join(BASE_DIR, "..", "strats", "strategy_hub", "token.json"))

API_KEY = os.getenv("UPSTOX_API_KEY", "")
API_SECRET = os.getenv("UPSTOX_API_SECRET", "")
REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI", "UPSTOX_REDIRECT_URI")

AUTH_DIALOG_URL = "https://api.upstox.com/v2/login/authorization/dialog"
TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"


def jwt_exp(token):
    """Expiry (unix ts) from a JWT payload, or None."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("exp")
    except Exception:
        return None


def _valid(token, margin=120):
    exp = jwt_exp(token) if token else None
    return exp is not None and exp > time.time() + margin


def _from_file(path):
    try:
        with open(path) as f:
            return json.load(f).get("access_token")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_token():
    """Best available access token, or None if every source is expired/missing."""
    for candidate in (_from_file(TOKEN_FILE), _from_file(HUB_TOKEN_FILE),
                      os.getenv("UPSTOX_ACCESS_TOKEN")):
        if _valid(candidate):
            return candidate
    return None


def token_status():
    sources = (("token.json", _from_file(TOKEN_FILE)),
               ("strategy_hub/token.json", _from_file(HUB_TOKEN_FILE)),
               ("environment", os.getenv("UPSTOX_ACCESS_TOKEN")))
    for name, candidate in sources:
        if _valid(candidate):
            exp = jwt_exp(candidate)
            return {"authenticated": True, "source": name,
                    "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(exp))}
    return {"authenticated": False, "source": None, "expires_at": None,
            "hint": "Call get_auth_url, log in, then exchange_code_for_token."}


def login_url():
    params = urllib.parse.urlencode({
        "response_type": "code", "client_id": API_KEY, "redirect_uri": REDIRECT_URI})
    return f"{AUTH_DIALOG_URL}?{params}"


def extract_code(text):
    """Accept a raw auth code or a full redirect URL containing ?code=..."""
    text = (text or "").strip()
    if "code=" in text:
        try:
            qs = urllib.parse.urlparse(text).query or text.split("?", 1)[-1]
            code = urllib.parse.parse_qs(qs).get("code", [None])[0]
            if code:
                return code.strip()
        except Exception:
            pass
    return text or None


def exchange_code(code):
    """Exchange an authorization code for an access token; persist to token.json.
    Returns (token, error)."""
    code = extract_code(code)
    if not code:
        return None, "No authorization code provided."
    if not API_SECRET:
        return None, "UPSTOX_API_SECRET is not configured (.env)."
    try:
        resp = requests.post(
            TOKEN_URL,
            headers={"accept": "application/json",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"code": code, "client_id": API_KEY, "client_secret": API_SECRET,
                  "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"},
            timeout=30)
        data = resp.json()
    except Exception as e:
        return None, f"Token request failed: {e}"
    token = data.get("access_token")
    if not token:
        errs = data.get("errors") or []
        detail = errs[0].get("message") if errs and isinstance(errs[0], dict) else data
        return None, f"Upstox rejected the code: {detail}"
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token, "obtained_at": int(time.time())}, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)
    return token, None


def set_token(token):
    """Manually persist a token (e.g. generated on the Upstox dashboard)."""
    if not _valid(token):
        return False, "Token is not a valid unexpired JWT."
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token, "obtained_at": int(time.time())}, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)
    return True, None
