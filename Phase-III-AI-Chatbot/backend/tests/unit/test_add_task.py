"""
Unit tests for add_task MCP tool.

Tests the business logic of the add_task tool in isolation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch


@pytest.mark.unit
@pytest.mark.asyncio
class TestAddTaskUnit:
    """Unit tests for add_task tool logic."""

    async def test_add_task_creates_task_with_title_only(
        self, async_session, test_user, mcp_context
    ):
        """Test creating a task with only title (minimal input)."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="Buy groceries")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task is not None
        assert result.task["title"] == "Buy groceries"
        assert result.task["description"] is None
        assert result.task["due_date"] is None
        assert result.task["completed"] is False
        assert result.task["id"] is not None
        assert result.error is None

    async def test_add_task_creates_task_with_all_fields(
        self, async_session, test_user, mcp_context
    ):
        """Test creating a task with all optional fields provided."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        input_data = AddTaskInput(
            title="Buy groceries",
            description="Milk, eggs, bread",
            due_date=future_date
        )

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task is not None
        assert result.task["title"] == "Buy groceries"
        assert result.task["description"] == "Milk, eggs, bread"
        assert result.task["due_date"] is not None
        assert result.task["completed"] is False
        assert result.task["user_id"] == test_user.id

    async def test_add_task_rejects_past_due_date(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task rejects due dates in the past."""
        from src.mcp_tools.add_task import AddTaskInput
        from pydantic import ValidationError

        past_date = datetime.now(timezone.utc) - timedelta(days=1)

        # Should raise validation error during input creation
        with pytest.raises(ValidationError) as exc_info:
            input_data = AddTaskInput(
                title="Buy groceries",
                due_date=past_date
            )

        errors = exc_info.value.errors()
        assert any('due_date' in str(error['loc']) for error in errors)
        assert any('future' in str(error['msg']).lower() for error in errors)

    async def test_add_task_accepts_future_due_date(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task accepts future due dates."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        future_date = datetime.now(timezone.utc) + timedelta(hours=1)

        input_data = AddTaskInput(
            title="Buy groceries",
            due_date=future_date
        )

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task is not None

    async def test_add_task_scopes_to_authenticated_user(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task creates task for authenticated user only."""
        from src.mcp_tools.add_task import add_task, AddTaskInput
        from src.models import Task
        from sqlmodel import select

        input_data = AddTaskInput(title="User-specific task")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True

        # Verify task is scoped to the user from context
        task_id = result.task["id"]
        stmt = select(Task).where(Task.id == task_id)
        db_result = await async_session.execute(stmt)
        task = db_result.scalar_one_or_none()

        assert task is not None
        assert task.user_id == test_user.id

    async def test_add_task_persists_to_database(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task persists task to database."""
        from src.mcp_tools.add_task import add_task, AddTaskInput
        from src.models import Task
        from sqlmodel import select

        input_data = AddTaskInput(
            title="Database persistence test",
            description="Test description"
        )

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        task_id = result.task["id"]

        # Verify task exists in database
        stmt = select(Task).where(Task.id == task_id)
        db_result = await async_session.execute(stmt)
        task = db_result.scalar_one_or_none()

        assert task is not None
        assert task.title == "Database persistence test"
        assert task.description == "Test description"

    async def test_add_task_returns_proper_timestamps(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task returns created_at timestamp."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="Timestamp test")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["created_at"] is not None

        # Verify created_at is recent (within last minute)
        created_at_str = result.task["created_at"]
        # ISO format parsing
        if isinstance(created_at_str, str):
            # Parse ISO format and ensure timezone-aware
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at_str
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        time_diff = (now - created_at).total_seconds()
        assert time_diff < 60  # Created within last minute

    async def test_add_task_handles_empty_description(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task handles None description gracefully."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="No description task")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["description"] is None

    async def test_add_task_handles_database_error(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task handles database errors gracefully."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="Error handling test")

        # Simulate database error
        with patch.object(async_session, 'commit', side_effect=Exception("DB error")):
            result = await add_task(input_data, async_session, mcp_context)

            assert result.success is False
            assert result.error is not None
            assert result.task is None

    async def test_add_task_strips_whitespace_from_title(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task strips leading/trailing whitespace from title."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="  Buy groceries  ")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["title"] == "Buy groceries"

    async def test_add_task_sets_completed_false_by_default(
        self, async_session, test_user, mcp_context
    ):
        """Test add_task sets completed to False for new tasks."""
        from src.mcp_tools.add_task import add_task, AddTaskInput

        input_data = AddTaskInput(title="New task")

        result = await add_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["completed"] is False

    async def test_add_task_logs_execution(
        self, async_session, test_user, mcp_context, caplog
    ):
        """Test add_task logs tool execution for audit trail."""
        from src.mcp_tools.add_task import add_task, AddTaskInput
        import logging

        caplog.set_level(logging.INFO)

        input_data = AddTaskInput(title="Log test task")

        await add_task(input_data, async_session, mcp_context)

        # Check that logging occurred
        log_records = [record for record in caplog.records if record.name.startswith('src.mcp_tools')]
        assert len(log_records) > 0
