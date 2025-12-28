"""Unit tests for the Task model."""

import pytest
from datetime import datetime

from models.task import Task


class TestTaskInitialization:
    """Tests for Task initialization."""

    def test_create_task_with_required_fields(self):
        """Test creating a task with only required fields."""
        task = Task(task_id=1, title="Test Task")
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.status == "pending"
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields."""
        created = datetime(2025, 1, 1, 12, 0, 0)
        task = Task(
            task_id=1,
            title="Test Task",
            description="Test Description",
            status="completed",
            created_at=created,
        )
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == "completed"
        assert task.created_at == created


class TestTaskTitleValidation:
    """Tests for task title validation."""

    def test_valid_title_length_min(self):
        """Test title with minimum valid length."""
        task = Task(task_id=1, title="A")
        assert task.title == "A"

    def test_valid_title_length_max(self):
        """Test title with maximum valid length."""
        task = Task(task_id=1, title="A" * 200)
        assert len(task.title) == 200

    def test_title_too_short(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title must be 1-200 characters"):
            Task(task_id=1, title="")

    def test_title_too_long(self):
        """Test that title over 200 chars raises ValueError."""
        with pytest.raises(ValueError, match="Title must be 1-200 characters"):
            Task(task_id=1, title="A" * 201)

    def test_title_must_be_string(self):
        """Test that non-string title raises TypeError."""
        with pytest.raises(TypeError):
            Task(task_id=1, title=123)

    def test_title_strips_whitespace(self):
        """Test that title strips leading/trailing whitespace."""
        task = Task(task_id=1, title="  Test Task  ")
        assert task.title == "Test Task"


class TestTaskDescriptionValidation:
    """Tests for task description validation."""

    def test_valid_empty_description(self):
        """Test that empty description is allowed."""
        task = Task(task_id=1, title="Test", description="")
        assert task.description == ""

    def test_valid_max_length_description(self):
        """Test description with maximum valid length."""
        task = Task(task_id=1, title="Test", description="A" * 1000)
        assert len(task.description) == 1000

    def test_description_too_long(self):
        """Test that description over 1000 chars raises ValueError."""
        with pytest.raises(ValueError, match="Description must be 1000 characters or less"):
            Task(task_id=1, title="Test", description="A" * 1001)

    def test_description_must_be_string(self):
        """Test that non-string description raises TypeError."""
        with pytest.raises(TypeError):
            Task(task_id=1, title="Test", description=123)


class TestTaskStatusValidation:
    """Tests for task status validation."""

    def test_valid_pending_status(self):
        """Test that pending status is valid."""
        task = Task(task_id=1, title="Test", status="pending")
        assert task.status == "pending"

    def test_valid_completed_status(self):
        """Test that completed status is valid."""
        task = Task(task_id=1, title="Test", status="completed")
        assert task.status == "completed"

    def test_status_case_insensitive(self):
        """Test that status is case insensitive."""
        task = Task(task_id=1, title="Test", status="PENDING")
        assert task.status == "pending"

    def test_invalid_status(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Status must be one of"):
            Task(task_id=1, title="Test", status="invalid")

    def test_status_must_be_string(self):
        """Test that non-string status raises TypeError."""
        with pytest.raises(TypeError):
            Task(task_id=1, title="Test", status=123)


class TestTaskIdValidation:
    """Tests for task ID validation."""

    def test_valid_id(self):
        """Test that valid ID is accepted."""
        task = Task(task_id=1, title="Test")
        assert task.id == 1

    def test_id_zero_raises_error(self):
        """Test that ID of 0 raises ValueError."""
        with pytest.raises(ValueError, match="Task ID must be a positive integer"):
            Task(task_id=0, title="Test")

    def test_negative_id_raises_error(self):
        """Test that negative ID raises ValueError."""
        with pytest.raises(ValueError, match="Task ID must be a positive integer"):
            Task(task_id=-1, title="Test")


class TestTaskEquality:
    """Tests for Task equality."""

    def test_equal_tasks(self):
        """Test that two tasks with same values are equal."""
        created = datetime(2025, 1, 1, 12, 0, 0)
        task1 = Task(task_id=1, title="Test", description="Desc", status="pending", created_at=created)
        task2 = Task(task_id=1, title="Test", description="Desc", status="pending", created_at=created)
        assert task1 == task2

    def test_different_tasks(self):
        """Test that tasks with different values are not equal."""
        task1 = Task(task_id=1, title="Test 1")
        task2 = Task(task_id=2, title="Test 2")
        assert task1 != task2


class TestTaskToDict:
    """Tests for Task.to_dict() method."""

    def test_to_dict_returns_correct_format(self):
        """Test that to_dict returns expected dictionary format."""
        created = datetime(2025, 1, 1, 12, 0, 0)
        task = Task(
            task_id=1,
            title="Test",
            description="Desc",
            status="pending",
            created_at=created,
        )
        result = task.to_dict()
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["title"] == "Test"
        assert result["description"] == "Desc"
        assert result["status"] == "pending"
        assert result["created_at"] == "2025-01-01T12:00:00"


class TestTaskRepr:
    """Tests for Task __repr__ method."""

    def test_repr_contains_task_info(self):
        """Test that repr contains task information."""
        task = Task(task_id=1, title="Test Task", status="pending")
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "1" in repr_str
        assert "Test Task" in repr_str
        assert "pending" in repr_str
