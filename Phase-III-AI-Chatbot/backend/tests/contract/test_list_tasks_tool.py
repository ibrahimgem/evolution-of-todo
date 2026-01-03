"""
Contract tests for list_tasks MCP tool.

Tests verify that list_tasks tool adheres to the MCP contract specification
defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError


@pytest.mark.contract
@pytest.mark.asyncio
class TestListTasksContract:
    """Test list_tasks tool contract compliance."""

    async def test_list_tasks_input_schema_valid_minimal(self):
        """Test list_tasks accepts minimal valid input (no parameters)."""
        from src.mcp_tools.list_tasks import ListTasksInput

        # All parameters should have defaults
        input_data = ListTasksInput()

        assert input_data.status == "all"
        assert input_data.limit == 50
        assert input_data.offset == 0

    async def test_list_tasks_input_schema_valid_with_status(self):
        """Test list_tasks accepts valid status filter."""
        from src.mcp_tools.list_tasks import ListTasksInput

        # Test all valid status values
        for status in ["all", "complete", "incomplete"]:
            input_data = ListTasksInput(status=status)
            assert input_data.status == status

    async def test_list_tasks_input_schema_invalid_status(self):
        """Test list_tasks rejects invalid status values."""
        from src.mcp_tools.list_tasks import ListTasksInput

        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(status="invalid")

        errors = exc_info.value.errors()
        assert any('status' in str(error['loc']) for error in errors)

    async def test_list_tasks_input_schema_limit_validation(self):
        """Test list_tasks validates limit (1-100)."""
        from src.mcp_tools.list_tasks import ListTasksInput

        # Test invalid limits
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(limit=0)

        errors = exc_info.value.errors()
        assert any('limit' in str(error['loc']) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(limit=101)

        errors = exc_info.value.errors()
        assert any('limit' in str(error['loc']) for error in errors)

        # Test valid edge cases
        ListTasksInput(limit=1)  # 1 - valid
        ListTasksInput(limit=100)  # 100 - valid

    async def test_list_tasks_input_schema_offset_validation(self):
        """Test list_tasks validates offset (>= 0)."""
        from src.mcp_tools.list_tasks import ListTasksInput

        # Test invalid offset
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(offset=-1)

        errors = exc_info.value.errors()
        assert any('offset' in str(error['loc']) for error in errors)

        # Test valid edge cases
        ListTasksInput(offset=0)  # 0 - valid
        ListTasksInput(offset=100)  # 100 - valid

    async def test_list_tasks_input_schema_complete(self):
        """Test list_tasks accepts all parameters."""
        from src.mcp_tools.list_tasks import ListTasksInput

        input_data = ListTasksInput(
            status="incomplete",
            limit=10,
            offset=5
        )

        assert input_data.status == "incomplete"
        assert input_data.limit == 10
        assert input_data.offset == 5

    async def test_list_tasks_output_schema_success_empty(self):
        """Test list_tasks output schema for empty result."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        output_data = ListTasksOutput(
            success=True,
            tasks=[],
            total=0,
            offset=0,
            limit=50
        )

        assert output_data.success is True
        assert output_data.tasks == []
        assert output_data.total == 0
        assert output_data.offset == 0
        assert output_data.limit == 50
        assert output_data.error is None

    async def test_list_tasks_output_schema_success_with_tasks(self):
        """Test list_tasks output schema with tasks."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        output_data = ListTasksOutput(
            success=True,
            tasks=[
                {
                    "id": 42,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": False,
                    "due_date": "2026-01-02T18:00:00Z",
                    "created_at": "2026-01-01T10:30:00Z",
                    "updated_at": "2026-01-01T10:30:00Z"
                },
                {
                    "id": 43,
                    "title": "Finish report",
                    "description": None,
                    "completed": True,
                    "due_date": None,
                    "created_at": "2026-01-01T09:00:00Z",
                    "updated_at": "2026-01-01T11:00:00Z"
                }
            ],
            total=2,
            offset=0,
            limit=50
        )

        assert output_data.success is True
        assert len(output_data.tasks) == 2
        assert output_data.tasks[0]["id"] == 42
        assert output_data.tasks[0]["title"] == "Buy groceries"
        assert output_data.tasks[0]["completed"] is False
        assert output_data.tasks[1]["id"] == 43
        assert output_data.tasks[1]["completed"] is True
        assert output_data.total == 2
        assert output_data.error is None

    async def test_list_tasks_output_schema_success_pagination(self):
        """Test list_tasks output schema with pagination."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        output_data = ListTasksOutput(
            success=True,
            tasks=[{"id": 1, "title": "Task 1", "completed": False}],
            total=25,  # Total tasks in DB
            offset=10,  # Starting from 11th task
            limit=10   # Returning 10 tasks
        )

        assert output_data.success is True
        assert len(output_data.tasks) == 1
        assert output_data.total == 25
        assert output_data.offset == 10
        assert output_data.limit == 10

    async def test_list_tasks_output_schema_error(self):
        """Test list_tasks output schema for error case."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        output_data = ListTasksOutput(
            success=False,
            error="Database connection failed"
        )

        assert output_data.success is False
        assert output_data.error == "Database connection failed"
        # Note: tasks, total, offset, limit are optional on error

    async def test_list_tasks_output_schema_requires_success_field(self):
        """Test list_tasks output schema requires success field."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        with pytest.raises(ValidationError) as exc_info:
            ListTasksOutput()

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('success',) for error in errors)

    async def test_list_tasks_context_structure(self, mcp_context):
        """Test list_tasks receives proper context structure."""
        # Context should contain user_id, request_id, timestamp
        assert "user_id" in mcp_context
        assert "request_id" in mcp_context
        assert "timestamp" in mcp_context

        assert isinstance(mcp_context["user_id"], int)
        assert isinstance(mcp_context["request_id"], str)
        assert isinstance(mcp_context["timestamp"], str)

    async def test_list_tasks_tool_function_exists(self):
        """Test list_tasks tool function is defined and callable."""
        from src.mcp_tools.list_tasks import list_tasks

        assert callable(list_tasks)

    async def test_list_tasks_tool_metadata(self):
        """Test list_tasks tool has proper metadata for MCP registration."""
        from src.mcp_tools.list_tasks import TOOL_METADATA

        assert TOOL_METADATA["name"] == "list_tasks"
        assert TOOL_METADATA["description"] is not None
        assert len(TOOL_METADATA["description"]) > 0
        assert "filter" in str(TOOL_METADATA).lower() or "list" in str(TOOL_METADATA).lower()

    async def test_list_tasks_task_fields_complete(self):
        """Test list_tasks output includes all required task fields."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        task_dict = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "completed": False,
            "due_date": "2026-01-02T00:00:00Z",
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-01T10:00:00Z"
        }

        output_data = ListTasksOutput(
            success=True,
            tasks=[task_dict],
            total=1,
            offset=0,
            limit=50
        )

        # Verify all required fields are present
        task = output_data.tasks[0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "completed" in task
        assert "due_date" in task
        assert "created_at" in task
        assert "updated_at" in task

    async def test_list_tasks_nullable_fields(self):
        """Test list_tasks handles nullable fields (description, due_date)."""
        from src.mcp_tools.list_tasks import ListTasksOutput

        task_with_nulls = {
            "id": 1,
            "title": "Test Task",
            "description": None,  # Nullable
            "completed": False,
            "due_date": None,  # Nullable
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-01T10:00:00Z"
        }

        output_data = ListTasksOutput(
            success=True,
            tasks=[task_with_nulls],
            total=1,
            offset=0,
            limit=50
        )

        assert output_data.success is True
        assert output_data.tasks[0]["description"] is None
        assert output_data.tasks[0]["due_date"] is None
