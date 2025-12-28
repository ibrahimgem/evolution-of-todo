"""Unit tests for the TaskService."""

import pytest

from models.task import Task
from services.task_service import TaskService


class TestTaskServiceInitialization:
    """Tests for TaskService initialization."""

    def test_initial_state(self):
        """Test that a new TaskService has empty tasks and next_id=1."""
        service = TaskService()
        assert service.tasks == []
        assert service.next_id == 1


class TestAddTask:
    """Tests for TaskService.add_task()."""

    def test_add_single_task(self):
        """Test adding a single task."""
        service = TaskService()
        task = service.add_task("Test Task")
        assert len(service.tasks) == 1
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.status == "pending"

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks gets sequential IDs."""
        service = TaskService()
        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")
        task3 = service.add_task("Task 3")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_with_description(self):
        """Test adding a task with description."""
        service = TaskService()
        task = service.add_task("Test Task", "Test Description")
        assert task.description == "Test Description"

    def test_add_task_empty_title_raises_error(self):
        """Test that adding a task with empty title raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError):
            service.add_task("")

    def test_add_task_too_long_title_raises_error(self):
        """Test that adding a task with title > 200 chars raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError):
            service.add_task("A" * 201)

    def test_add_task_creates_copy(self):
        """Test that tasks returns a copy, not the original list."""
        service = TaskService()
        task = service.add_task("Test Task")
        # Modify the returned list
        service.tasks.append(task)
        # Original should be unchanged
        assert len(service.tasks) == 1


class TestGetAllTasks:
    """Tests for TaskService.get_all_tasks()."""

    def test_empty_service(self):
        """Test getting all tasks from empty service."""
        service = TaskService()
        assert service.get_all_tasks() == []

    def test_get_all_returns_all(self):
        """Test that get_all_tasks returns all tasks."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        tasks = service.get_all_tasks()
        assert len(tasks) == 2


class TestGetTaskById:
    """Tests for TaskService.get_task_by_id()."""

    def test_get_existing_task(self):
        """Test getting an existing task by ID."""
        service = TaskService()
        added = service.add_task("Test Task")
        found = service.get_task_by_id(1)
        assert found is added

    def test_get_nonexistent_task(self):
        """Test getting a non-existent task returns None."""
        service = TaskService()
        found = service.get_task_by_id(999)
        assert found is None


class TestUpdateTask:
    """Tests for TaskService.update_task()."""

    def test_update_title(self):
        """Test updating task title."""
        service = TaskService()
        service.add_task("Original")
        updated = service.update_task(1, title="Updated")
        assert updated.title == "Updated"

    def test_update_description(self):
        """Test updating task description."""
        service = TaskService()
        service.add_task("Test", "Original")
        updated = service.update_task(1, description="Updated")
        assert updated.description == "Updated"

    def test_update_both(self):
        """Test updating both title and description."""
        service = TaskService()
        service.add_task("Original", "Original Desc")
        updated = service.update_task(1, title="New", description="New Desc")
        assert updated.title == "New"
        assert updated.description == "New Desc"

    def test_update_nonexistent_task(self):
        """Test updating non-existent task raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task 999 not found"):
            service.update_task(999, title="New")

    def test_update_with_none_keeps_original(self):
        """Test that passing None keeps original value."""
        service = TaskService()
        service.add_task("Original", "Original Desc")
        updated = service.update_task(1, title="New", description=None)
        assert updated.title == "New"
        assert updated.description == "Original Desc"


class TestDeleteTask:
    """Tests for TaskService.delete_task()."""

    def test_delete_existing_task(self):
        """Test deleting an existing task returns True."""
        service = TaskService()
        service.add_task("Test")
        result = service.delete_task(1)
        assert result is True
        assert len(service.tasks) == 0

    def test_delete_nonexistent_task(self):
        """Test deleting non-existent task returns False."""
        service = TaskService()
        result = service.delete_task(999)
        assert result is False

    def test_delete_changes_ids(self):
        """Test that IDs don't reuse after delete."""
        service = TaskService()
        task1 = service.add_task("Task 1")
        service.add_task("Task 2")
        service.delete_task(1)
        task3 = service.add_task("Task 3")
        assert task3.id == 3


class TestToggleComplete:
    """Tests for TaskService.toggle_complete()."""

    def test_toggle_pending_to_completed(self):
        """Test toggling pending task to completed."""
        service = TaskService()
        service.add_task("Test")
        task = service.toggle_complete(1)
        assert task.status == "completed"

    def test_toggle_completed_to_pending(self):
        """Test toggling completed task back to pending."""
        service = TaskService()
        service.add_task("Test")
        service.toggle_complete(1)
        task = service.toggle_complete(1)
        assert task.status == "pending"

    def test_toggle_nonexistent_task(self):
        """Test toggling non-existent task raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task 999 not found"):
            service.toggle_complete(999)


class TestGetTasksByStatus:
    """Tests for TaskService.get_tasks_by_status()."""

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        service = TaskService()
        service.add_task("Task 1")  # pending
        service.add_task("Task 2", status="completed")
        service.add_task("Task 3")  # pending
        pending = service.get_tasks_by_status("pending")
        assert len(pending) == 2

    def test_get_completed_tasks(self):
        """Test getting completed tasks."""
        service = TaskService()
        service.add_task("Task 1")  # pending
        service.add_task("Task 2", status="completed")
        completed = service.get_tasks_by_status("completed")
        assert len(completed) == 1


class TestClearAll:
    """Tests for TaskService.clear_all()."""

    def test_clear_all_resets(self):
        """Test that clear_all removes all tasks and resets ID."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.clear_all()
        assert service.tasks == []
        assert service.next_id == 1
