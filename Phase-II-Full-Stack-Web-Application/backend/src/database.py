from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from typing import AsyncGenerator

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./todos.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for debugging
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration for production
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600
    )

# Create async session factory
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_db_and_tables():
    """
    Create database tables on startup
    """
    try:
        async with async_engine.begin() as conn:
            # Use run_sync to create tables synchronously
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

async def close_db():
    """
    Close database connection on shutdown
    """
    await async_engine.dispose()
