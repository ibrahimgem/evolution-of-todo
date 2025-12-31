---
name: sqlmodel-db
description: Use when defining database schemas, models, or performing database operations. Covers SQLModel ORM patterns, async sessions, PostgreSQL integration, and migrations for Python FastAPI applications.
---

# SQLModel Database

## Overview

SQLModel is a Python ORM built on top of SQLAlchemy and Pydantic. Use for database models, schema definitions, and async database operations in FastAPI applications.

## Quick Start

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=1000, default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="tasks")
```

## Database Connection

```python
# db.py
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/todo")

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from sqlmodel import SQLModel
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Common Operations

### Create

```python
async def create_task(db: AsyncSession, user_id: int, title: str, description: str = None):
    task = Task(user_id=user_id, title=title, description=description)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

### Read

```python
from sqlalchemy import select

async def get_user_tasks(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()

async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

### Update

```python
async def update_task(db: AsyncSession, task: Task, **kwargs):
    for field, value in kwargs.items():
        if value is not None:
            setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task
```

### Delete

```python
async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()
```

## Relationships

```python
# Eager loading for related objects
async def get_user_with_tasks(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        # Load tasks relationship
        await db.refresh(user, attribute_names=["tasks"])
    return user
```

## Indexes and Constraints

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200, index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    # Composite index for common queries
    __table_args__ = (
        {"postgresql_indexes": [
            Index("idx_user_completed", "user_id", "completed")
        ]},
    )
```

## Migrations

Use Alembic for schema migrations:

```bash
# Generate migration
alembic revision -m "add_user_tasks"

# Apply migrations
alembic upgrade head
```

## Best Practices

- Use async/await for all database operations in FastAPI
- Always use `expire_on_commit=False` in sessionmaker for better performance
- Index foreign keys and frequently filtered columns
- Use `select()` instead of legacy query API
- Validate input with Pydantic before database operations
