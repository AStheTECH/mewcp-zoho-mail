"""Accounts group: list_accounts."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.accounts import AccountListData, AccountListResult
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("zoho-mail-mcp.tools.accounts")


def register_accounts_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_accounts",
        description=(
            "Retrieves all account details of the authenticated user, including each account's "
            "accountId, email addresses, storage, send-mail details, forwarding and vacation-reply "
            "settings. The accountId returned here is required by every account-scoped endpoint. "
            "A linked external (non-Zoho) account returns a smaller object than a native Zoho "
            "account, and some fields such as address, mailForward, and vacationResponse are "
            "absent when not configured — use mailboxAddress or sendMailDetails[].fromAddress, "
            "not emailAddress[].isPrimary, to find the address usable for sending mail."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_accounts() -> AccountListResult:
        tlog = ToolLogger(logger, "list_accounts")

        try:
            data, status, retry_after = service.api_request(
                "GET", "/accounts",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return AccountListResult(success=True, statusCode=status, data=AccountListData(**data))
            return _upstream_err(AccountListResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(AccountListResult, tlog, exc)
