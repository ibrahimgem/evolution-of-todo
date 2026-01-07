import pytest
from datetime import datetime, timezone, timedelta
from src.mcp_tools.complete_task import complete_task, CompleteTaskInput
from src.mcp_tools.delete_task import delete_task, DeleteTaskInput
from src.mcp_tools.update_task import update_task, UpdateTaskInput
from src.models import Task, User
from src.auth import hash_password
from sqlmodel import select

@pytest.mark.asyncio
@pytest.mark.unit
class TestCompleteTaskTool:
    async def test_complete_task_success(self, async_session, test_user, test_task, mcp_context):
        """Test successfully marking a task as complete."""
        input_data = CompleteTaskInput(task_id=test_task.id, completed=True)
        result = await complete_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["id"] == test_task.id
        assert result.task["completed"] is True

        # Verify in database
        statement = select(Task).where(Task.id == test_task.id)
        db_result = await async_session.execute(statement)
        updated_task = db_result.scalar_one()
        assert updated_task.completed is True

    async def test_complete_task_not_found(self, async_session, test_user, mcp_context):
        """Test error when task does not exist."""
        input_data = CompleteTaskInput(task_id=999, completed=True)
        result = await complete_task(input_data, async_session, mcp_context)

        assert result.success is False
        assert "not found" in result.error

    async def test_complete_task_wrong_user(self, async_session, test_user, mcp_context):
        """Test error when task belongs to another user."""
        # Create another user and their task
        other_user = User(
            email="other@example.com",
            hashed_password=hash_password("password"),
            created_at=datetime.now(timezone.utc)
        )
        async_session.add(other_user)
        await async_session.commit()
        await async_session.refresh(other_user)

        other_task = Task(
            user_id=other_user.id,
            title="Other Task",
            created_at=datetime.now(timezone.utc)
        )
        async_session.add(other_task)
        await async_session.commit()
        await async_session.refresh(other_task)

        # Try to complete other user's task using first user's context
        input_data = CompleteTaskInput(task_id=other_task.id, completed=True)
        result = await complete_task(input_data, async_session, mcp_context)

        assert result.success is False
        assert "access denied" in result.error.lower()

@pytest.mark.asyncio
@pytest.mark.unit
class TestDeleteTaskTool:
    async def test_delete_task_success(self, async_session, test_user, test_task, mcp_context):
        """Test successfully deleting a task."""
        input_data = DeleteTaskInput(task_id=test_task.id)
        result = await delete_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.deleted_task_id == test_task.id

        # Verify in database
        statement = select(Task).where(Task.id == test_task.id)
        db_result = await async_session.execute(statement)
        deleted_task = db_result.scalar_one_or_none()
        assert deleted_task is None

    async def test_delete_task_wrong_user(self, async_session, test_user, mcp_context):
        """Test error when deleting another user's task."""
        other_user = User(
            email="other_del@example.com",
            hashed_password=hash_password("password"),
            created_at=datetime.now(timezone.utc)
        )
        async_session.add(other_user)
        await async_session.commit()
        await async_session.refresh(other_user)

        other_task = Task(
            user_id=other_user.id,
            title="Other Task",
            created_at=datetime.now(timezone.utc)
        )
        async_session.add(other_task)
        await async_session.commit()
        await async_session.refresh(other_task)

        input_data = DeleteTaskInput(task_id=other_task.id)
        result = await delete_task(input_data, async_session, mcp_context)

        assert result.success is False
        assert "access denied" in result.error.lower()

@pytest.mark.asyncio
@pytest.mark.unit
class TestUpdateTaskTool:
    async def test_update_task_success(self, async_session, test_user, test_task, mcp_context):
        """Test successfully updating task fields."""
        new_title = "Updated Title"
        new_due = datetime.now(timezone.utc) + timedelta(days=1)

        input_data = UpdateTaskInput(
            task_id=test_task.id,
            title=new_title,
            due_date=new_due
        )
        result = await update_task(input_data, async_session, mcp_context)

        assert result.success is True
        assert result.task["title"] == new_title

        # Verify in database
        statement = select(Task).where(Task.id == test_task.id)
        db_result = await async_session.execute(statement)
        updated_task = db_result.scalar_one()
        assert updated_task.title == new_title

    async def test_update_task_no_fields(self, async_session, test_user, test_task, mcp_context):
        """Test error when no update fields are provided."""
        input_data = UpdateTaskInput(task_id=test_task.id)
        result = await update_task(input_data, async_session, mcp_context)

        assert result.success is False
        assert "At least one field" in result.error

    async def test_update_task_past_due_date(self, async_session, test_user, test_task, mcp_context):
        """Test validation error for past due date."""
        past_due = datetime.now(timezone.utc) - timedelta(days=1)

        try:
            UpdateTaskInput(task_id=test_task.id, due_date=past_due)
        except ValueError as e:
            assert "future" in str(e).lower()
