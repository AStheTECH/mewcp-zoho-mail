"""Emails group: apply_labels_to_emails, delete_email, get_email_content, list_emails,
mark_email_as_read, mark_email_as_unread, move_emails, reply_to_email, save_draft,
search_emails, send_email."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.emails import (
    ApplyLabelsToEmailsData,
    ApplyLabelsToEmailsResult,
    DeleteEmailData,
    DeleteEmailResult,
    GetEmailContentData,
    GetEmailContentResult,
    ListEmailsData,
    ListEmailsResult,
    MarkEmailAsReadData,
    MarkEmailAsReadResult,
    MarkEmailAsUnreadData,
    MarkEmailAsUnreadResult,
    MoveEmailsData,
    MoveEmailsResult,
    ReplyToEmailData,
    ReplyToEmailResult,
    SaveDraftData,
    SaveDraftResult,
    SearchEmailsData,
    SearchEmailsResult,
    SendEmailData,
    SendEmailResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("zoho-mail-mcp.tools.emails")


def register_emails_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="apply_labels_to_emails",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Applies one or more labels to every email in messageId (or threadId) at once, in a "
            "single bulk call. "
            "This overwrites the current label set for every matched message or thread — the "
            "original label state is not returned and cannot be recovered from this call. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly how many messages/threads will be affected and "
            "which labels will be applied, and wait for their explicit written confirmation before "
            "proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def apply_labels_to_emails(
        accountId: str = Field(description="Identifies the specific account. Obtained from list_accounts."),
        messageId: list[str] = Field(description="Message IDs to apply the labels to. Obtained from list_emails or search_emails."),
        labelId: list[str] = Field(description="Label IDs to apply to the emails. Obtained from list_labels."),
        threadId: list[str] | None = Field(default=None, description="Thread IDs to apply the labels to instead of messageId, to label an entire thread at once."),
        isFolderSpecific: bool | None = Field(default=None, description="Whether this action is limited to a specific folder. If true, folderId must also be provided. Defaults to false."),
        folderId: str | None = Field(default=None, description="Folder whose messages are considered for this action, when isFolderSpecific is true. Obtained from list_folders."),
        isArchive: bool | None = Field(default=None, description="Whether archived emails are included. true includes both archived and non-archived emails; false excludes archived emails. Defaults to false."),
    ) -> ApplyLabelsToEmailsResult:
        tlog = ToolLogger(logger, "apply_labels_to_emails")

        if not accountId:
            return _err(ApplyLabelsToEmailsResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not messageId:
            return _err(ApplyLabelsToEmailsResult, tlog, "VALIDATION_ERROR", "messageId must have at least one entry", 400)
        if not labelId:
            return _err(ApplyLabelsToEmailsResult, tlog, "VALIDATION_ERROR", "labelId must have at least one entry", 400)
        if isFolderSpecific and not folderId:
            return _err(ApplyLabelsToEmailsResult, tlog, "VALIDATION_ERROR", "folderId is required when isFolderSpecific is true", 400)

        body = {"mode": "applyLabel", "messageId": messageId, "labelId": labelId}
        if threadId is not None:
            body["threadId"] = threadId
        if isFolderSpecific is not None:
            body["isFolderSpecific"] = isFolderSpecific
        if folderId is not None:
            body["folderId"] = folderId
        if isArchive is not None:
            body["isArchive"] = isArchive

        try:
            data, status, retry_after = service.api_request(
                "PUT", f"/accounts/{accountId}/updatemessage", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ApplyLabelsToEmailsResult(success=True, statusCode=status, data=ApplyLabelsToEmailsData())
            return _upstream_err(ApplyLabelsToEmailsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ApplyLabelsToEmailsResult, tlog, exc)

    @mcp.tool(
        name="delete_email",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Deletes a single email identified by accountId, folderId and messageId. "
            "By default the email is moved to the Trash folder; set expunge to true to delete it "
            "permanently without moving it to Trash — this is irreversible and the email cannot be "
            "recovered. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly what will be deleted and whether it is a "
            "permanent deletion, and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_email(
        accountId: str = Field(description="Identifies the specific account to fetch details. Obtained from list_accounts."),
        folderId: str = Field(description="Folder containing the email. Obtained from list_folders."),
        messageId: str = Field(description="Unique ID of the email to delete. Obtained from list_emails or search_emails."),
        expunge: bool | None = Field(default=None, description="Whether to delete the email permanently without moving it to Trash. Defaults to false (moved to Trash)."),
    ) -> DeleteEmailResult:
        tlog = ToolLogger(logger, "delete_email")

        if not accountId:
            return _err(DeleteEmailResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not folderId:
            return _err(DeleteEmailResult, tlog, "VALIDATION_ERROR", "folderId is required", 400)
        if not messageId:
            return _err(DeleteEmailResult, tlog, "VALIDATION_ERROR", "messageId is required", 400)

        params = {}
        if expunge is not None:
            params["expunge"] = expunge

        try:
            data, status, retry_after = service.api_request(
                "DELETE", f"/accounts/{accountId}/folders/{folderId}/messages/{messageId}",
                params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return DeleteEmailResult(success=True, statusCode=status, data=DeleteEmailData(**data.get("data", {})))
            return _upstream_err(DeleteEmailResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(DeleteEmailResult, tlog, exc)

    @mcp.tool(
        name="get_email_content",
        description=(
            "Retrieves the body content of a specific email by accountId, folderId and messageId. "
            "Returns the HTML content and the messageId; on a threaded message, pass "
            "includeBlockContent=true to get the reply (content) and the quoted parent "
            "(blockContent) separately — omitting it returns only the combined original content."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_email_content(
        accountId: str = Field(description="Identifies the specific account to fetch details. Obtained from list_accounts."),
        folderId: str = Field(description="Folder containing the email. Obtained from list_folders."),
        messageId: str = Field(description="Unique ID of the email. Obtained from list_emails or search_emails."),
        includeBlockContent: bool | None = Field(default=None, description="Whether to include the block quote (parent email) content separately from the reply content, for threaded emails."),
    ) -> GetEmailContentResult:
        tlog = ToolLogger(logger, "get_email_content")

        if not accountId:
            return _err(GetEmailContentResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not folderId:
            return _err(GetEmailContentResult, tlog, "VALIDATION_ERROR", "folderId is required", 400)
        if not messageId:
            return _err(GetEmailContentResult, tlog, "VALIDATION_ERROR", "messageId is required", 400)

        params = {}
        if includeBlockContent is not None:
            params["includeBlockContent"] = includeBlockContent

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/accounts/{accountId}/folders/{folderId}/messages/{messageId}/content",
                params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetEmailContentResult(success=True, statusCode=status, data=GetEmailContentData(**data.get("data", {})))
            return _upstream_err(GetEmailContentResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetEmailContentResult, tlog, exc)

    @mcp.tool(
        name="list_emails",
        description=(
            "Lists emails in a mailbox folder, or filtered by read/unread status, flag, label, "
            "thread or attachment presence, with start/limit paging. "
            "limit accepts 1-200 (default 10); start is the 1-based sequence number to page from "
            "(default 1). For a free-text or search-syntax query, use search_emails instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_emails(
        accountId: str = Field(description="Identifies the account from which emails are retrieved. Obtained from list_accounts."),
        folderId: str | None = Field(default=None, description="Folder to list emails from. Obtained from list_folders. Omit to search across the whole mailbox."),
        start: int | None = Field(default=None, description="1-based starting sequence number of the emails to retrieve. Defaults to 1."),
        limit: int | None = Field(default=None, description="Number of emails to retrieve from start. Range 1-200, defaults to 10."),
        status: str | None = Field(default=None, description="Filter by read status. One of read, unread, all. Defaults to all."),
        flagid: int | None = Field(default=None, description="Filter by flag type. 0 = flag not set, 1 = info, 2 = important, 3 = followup."),
        labelid: str | None = Field(default=None, description="Filter to emails with this label. Obtained from list_labels."),
        threadId: str | None = Field(default=None, description="Filter to emails belonging to this thread."),
        sortBy: str | None = Field(default=None, description="Field to sort by. One of date, messageId, size. Defaults to date."),
        sortorder: bool | None = Field(default=None, description="Sort order. true for ascending, false for descending. Defaults to false."),
        includeto: bool | None = Field(default=None, description="Whether to include the To address details. Defaults to false."),
        includesent: bool | None = Field(default=None, description="Whether to include sent emails in the list. Defaults to false."),
        includearchive: bool | None = Field(default=None, description="Whether to include archived emails in the list. Defaults to false."),
        attachedMails: bool | None = Field(default=None, description="If true, retrieve only emails with attachments; if false, retrieve all. Defaults to false."),
        inlinedMails: bool | None = Field(default=None, description="If true, retrieve only emails with inline images; if false, retrieve all. Defaults to false."),
        flaggedMails: bool | None = Field(default=None, description="If true, retrieve only flagged emails; if false, retrieve all. Defaults to false."),
        respondedMails: bool | None = Field(default=None, description="If true, retrieve only emails with replies; if false, retrieve all. Defaults to false."),
        threadedMails: bool | None = Field(default=None, description="If true, retrieve emails that are part of conversations; if false, retrieve all. Defaults to false."),
    ) -> ListEmailsResult:
        tlog = ToolLogger(logger, "list_emails")

        if not accountId:
            return _err(ListEmailsResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if limit is not None and not (1 <= limit <= 200):
            return _err(ListEmailsResult, tlog, "VALIDATION_ERROR", "limit must be between 1 and 200", 400)

        params = {}
        for key, value in {
            "folderId": folderId, "start": start, "limit": limit, "status": status,
            "flagid": flagid, "labelid": labelid, "threadId": threadId, "sortBy": sortBy,
            "sortorder": sortorder, "includeto": includeto, "includesent": includesent,
            "includearchive": includearchive, "attachedMails": attachedMails,
            "inlinedMails": inlinedMails, "flaggedMails": flaggedMails,
            "respondedMails": respondedMails, "threadedMails": threadedMails,
        }.items():
            if value is not None:
                params[key] = value

        try:
            data, status_code, retry_after = service.api_request(
                "GET", f"/accounts/{accountId}/messages/view", params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status_code < 300:
                tlog.success()
                items = data.get("data", [])
                return ListEmailsResult(
                    success=True, statusCode=status_code,
                    data=[ListEmailsData(**item) for item in items],
                )
            return _upstream_err(ListEmailsResult, tlog, status_code, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListEmailsResult, tlog, exc)

    @mcp.tool(
        name="mark_email_as_read",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Marks every email in messageId (or threadId) as read in a single bulk call. "
            "This overwrites the current read/unread state for every matched message or thread — "
            "the original state is not returned and cannot be recovered from this call. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly how many messages/threads will be marked read, "
            "and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def mark_email_as_read(
        accountId: str = Field(description="Identifies the specific account. Obtained from list_accounts."),
        messageId: list[str] | None = Field(default=None, description="Message IDs to mark as read. Obtained from list_emails or search_emails."),
        threadId: list[str] | None = Field(default=None, description="Thread IDs to mark as read."),
    ) -> MarkEmailAsReadResult:
        tlog = ToolLogger(logger, "mark_email_as_read")

        if not accountId:
            return _err(MarkEmailAsReadResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not messageId and not threadId:
            return _err(MarkEmailAsReadResult, tlog, "VALIDATION_ERROR", "either messageId or threadId must be provided", 400)

        body = {"mode": "markAsRead"}
        if messageId is not None:
            body["messageId"] = messageId
        if threadId is not None:
            body["threadId"] = threadId

        try:
            data, status, retry_after = service.api_request(
                "PUT", f"/accounts/{accountId}/updatemessage", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return MarkEmailAsReadResult(success=True, statusCode=status, data=MarkEmailAsReadData())
            return _upstream_err(MarkEmailAsReadResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(MarkEmailAsReadResult, tlog, exc)

    @mcp.tool(
        name="mark_email_as_unread",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Marks every email in messageId (or threadId) as unread in a single bulk call. "
            "This overwrites the current read/unread state for every matched message or thread — "
            "the original state is not returned and cannot be recovered from this call. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly how many messages/threads will be marked unread, "
            "and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def mark_email_as_unread(
        accountId: str = Field(description="Identifies the specific account. Obtained from list_accounts."),
        messageId: list[str] | None = Field(default=None, description="Message IDs to mark as unread. Obtained from list_emails or search_emails."),
        threadId: list[str] | None = Field(default=None, description="Thread IDs to mark as unread."),
    ) -> MarkEmailAsUnreadResult:
        tlog = ToolLogger(logger, "mark_email_as_unread")

        if not accountId:
            return _err(MarkEmailAsUnreadResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not messageId and not threadId:
            return _err(MarkEmailAsUnreadResult, tlog, "VALIDATION_ERROR", "either messageId or threadId must be provided", 400)

        body = {"mode": "markAsUnread"}
        if messageId is not None:
            body["messageId"] = messageId
        if threadId is not None:
            body["threadId"] = threadId

        try:
            data, status, retry_after = service.api_request(
                "PUT", f"/accounts/{accountId}/updatemessage", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return MarkEmailAsUnreadResult(success=True, statusCode=status, data=MarkEmailAsUnreadData())
            return _upstream_err(MarkEmailAsUnreadResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(MarkEmailAsUnreadResult, tlog, exc)

    @mcp.tool(
        name="move_emails",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Moves every email in messageId (or whole threads in threadId) from its current folder "
            "to destfolderId, in a single bulk call. "
            "This changes the folder of every matched message or thread — the original folder is "
            "not returned and cannot be recovered from this call. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly how many messages/threads will be moved and to "
            "which folder, and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def move_emails(
        accountId: str = Field(description="Identifies the specific account. Obtained from list_accounts."),
        messageId: list[str] = Field(description="Message IDs to move. Obtained from list_emails or search_emails."),
        destfolderId: str = Field(description="Folder to move the email(s) into. Obtained from list_folders."),
        threadId: list[str] | None = Field(default=None, description="Thread IDs to move instead of messageId, to move an entire thread at once."),
        isFolderSpecific: bool | None = Field(default=None, description="Whether this action is limited to a specific existing folder. If true, folderId must also be provided. Defaults to false."),
        folderId: str | None = Field(default=None, description="The existing folder the messages are being moved from, when isFolderSpecific is true. Obtained from list_folders."),
        isArchive: bool | None = Field(default=None, description="Whether archived emails are included. true includes both archived and non-archived emails; false excludes archived emails. Defaults to false."),
    ) -> MoveEmailsResult:
        tlog = ToolLogger(logger, "move_emails")

        if not accountId:
            return _err(MoveEmailsResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not messageId:
            return _err(MoveEmailsResult, tlog, "VALIDATION_ERROR", "messageId must have at least one entry", 400)
        if not destfolderId:
            return _err(MoveEmailsResult, tlog, "VALIDATION_ERROR", "destfolderId is required", 400)
        if isFolderSpecific and not folderId:
            return _err(MoveEmailsResult, tlog, "VALIDATION_ERROR", "folderId is required when isFolderSpecific is true", 400)

        body = {"mode": "moveMessage", "messageId": messageId, "destfolderId": destfolderId}
        if threadId is not None:
            body["threadId"] = threadId
        if isFolderSpecific is not None:
            body["isFolderSpecific"] = isFolderSpecific
        if folderId is not None:
            body["folderId"] = folderId
        if isArchive is not None:
            body["isArchive"] = isArchive

        try:
            data, status, retry_after = service.api_request(
                "PUT", f"/accounts/{accountId}/updatemessage", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return MoveEmailsResult(success=True, statusCode=status, data=MoveEmailsData())
            return _upstream_err(MoveEmailsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(MoveEmailsResult, tlog, exc)

    @mcp.tool(
        name="reply_to_email",
        description=(
            "Sends a reply to an existing email identified by messageId, immediately or scheduled "
            "when isSchedule is true. action must be sent as the lowercase value reply — the "
            "uppercase form documented elsewhere is rejected. fromAddress must be the account's "
            "Zoho mailbox address (mailboxAddress from list_accounts), not an external address, or "
            "delivery can fail even though the call returns success. scheduleType 6 requires both "
            "timeZone and scheduleTime; other scheduleType values need neither. Returns the sent "
            "reply's messageId and mailId."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def reply_to_email(
        accountId: str = Field(description="Identifies the account to send the reply from. Obtained from list_accounts."),
        messageId: str = Field(description="Identifies the message being replied to. Obtained from list_emails or search_emails."),
        fromAddress: str = Field(description="Sender's email address, associated with the authenticated account. Use the account's mailboxAddress, not an external address."),
        toAddress: str = Field(description="Recipient's email address."),
        action: str = Field(description="Which action to perform with the message. Must be the lowercase value 'reply'."),
        ccAddress: str | None = Field(default=None, description="Recipient's email address for the Cc field."),
        bccAddress: str | None = Field(default=None, description="Recipient's email address for the Bcc field."),
        subject: str | None = Field(default=None, description="Subject of the email."),
        content: str | None = Field(default=None, description="Body of the reply."),
        mailFormat: str | None = Field(default=None, description="Format of the mail. One of html, plaintext. Defaults to html."),
        askReceipt: str | None = Field(default=None, description="Whether a read receipt is requested from the recipient. One of yes, no."),
        encoding: str | None = Field(default=None, description="Encoding used in the email content, e.g. UTF-8, ISO-8859-1, Shift_JIS. Defaults to UTF-8."),
        isSchedule: bool | None = Field(default=None, description="Whether the reply should be scheduled instead of sent immediately."),
        scheduleType: int | None = Field(default=None, description="Type of scheduling: 1 after one hour, 2 after two hours, 3 after four hours, 4 by next morning, 5 by next afternoon, 6 a custom date/time."),
        timeZone: str | None = Field(default=None, description="Timezone to schedule the reply in. Required when scheduleType is 6."),
        scheduleTime: str | None = Field(default=None, description="Date and time to schedule the reply, format MM/DD/YYYY HH:MM:SS. Required when scheduleType is 6."),
    ) -> ReplyToEmailResult:
        tlog = ToolLogger(logger, "reply_to_email")

        if not accountId:
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not messageId:
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "messageId is required", 400)
        if not fromAddress:
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "fromAddress is required", 400)
        if not toAddress:
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "toAddress is required", 400)
        if action != "reply":
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "action must be the lowercase value 'reply'", 400)
        if scheduleType == 6 and (not timeZone or not scheduleTime):
            return _err(ReplyToEmailResult, tlog, "VALIDATION_ERROR", "timeZone and scheduleTime are required when scheduleType is 6", 400)

        body = {
            "fromAddress": fromAddress,
            "toAddress": toAddress,
            "action": action,
        }
        for key, value in {
            "ccAddress": ccAddress, "bccAddress": bccAddress, "subject": subject,
            "content": content, "mailFormat": mailFormat, "askReceipt": askReceipt,
            "encoding": encoding, "isSchedule": isSchedule, "scheduleType": scheduleType,
            "timeZone": timeZone, "scheduleTime": scheduleTime,
        }.items():
            if value is not None:
                body[key] = value

        try:
            data, status, retry_after = service.api_request(
                "POST", f"/accounts/{accountId}/messages/{messageId}", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ReplyToEmailResult(success=True, statusCode=status, data=ReplyToEmailData(**data.get("data", {})))
            return _upstream_err(ReplyToEmailResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ReplyToEmailResult, tlog, exc)

    @mcp.tool(
        name="save_draft",
        description=(
            "Saves an email as a draft or a template without sending it, selected via mode (draft "
            "or template). Omitting mode falls through to sending a real email instead of saving "
            "a draft, since the request is then processed as a normal send. fromAddress "
            "must be the account's Zoho mailbox address (mailboxAddress from list_accounts), not an "
            "external address, or delivery can fail even though the call returns success. For a "
            "draft reply pass inReplyTo (the Message-ID header, not the numeric messageId, from "
            "get_email_headers or get_original_message), and refHeader as well when the reply is "
            "part of an existing thread. To send immediately instead, use send_email. Returns the "
            "saved draft's messageId and mailId."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def save_draft(
        accountId: str = Field(description="Identifies the account to save the draft under. Obtained from list_accounts."),
        fromAddress: str = Field(description="Sender's email address, associated with the authenticated account. Use the account's mailboxAddress, not an external address."),
        toAddress: str = Field(description="Recipient's email address."),
        mode: str = Field(description="Whether the content is saved as a draft or a template. One of draft, template."),
        ccAddress: str | None = Field(default=None, description="Recipient's email address for the Cc field."),
        bccAddress: str | None = Field(default=None, description="Recipient's email address for the Bcc field."),
        subject: str | None = Field(default=None, description="Subject of the email."),
        content: str | None = Field(default=None, description="Content of the email."),
        mailFormat: str | None = Field(default=None, description="Format of the mail. One of html, plaintext. Defaults to html."),
        askReceipt: str | None = Field(default=None, description="Whether a read receipt is requested from the recipient. One of yes, no."),
        encoding: str | None = Field(default=None, description="Encoding used in the email content, e.g. UTF-8, ISO-8859-1, Shift_JIS. Defaults to UTF-8."),
        inReplyTo: str | None = Field(default=None, description="The Message-ID header of the email being replied to (not the numeric messageId). Required when this draft is a reply. Obtained from get_email_headers or get_original_message."),
        refHeader: str | None = Field(default=None, description="The Message-IDs of all previous emails in the thread, space-separated in chronological order. Required in addition to inReplyTo when the reply is part of an existing thread."),
    ) -> SaveDraftResult:
        tlog = ToolLogger(logger, "save_draft")

        if not accountId:
            return _err(SaveDraftResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not fromAddress:
            return _err(SaveDraftResult, tlog, "VALIDATION_ERROR", "fromAddress is required", 400)
        if not toAddress:
            return _err(SaveDraftResult, tlog, "VALIDATION_ERROR", "toAddress is required", 400)
        if mode not in ("draft", "template"):
            return _err(SaveDraftResult, tlog, "VALIDATION_ERROR", "mode must be draft or template", 400)

        body = {
            "fromAddress": fromAddress,
            "toAddress": toAddress,
            "mode": mode,
        }
        for key, value in {
            "ccAddress": ccAddress, "bccAddress": bccAddress, "subject": subject,
            "content": content, "mailFormat": mailFormat, "askReceipt": askReceipt,
            "encoding": encoding, "inReplyTo": inReplyTo, "refHeader": refHeader,
        }.items():
            if value is not None:
                body[key] = value

        try:
            data, status, retry_after = service.api_request(
                "POST", f"/accounts/{accountId}/messages", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return SaveDraftResult(success=True, statusCode=status, data=SaveDraftData(**data.get("data", {})))
            return _upstream_err(SaveDraftResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(SaveDraftResult, tlog, exc)

    @mcp.tool(
        name="search_emails",
        description=(
            "Searches emails using a searchKey built with Zoho Mail search syntax (for example "
            "entire:<text>, sender:<address>, subject:<text>, in:<folder>) and returns matching "
            "messages with start/limit paging. By default only emails received more than 2 minutes "
            "ago are returned, unless receivedTime (a Unix timestamp in milliseconds) is given. "
            "limit accepts 1-200 (default 10); start is the 1-based sequence number to page from "
            "(default 1). To browse a folder or filter by status, flag or label without a search "
            "query, use list_emails instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_emails(
        accountId: str = Field(description="Identifies the account to search. Obtained from list_accounts."),
        searchKey: str = Field(description="Search criteria, built using the Zoho Mail search syntax, e.g. 'sender:someone@example.com'."),
        receivedTime: str | None = Field(default=None, description="Unix timestamp in milliseconds; only emails received before this time are returned. Defaults to 2 minutes before the current time."),
        start: int | None = Field(default=None, description="1-based starting sequence number of the emails to retrieve. Defaults to 1."),
        limit: int | None = Field(default=None, description="Number of emails to retrieve from start. Range 1-200, defaults to 10."),
        includeto: bool | None = Field(default=None, description="Whether to include the To address details. Defaults to false."),
    ) -> SearchEmailsResult:
        tlog = ToolLogger(logger, "search_emails")

        if not accountId:
            return _err(SearchEmailsResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not searchKey:
            return _err(SearchEmailsResult, tlog, "VALIDATION_ERROR", "searchKey is required", 400)
        if limit is not None and not (1 <= limit <= 200):
            return _err(SearchEmailsResult, tlog, "VALIDATION_ERROR", "limit must be between 1 and 200", 400)

        params = {"searchKey": searchKey}
        for key, value in {
            "receivedTime": receivedTime, "start": start, "limit": limit, "includeto": includeto,
        }.items():
            if value is not None:
                params[key] = value

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/accounts/{accountId}/messages/search", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                items = data.get("data", [])
                return SearchEmailsResult(
                    success=True, statusCode=status,
                    data=[SearchEmailsData(**item) for item in items],
                )
            return _upstream_err(SearchEmailsResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(SearchEmailsResult, tlog, exc)

    @mcp.tool(
        name="send_email",
        description=(
            "Sends an email immediately from the given account, or schedules it for later when "
            "isSchedule is true. fromAddress must be the account's Zoho mailbox address "
            "(mailboxAddress from list_accounts), not an external address, or delivery can fail "
            "even though the call returns success. scheduleType 6 requires both timeZone and "
            "scheduleTime; other scheduleType values need neither. Returns the sent email's "
            "messageId and mailId. To save an email without sending it, use save_draft instead; to "
            "reply to an existing message, use reply_to_email instead."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def send_email(
        accountId: str = Field(description="Identifies the account to send the email from. Obtained from list_accounts."),
        fromAddress: str = Field(description="Sender's email address, associated with the authenticated account. Use the account's mailboxAddress, not an external address."),
        toAddress: str = Field(description="Recipient's email address."),
        ccAddress: str | None = Field(default=None, description="Recipient's email address for the Cc field."),
        bccAddress: str | None = Field(default=None, description="Recipient's email address for the Bcc field."),
        subject: str | None = Field(default=None, description="Subject of the email."),
        content: str | None = Field(default=None, description="Content of the email."),
        mailFormat: str | None = Field(default=None, description="Format of the mail. One of html, plaintext. Defaults to html."),
        askReceipt: str | None = Field(default=None, description="Whether a read receipt is requested from the recipient. One of yes, no."),
        encoding: str | None = Field(default=None, description="Encoding used in the email content, e.g. UTF-8, ISO-8859-1, Shift_JIS. Defaults to UTF-8."),
        isSchedule: bool | None = Field(default=None, description="Whether the email should be scheduled instead of sent immediately."),
        scheduleType: int | None = Field(default=None, description="Type of scheduling: 1 after one hour, 2 after two hours, 3 after four hours, 4 by next morning, 5 by next afternoon, 6 a custom date/time."),
        timeZone: str | None = Field(default=None, description="Timezone to schedule the email in. Required when scheduleType is 6."),
        scheduleTime: str | None = Field(default=None, description="Date and time to schedule the email, format MM/DD/YYYY HH:MM:SS. Required when scheduleType is 6."),
    ) -> SendEmailResult:
        tlog = ToolLogger(logger, "send_email")

        if not accountId:
            return _err(SendEmailResult, tlog, "VALIDATION_ERROR", "accountId is required", 400)
        if not fromAddress:
            return _err(SendEmailResult, tlog, "VALIDATION_ERROR", "fromAddress is required", 400)
        if not toAddress:
            return _err(SendEmailResult, tlog, "VALIDATION_ERROR", "toAddress is required", 400)
        if scheduleType == 6 and (not timeZone or not scheduleTime):
            return _err(SendEmailResult, tlog, "VALIDATION_ERROR", "timeZone and scheduleTime are required when scheduleType is 6", 400)

        body = {
            "fromAddress": fromAddress,
            "toAddress": toAddress,
        }
        for key, value in {
            "ccAddress": ccAddress, "bccAddress": bccAddress, "subject": subject,
            "content": content, "mailFormat": mailFormat, "askReceipt": askReceipt,
            "encoding": encoding, "isSchedule": isSchedule, "scheduleType": scheduleType,
            "timeZone": timeZone, "scheduleTime": scheduleTime,
        }.items():
            if value is not None:
                body[key] = value

        try:
            data, status, retry_after = service.api_request(
                "POST", f"/accounts/{accountId}/messages", body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return SendEmailResult(success=True, statusCode=status, data=SendEmailData(**data.get("data", {})))
            return _upstream_err(SendEmailResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(SendEmailResult, tlog, exc)
