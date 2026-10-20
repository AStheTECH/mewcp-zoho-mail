from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class LabelStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: int | None = None
    description: str | None = None


class LabelData(BaseModel):
    model_config = ConfigDict(extra="allow")

    sequence: int | None = None
    labelId: str | None = None
    color: str | None = None
    tagId: str | None = None
    displayName: str | None = None
    URI: str | None = None


class LabelListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: LabelStatus | None = None
    data: list[LabelData] = []


class LabelListResult(ToolResult):
    data: LabelListData | None = None
