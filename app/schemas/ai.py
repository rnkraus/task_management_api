from pydantic import BaseModel


class TaskImproveRequest(BaseModel):
    title: str
    description: str | None = None


class TaskImproveResponse(BaseModel):
    suggested_title: str
    suggested_description: str | None = None


class GroupedTaskItem(BaseModel):
    id: int
    title: str


class TaskGroup(BaseModel):
    group_name: str
    tasks: list[GroupedTaskItem]


class GroupTasksResponse(BaseModel):
    groups: list[TaskGroup]


class PlannedTaskStep(BaseModel):
    id: int
    title: str
    reason: str


class TaskPlanResponse(BaseModel):
    steps: list[PlannedTaskStep]