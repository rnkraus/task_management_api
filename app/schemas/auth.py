from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    email: str
    name: str
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"