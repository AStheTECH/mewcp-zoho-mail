from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class FolderListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    folderId: str | None = None
    folderName: str | None = None
    path: str | None = None
    folderType: str | None = None
    imapAccess: bool | None = None
    isArchived: int | None = None
    URI: str | None = None
    previousFolderId: str | None = None


class FolderListResult(ToolResult):
    data: list[FolderListData] | None = None
