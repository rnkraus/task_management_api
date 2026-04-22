from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    title: str
    completed: bool = False
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 3

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value

    @field_validator("priority")
    def priority_must_be_valid(cls, value):
        if value not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3")
        return value


class TaskPut(BaseModel):
    title: str
    completed: bool
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 3

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value

    @field_validator("priority")
    def priority_must_be_valid(cls, value):
        if value not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value

    @field_validator("priority")
    def priority_must_be_valid(cls, value):
        if value is None:
            return value
        if value not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self):
        if (
            self.title is None
            and self.completed is None
            and self.description is None
            and self.due_date is None
            and self.priority is None
        ):
            raise ValueError("At least one field must be provided")
        return self


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskDetailResponse(TaskResponse):
    user: UserResponse