# SQLModel Database Integration

## Async Session Management

Always use async sessions for non-blocking database operations.

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def get_db():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
```

## Modeling Relationships

Define one-to-many and many-to-many relationships using `Relationship`.

```python
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="owner")

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="items")
```

## Efficient Querying

Use `select` statement with async execution.

```python
from sqlmodel import select

async def get_user_items(session: AsyncSession, user_id: int):
    statement = select(Item).where(Item.owner_id == user_id)
    results = await session.exec(statement)
    return results.all()
```
