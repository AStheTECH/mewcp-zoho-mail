from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class EmailAddressEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    mailId: str | None = None
    isPrimary: bool | None = None
    isAlias: bool | None = None
    isConfirmed: bool | None = None


class SendMailDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    sendMailId: str | None = None
    displayName: str | None = None
    fromAddress: str | None = None
    serverName: str | None = None
    serverPort: int | None = None
    userName: str | None = None
    connectionType: str | None = None
    mode: str | None = None
    validated: bool | None = None
    status: bool | None = None


class MailForwardEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    mailForwardTo: str | None = None
    type: str | None = None
    status: str | None = None


class VacationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    vacationId: str | None = None
    accountId: str | None = None
    subject: str | None = None
    content: str | None = None
    fromDate: str | None = None
    toDate: str | None = None
    infiniteDate: bool | None = None
    replyType: int | None = None
    sendTo: int | None = None
    includeSignature: int | None = None
    markBusy: int | None = None
    intervalType: int | None = None
    interval: int | None = None
    accType: int | None = None
    name: str | None = None


class AccountEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    accountId: str | None = None
    accountDisplayName: str | None = None
    accountName: str | None = None
    displayName: str | None = None
    type: str | None = None
    enabled: bool | None = None
    mailboxStatus: str | None = None
    mailboxAddress: str | None = None
    incomingUserName: str | None = None
    primaryEmailAddress: str | None = None
    emailAddress: list[EmailAddressEntry] = []
    usedStorage: int | None = None
    allowedStorage: int | None = None
    planStorage: int | None = None
    basicStorage: str | None = None
    sendMailDetails: list[SendMailDetail] = []
    mailForward: list[MailForwardEntry] = []
    vacationResponse: list[VacationResponse] = []
    zuid: int | None = None
    URI: str | None = None


class AccountListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: list[AccountEntry] = []


class AccountListResult(ToolResult):
    data: AccountListData | None = None
