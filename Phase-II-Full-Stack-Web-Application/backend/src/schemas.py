from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone


# User schemas
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    access_token: str
    token_type: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None
