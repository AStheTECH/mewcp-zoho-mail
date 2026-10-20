"""Labels group: list_labels."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.labels import LabelListData, LabelListResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("zoho-mail-mcp.tools.labels")


def register_labels_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_labels",
        description=(
            "Retrieves all labels for the specified Zoho Mail account, returning each label's "
            "labelId, tagId, displayName, color and sequence. The labelId returned here is "
            "required by label-specific and email/thread labelling endpoints."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_labels(
        accountId: str = Field(description="Identifies the account whose label details are retrieved. It can be retrieved from the Get User Account Details API."),
    ) -> LabelListResult:
        tlog = ToolLogger(logger, "list_labels")

        if not accountId:
            return _err(LabelListResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/accounts/{accountId}/labels",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return LabelListResult(success=True, statusCode=status, data=LabelListData(**data))
            return _upstream_err(LabelListResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(LabelListResult, tlog, exc)
