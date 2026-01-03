"""
Contract tests for add_task MCP tool.

Tests verify that add_task tool adheres to the MCP contract specification
defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError


@pytest.mark.contract
@pytest.mark.asyncio
class TestAddTaskContract:
    """Test add_task tool contract compliance."""

    async def test_add_task_input_schema_valid_minimal(self):
        """Test add_task accepts minimal valid input (title only)."""
        # This test verifies the tool accepts the minimum required input
        from src.mcp_tools.add_task import AddTaskInput

        input_data = AddTaskInput(title="Buy groceries")

        assert input_data.title == "Buy groceries"
        assert input_data.description is None
        assert input_data.due_date is None

    async def test_add_task_input_schema_valid_complete(self):
        """Test add_task accepts complete valid input."""
        from src.mcp_tools.add_task import AddTaskInput

        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        input_data = AddTaskInput(
            title="Buy groceries",
            description="Milk, eggs, bread",
            due_date=future_date
        )

        assert input_data.title == "Buy groceries"
        assert input_data.description == "Milk, eggs, bread"
        assert input_data.due_date == future_date

    async def test_add_task_input_schema_title_required(self):
        """Test add_task rejects input without title."""
        from src.mcp_tools.add_task import AddTaskInput

        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput()

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    async def test_add_task_input_schema_title_length_validation(self):
        """Test add_task validates title length (1-200 chars)."""
        from src.mcp_tools.add_task import AddTaskInput

        # Test empty title
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(title="")

        errors = exc_info.value.errors()
        assert any('title' in str(error['loc']) for error in errors)

        # Test title too long (>200 chars)
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(title="x" * 201)

        errors = exc_info.value.errors()
        assert any('title' in str(error['loc']) for error in errors)

        # Test valid edge cases
        AddTaskInput(title="x")  # 1 char - valid
        AddTaskInput(title="x" * 200)  # 200 chars - valid

    async def test_add_task_input_schema_description_length_validation(self):
        """Test add_task validates description length (max 1000 chars)."""
        from src.mcp_tools.add_task import AddTaskInput

        # Test description too long (>1000 chars)
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                title="Test",
                description="x" * 1001
            )

        errors = exc_info.value.errors()
        assert any('description' in str(error['loc']) for error in errors)

        # Test valid edge case
        AddTaskInput(title="Test", description="x" * 1000)  # 1000 chars - valid

    async def test_add_task_output_schema_success(self):
        """Test add_task output schema for success case."""
        from src.mcp_tools.add_task import AddTaskOutput

        output_data = AddTaskOutput(
            success=True,
            task={
                "id": 42,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "due_date": "2026-01-02T18:00:00Z",
                "completed": False,
                "created_at": "2026-01-01T10:30:00Z"
            }
        )

        assert output_data.success is True
        assert output_data.task is not None
        assert output_data.task["id"] == 42
        assert output_data.task["title"] == "Buy groceries"
        assert output_data.task["completed"] is False
        assert output_data.error is None

    async def test_add_task_output_schema_error(self):
        """Test add_task output schema for error case."""
        from src.mcp_tools.add_task import AddTaskOutput

        output_data = AddTaskOutput(
            success=False,
            error="Due date must be in the future"
        )

        assert output_data.success is False
        assert output_data.error == "Due date must be in the future"
        assert output_data.task is None

    async def test_add_task_output_schema_requires_success_field(self):
        """Test add_task output schema requires success field."""
        from src.mcp_tools.add_task import AddTaskOutput

        with pytest.raises(ValidationError) as exc_info:
            AddTaskOutput()

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('success',) for error in errors)

    async def test_add_task_context_structure(self, mcp_context):
        """Test add_task receives proper context structure."""
        # Context should contain user_id, request_id, timestamp
        assert "user_id" in mcp_context
        assert "request_id" in mcp_context
        assert "timestamp" in mcp_context

        assert isinstance(mcp_context["user_id"], int)
        assert isinstance(mcp_context["request_id"], str)
        assert isinstance(mcp_context["timestamp"], str)

    async def test_add_task_tool_function_exists(self):
        """Test add_task tool function is defined and callable."""
        from src.mcp_tools.add_task import add_task

        assert callable(add_task)

    async def test_add_task_tool_metadata(self):
        """Test add_task tool has proper metadata for MCP registration."""
        from src.mcp_tools.add_task import TOOL_METADATA

        assert TOOL_METADATA["name"] == "add_task"
        assert TOOL_METADATA["description"] is not None
        assert len(TOOL_METADATA["description"]) > 0
        assert "title" in str(TOOL_METADATA).lower()
