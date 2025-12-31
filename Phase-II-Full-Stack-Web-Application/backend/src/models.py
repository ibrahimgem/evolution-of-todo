from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field

if TYPE_CHECKING:
    pass


# User model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, min_length=5, max_length=100)
    hashed_password: str = Field(min_length=8)
    name: str | None = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Task model
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Pydantic models for request/response validation
class UserBase(SQLModel):
    email: str
    name: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    email: str
    name: str | None = None
    created_at: datetime


class UserLogin(SQLModel):
    email: str
    password: str


class UserResponse(SQLModel):
    access_token: str
    token_type: str


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
