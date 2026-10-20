"""Upstream API client for MewCP Zoho Mail MCP Server."""

import logging
import re
from typing import Any

import requests
from fastmcp_credentials import get_credentials

from .config import ZOHO_MAIL_API_BASE, CONNECT_TIMEOUT, READ_TIMEOUT

logger = logging.getLogger("zoho-mail-mcp.service")

_MAIL_HOST = re.compile(r"^mail\.zoho(?:cloud)?\.[a-z.]+$")

_LOCATION_HOSTS = {
    "us": "mail.zoho.com",
    "eu": "mail.zoho.eu",
    "in": "mail.zoho.in",
    "com.au": "mail.zoho.com.au",
    "jp": "mail.zoho.jp",
    "ca": "mail.zohocloud.ca",
    "com.cn": "mail.zoho.com.cn",
    "ae": "mail.zoho.ae",
    "sa": "mail.zoho.sa",
}


def _derive_mail_host(extra: dict) -> str:
    accounts_server = extra.get("accounts_server")
    if accounts_server:
        host = accounts_server.split("://", 1)[-1].split("/", 1)[0]
        if host.startswith("accounts."):
            candidate = "mail." + host[len("accounts."):]
            if _MAIL_HOST.fullmatch(candidate):
                return candidate

    location = extra.get("location")
    if location and location in _LOCATION_HOSTS:
        candidate = _LOCATION_HOSTS[location]
        if _MAIL_HOST.fullmatch(candidate):
            return candidate

    raise ValueError("Missing or invalid accounts_server/location in credentials")


def _base_url() -> str:
    cred = get_credentials()
    extra = cred.extra or {}
    mail_host = _derive_mail_host(extra)
    return ZOHO_MAIL_API_BASE.format(mail_host=mail_host)


def _get_credential() -> str:
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")
    return cred.access_token


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Zoho-oauthtoken {_get_credential()}",
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
    url = f"{_base_url()}{endpoint}"
    resp = requests.request(method=method, url=url, headers=_auth_headers(),
                            json=body, params=params, timeout=timeout)
    try:
        data = resp.json()
    except Exception:
        data = {"error": resp.text or "Empty response body"}
    return data, resp.status_code, _parse_retry_after(resp.headers.get("Retry-After"))
