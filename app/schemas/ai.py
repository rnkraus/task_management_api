from pydantic import BaseModel


class TaskImproveRequest(BaseModel):
    title: str
    description: str | None = None


class TaskImproveResponse(BaseModel):
    suggested_title: str
    suggested_description: str | None = None