from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field, JSON, Column, TEXT

# Helper function to get timezone-naive UTC datetime
def get_utc_now():
    """Get timezone-naive UTC datetime for database compatibility"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

if TYPE_CHECKING:
    pass


# User model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, min_length=5, max_length=100)
    hashed_password: str = Field(min_length=8)
    name: str | None = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


# Priority enum values
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH]

# Category enum values
VALID_CATEGORIES = ["work", "personal", "shopping", "health", "finance", "education", "other"]


# Task model
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default=PRIORITY_MEDIUM, max_length=20)  # low, medium, high
    category: str | None = Field(default=None, max_length=50)  # work, personal, shopping, etc.
    due_date: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


# Conversation model (Phase III - AI Chatbot)
class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    title: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))


# Message model (Phase III - AI Chatbot)
class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int | None = Field(default=None, foreign_key="conversation.id")
    role: str = Field(max_length=20)  # 'user', 'assistant', 'system'
    content: str | None = Field(default=None, sa_column=Column(TEXT))
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=get_utc_now)


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
    priority: str = PRIORITY_MEDIUM  # low, medium, high
    category: str | None = None  # work, personal, shopping, health, finance, education, other
    due_date: datetime | None = None


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
    priority: str | None = None
    category: str | None = None
    due_date: datetime | None = None


# Pydantic models for Conversation
class ConversationBase(SQLModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    meta: dict


# Pydantic models for Message
class MessageBase(SQLModel):
    role: str
    content: str | None = None
    tool_calls: dict | None = None


class MessageCreate(MessageBase):
    conversation_id: int


class MessageRead(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
