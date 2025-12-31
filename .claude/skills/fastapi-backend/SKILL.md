---
name: fastapi-backend
description: Use when building or modifying Python FastAPI backends for web applications. Covers REST API endpoints, Pydantic models, SQLModel integration, JWT authentication middleware, and async database operations.
---

# FastAPI Backend

## Overview

This skill provides guidance for building Python FastAPI backends with SQLModel ORM, JWT authentication, and RESTful API design. Use when creating API endpoints, database models, authentication middleware, or modifying the todo app backend.

## Quick Start

```python
# main.py - FastAPI app entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Todo API",
    description="REST API for todo task management",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD endpoints
│   │   └── auth.py          # Authentication endpoints
│   ├── db.py                # Database connection
│   └── auth.py              # JWT utilities
├── requirements.txt
└── .env
```

## SQLModel Database Models

```python
# models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """User model for authentication"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: list["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task model for todo items"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=1000, default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="tasks")
```

## Pydantic Schemas

```python
# schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: str
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: Optional[str]
    created_at: datetime
```

## REST API Endpoints

```python
# routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from auth import get_current_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tasks for a user"""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tasks = await db.execute(
        select(Task).where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return tasks.scalars().all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = Task(user_id=user_id, **task_data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task"""
    task = await db.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    task = await db.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    task = await db.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle task completion status"""
    task = await db.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    await db.commit()
    await db.refresh(task)
    return task
```

## Database Connection

```python
# db.py
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/todo")

# Async engine for FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Resources

### references/

- `fastapi-docs.md` - FastAPI official documentation reference
- `sqlmodel-guide.md` - SQLModel ORM guide

### scripts/

- `init-db.sh` - Initialize database tables
- `seed-data.py` - Seed test data
