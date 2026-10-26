from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class ApplyLabelsToEmailsData(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApplyLabelsToEmailsResult(ToolResult):
    data: ApplyLabelsToEmailsData | None = None


class DeleteEmailData(BaseModel):
    model_config = ConfigDict(extra="allow")

    cId: str | int | None = None


class DeleteEmailResult(ToolResult):
    data: DeleteEmailData | None = None


class GetEmailContentData(BaseModel):
    model_config = ConfigDict(extra="allow")

    messageId: str | int | None = None
    content: str | None = None
    blockContent: str | None = None


class GetEmailContentResult(ToolResult):
    data: GetEmailContentData | None = None


class ListEmailsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    summary: str | None = None
    sentDateInGMT: str | None = None
    calendarType: int | None = None
    subject: str | None = None
    messageId: str | None = None
    threadCount: str | None = None
    flagid: str | None = None
    status2: str | None = None
    priority: str | None = None
    hasInline: str | None = None
    toAddress: str | None = None
    folderId: str | None = None
    ccAddress: str | None = None
    threadId: str | None = None
    hasAttachment: str | None = None
    size: str | None = None
    sender: str | None = None
    receivedTime: str | None = None
    fromAddress: str | None = None
    status: str | None = None


class ListEmailsResult(ToolResult):
    data: list[ListEmailsData] | None = None


class MarkEmailAsReadData(BaseModel):
    model_config = ConfigDict(extra="allow")


class MarkEmailAsReadResult(ToolResult):
    data: MarkEmailAsReadData | None = None


class MarkEmailAsUnreadData(BaseModel):
    model_config = ConfigDict(extra="allow")


class MarkEmailAsUnreadResult(ToolResult):
    data: MarkEmailAsUnreadData | None = None


class MoveEmailsData(BaseModel):
    model_config = ConfigDict(extra="allow")


class MoveEmailsResult(ToolResult):
    data: MoveEmailsData | None = None


class ReplyToEmailData(BaseModel):
    model_config = ConfigDict(extra="allow")

    subject: str | None = None
    action: str | None = None
    messageId: str | None = None
    fromAddress: str | None = None
    mailId: str | None = None
    toAddress: str | None = None
    content: str | None = None


class ReplyToEmailResult(ToolResult):
    data: ReplyToEmailData | None = None


class SaveDraftData(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: str | None = None
    subject: str | None = None
    messageId: str | None = None
    fromAddress: str | None = None
    mailId: str | None = None
    toAddress: str | None = None
    content: str | None = None


class SaveDraftResult(ToolResult):
    data: SaveDraftData | None = None


class SearchEmailsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    URI: str | None = None
    hasAttachment: str | None = None
    fromAddress: str | None = None
    folderId: str | None = None
    messageId: str | None = None
    sender: str | None = None
    summary: str | None = None
    status2: str | None = None
    sentDateInGMT: str | None = None
    size: str | None = None
    status: str | None = None
    priority: str | None = None
    threadCount: str | None = None
    flagid: str | None = None
    subject: str | None = None
    threadId: str | None = None
    receivedTime: str | None = None


class SearchEmailsResult(ToolResult):
    data: list[SearchEmailsData] | None = None


class SendEmailData(BaseModel):
    model_config = ConfigDict(extra="allow")

    subject: str | None = None
    messageId: str | None = None
    fromAddress: str | None = None
    mailId: str | None = None
    toAddress: str | None = None
    content: str | None = None


class SendEmailResult(ToolResult):
    data: SendEmailData | None = None
