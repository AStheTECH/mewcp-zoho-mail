"""Folders group: list_folders"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.folders import FolderListData, FolderListResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("zoho-mail-mcp.tools.folders")


def register_folders_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_folders",
        description=(
            "Lists all folders within the specified account, returning each folder's ID, name, "
            "path, type, IMAP access flag, and archive flag. folderType is not unique — "
            "Zoho-created folders such as Notification or Newsletter can also carry folderType "
            "\"Inbox\", so identify the actual Inbox by path (\"/Inbox\") rather than by folderType."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_folders(
        accountId: str = Field(description="ID of the account to list folders for. Obtained from the list_accounts tool."),
    ) -> FolderListResult:
        tlog = ToolLogger(logger, "list_folders")

        if not accountId:
            return _err(FolderListResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/accounts/{accountId}/folders",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return FolderListResult(
                    success=True, statusCode=status,
                    data=[FolderListData(**item) for item in data.get("data", [])],
                )
            return _upstream_err(FolderListResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(FolderListResult, tlog, exc)
