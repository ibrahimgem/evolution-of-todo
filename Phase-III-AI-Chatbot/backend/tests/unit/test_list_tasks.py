"""
Unit tests for list_tasks MCP tool.

Tests the business logic of the list_tasks tool in isolation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from src.models import Task


@pytest.mark.unit
@pytest.mark.asyncio
class TestListTasksUnit:
    """Unit tests for list_tasks tool logic."""

    async def test_list_tasks_returns_empty_list_when_no_tasks(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks returns empty list when user has no tasks."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.tasks == []
        assert result.total == 0
        assert result.offset == 0
        assert result.limit == 50
        assert result.error is None

    async def test_list_tasks_returns_all_user_tasks(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks returns all tasks for the authenticated user."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create multiple tasks for the user
        tasks_data = [
            Task(
                user_id=test_user.id,
                title=f"Task {i}",
                description=f"Description {i}",
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 4)
        ]

        for task in tasks_data:
            async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 3
        assert result.total == 3
        assert result.error is None

    async def test_list_tasks_filters_by_status_complete(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks filters by status='complete'."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create completed and incomplete tasks
        completed_task = Task(
            user_id=test_user.id,
            title="Completed Task",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task = Task(
            user_id=test_user.id,
            title="Incomplete Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(completed_task)
        async_session.add(incomplete_task)
        await async_session.commit()

        input_data = ListTasksInput(status="complete")

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1
        assert result.tasks[0]["title"] == "Completed Task"
        assert result.tasks[0]["completed"] is True
        assert result.total == 1

    async def test_list_tasks_filters_by_status_incomplete(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks filters by status='incomplete'."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create completed and incomplete tasks
        completed_task = Task(
            user_id=test_user.id,
            title="Completed Task",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task = Task(
            user_id=test_user.id,
            title="Incomplete Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(completed_task)
        async_session.add(incomplete_task)
        await async_session.commit()

        input_data = ListTasksInput(status="incomplete")

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1
        assert result.tasks[0]["title"] == "Incomplete Task"
        assert result.tasks[0]["completed"] is False
        assert result.total == 1

    async def test_list_tasks_filters_by_status_all(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks filters by status='all'."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create completed and incomplete tasks
        completed_task = Task(
            user_id=test_user.id,
            title="Completed Task",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task = Task(
            user_id=test_user.id,
            title="Incomplete Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(completed_task)
        async_session.add(incomplete_task)
        await async_session.commit()

        input_data = ListTasksInput(status="all")

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 2
        assert result.total == 2

    async def test_list_tasks_respects_limit(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks respects limit parameter."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create 10 tasks
        tasks_data = [
            Task(
                user_id=test_user.id,
                title=f"Task {i}",
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 11)
        ]

        for task in tasks_data:
            async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput(limit=5)

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 5  # Limited to 5
        assert result.total == 10  # But total count is still 10
        assert result.limit == 5

    async def test_list_tasks_respects_offset(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks respects offset parameter for pagination."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create 10 tasks with distinct titles
        tasks_data = [
            Task(
                user_id=test_user.id,
                title=f"Task {i:02d}",  # Zero-padded for sorting
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 11)
        ]

        for task in tasks_data:
            async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput(offset=5, limit=5)

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 5  # Second page of 5
        assert result.total == 10  # Total count
        assert result.offset == 5

    async def test_list_tasks_pagination_combination(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks with both offset and limit for pagination."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create 25 tasks
        tasks_data = [
            Task(
                user_id=test_user.id,
                title=f"Task {i}",
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 26)
        ]

        for task in tasks_data:
            async_session.add(task)
        await async_session.commit()

        # Get second page (10-19)
        input_data = ListTasksInput(offset=10, limit=10)

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 10
        assert result.total == 25
        assert result.offset == 10
        assert result.limit == 10

    async def test_list_tasks_scopes_to_authenticated_user(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks only returns tasks for authenticated user."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput
        from src.models import User
        from src.auth import hash_password

        # Create another user with tasks
        other_user = User(
            email="other@example.com",
            name="Other User",
            hashed_password=hash_password("password123"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(other_user)
        await async_session.commit()
        await async_session.refresh(other_user)

        # Create tasks for both users
        test_user_task = Task(
            user_id=test_user.id,
            title="Test User Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        other_user_task = Task(
            user_id=other_user.id,
            title="Other User Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(test_user_task)
        async_session.add(other_user_task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1
        assert result.tasks[0]["title"] == "Test User Task"
        assert result.total == 1

    async def test_list_tasks_includes_all_required_fields(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks includes all required task fields."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        task = Task(
            user_id=test_user.id,
            title="Complete Task",
            description="Task description",
            completed=False,
            due_date=future_date,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1

        task_dict = result.tasks[0]
        assert "id" in task_dict
        assert "title" in task_dict
        assert "description" in task_dict
        assert "completed" in task_dict
        assert "due_date" in task_dict
        assert "created_at" in task_dict
        assert "updated_at" in task_dict

    async def test_list_tasks_handles_nullable_fields(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks handles nullable fields (description, due_date)."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        task = Task(
            user_id=test_user.id,
            title="Minimal Task",
            description=None,
            completed=False,
            due_date=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1
        assert result.tasks[0]["description"] is None
        assert result.tasks[0]["due_date"] is None

    async def test_list_tasks_orders_by_created_at_desc(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks returns tasks ordered by created_at DESC (newest first)."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        # Create tasks with different timestamps
        old_task = Task(
            user_id=test_user.id,
            title="Old Task",
            completed=False,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        recent_task = Task(
            user_id=test_user.id,
            title="Recent Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(old_task)
        async_session.add(recent_task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 2
        # Newest task should be first
        assert result.tasks[0]["title"] == "Recent Task"
        assert result.tasks[1]["title"] == "Old Task"

    async def test_list_tasks_handles_database_error(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks handles database errors gracefully."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        input_data = ListTasksInput()

        # Simulate database error
        with patch.object(async_session, 'execute', side_effect=Exception("DB error")):
            result = await list_tasks(input_data, async_session, mcp_context)

            assert result.success is False
            assert result.error is not None
            assert "Failed to list tasks" in result.error or "DB error" in result.error

    async def test_list_tasks_handles_missing_user_id(
        self, async_session, mcp_context
    ):
        """Test list_tasks handles missing user_id in context."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        input_data = ListTasksInput()

        # Remove user_id from context
        invalid_context = {
            "request_id": "test_req",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        result = await list_tasks(input_data, async_session, invalid_context)

        assert result.success is False
        assert result.error is not None
        assert "user_id" in result.error.lower() or "authentication" in result.error.lower()

    async def test_list_tasks_logs_execution(
        self, async_session, test_user, mcp_context, caplog
    ):
        """Test list_tasks logs tool execution for audit trail."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput
        import logging

        caplog.set_level(logging.INFO)

        input_data = ListTasksInput()

        await list_tasks(input_data, async_session, mcp_context)

        # Check that logging occurred
        log_records = [record for record in caplog.records if record.name.startswith('src.mcp_tools')]
        assert len(log_records) > 0

    async def test_list_tasks_default_limit_50(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks uses default limit of 50."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.limit == 50

    async def test_list_tasks_returns_iso_datetime_strings(
        self, async_session, test_user, mcp_context
    ):
        """Test list_tasks returns datetime fields as ISO format strings."""
        from src.mcp_tools.list_tasks import list_tasks, ListTasksInput

        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        task = Task(
            user_id=test_user.id,
            title="Datetime Test Task",
            completed=False,
            due_date=future_date,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async_session.add(task)
        await async_session.commit()

        input_data = ListTasksInput()

        result = await list_tasks(input_data, async_session, mcp_context)

        assert result.success is True
        assert len(result.tasks) == 1

        task_dict = result.tasks[0]
        # Verify datetime fields are strings in ISO format
        assert isinstance(task_dict["created_at"], str)
        assert isinstance(task_dict["updated_at"], str)
        if task_dict["due_date"]:
            assert isinstance(task_dict["due_date"], str)
