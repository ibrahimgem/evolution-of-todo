import pytest
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db
from src.models import User, Task
from src.auth import get_current_user
from unittest.mock import AsyncMock

# Create an in-memory SQLite database for testing
@pytest.fixture(name="db_engine")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine

@pytest.fixture(name="test_app")
def test_app(db_engine):
    with TestClient(app) as test_client:
        # Override the database dependency
        def get_test_db():
            yield db_engine
        app.dependency_overrides[get_db] = get_test_db
        yield test_client