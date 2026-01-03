"""Pytest configuration and fixtures for Phase III AI Chatbot tests."""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

# Import models to ensure they're registered with SQLModel
from src.models import User, Task, Conversation, Message
from src.database import get_db
from src.auth import hash_password, create_access_token


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async test backend."""
    return "asyncio"


@pytest_asyncio.fixture
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("testpassword123"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create authentication token for test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return token


@pytest_asyncio.fixture
async def auth_headers(test_user_token: str) -> dict:
    """Create authentication headers with Bearer token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def test_task(async_session: AsyncSession, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_conversation(async_session: AsyncSession, test_user: User) -> Conversation:
    """Create a test conversation."""
    conversation = Conversation(
        user_id=test_user.id,
        title="Test Conversation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        meta={}
    )
    async_session.add(conversation)
    await async_session.commit()
    await async_session.refresh(conversation)
    return conversation


@pytest_asyncio.fixture
async def test_message(
    async_session: AsyncSession,
    test_conversation: Conversation
) -> Message:
    """Create a test message."""
    message = Message(
        conversation_id=test_conversation.id,
        role="user",
        content="Test message",
        tool_calls=None,
        created_at=datetime.now(timezone.utc)
    )
    async_session.add(message)
    await async_session.commit()
    await async_session.refresh(message)
    return message


@pytest_asyncio.fixture
async def async_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing."""
    from src.main import app

    # Override database dependency
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    # Create async client with proper transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "message": "Add a task to buy groceries tomorrow"
    }


@pytest.fixture
def sample_tool_result():
    """Sample tool execution result."""
    return {
        "success": True,
        "task": {
            "id": 1,
            "title": "Buy groceries",
            "description": None,
            "due_date": "2026-01-02T00:00:00Z",
            "completed": False,
            "created_at": "2026-01-01T10:00:00Z"
        }
    }


@pytest.fixture
def mock_agent_response():
    """Mock agent response for testing without OpenAI API."""
    return {
        "response": "I've added 'Buy groceries' to your tasks for tomorrow.",
        "tool_calls": [
            {
                "tool_name": "add_task",
                "result": {
                    "success": True,
                    "task": {
                        "id": 1,
                        "title": "Buy groceries",
                        "due_date": "2026-01-02T00:00:00Z"
                    }
                }
            }
        ],
        "error": None
    }


@pytest.fixture
def mcp_context(test_user: User):
    """MCP tool execution context."""
    return {
        "user_id": test_user.id,
        "request_id": f"{test_user.id}_test",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Markers for test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (database, API endpoints)"
    )
    config.addinivalue_line(
        "markers", "contract: Contract tests (MCP tool schemas)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full user flows)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (external API calls)"
    )
