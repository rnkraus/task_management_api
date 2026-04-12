from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator, ConfigDict


class UserCreate(BaseModel):
    email: str
    name: str

class UserPut(BaseModel):
    email: str
    name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.email is None and self.name is None:
            raise ValueError("At least one field must be provided")
        return self

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime