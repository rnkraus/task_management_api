from typing import Optional
from pydantic import BaseModel, field_validator, model_validator, ConfigDict


class TaskCreate(BaseModel):
    title: str
    completed: bool = False
    description: Optional[str] = None
    user_id: int

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value


class TaskPut(BaseModel):
    title: str
    completed: bool
    description: Optional[str] = None
    user_id: int

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    description: Optional[str] = None
    user_id: int

    @field_validator("title")
    def title_must_not_be_empty(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self):
        if (
            self.title is None 
            and self.completed is None 
            and self.description is None
            and self.user_id is None
        ):
            raise ValueError("At least one field must be provided")
        return self


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    completed: bool
    description: Optional[str] = None
    user_id: int