from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str