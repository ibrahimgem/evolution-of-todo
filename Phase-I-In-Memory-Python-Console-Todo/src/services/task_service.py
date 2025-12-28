"""Task management service layer."""

from typing import List, Optional

from models.task import Task


class TaskService:
    """Manages todo tasks with in-memory storage."""

    def __init__(self):
        """Initialize the TaskService with empty task list."""
        self._tasks: List[Task] = []
        self._next_id: int = 1

    @property
    def tasks(self) -> List[Task]:
        """Get all tasks."""
        return self._tasks.copy()

    @property
    def next_id(self) -> int:
        """Get the next available task ID."""
        return self._next_id

    def add_task(self, title: str, description: str = "", status: str = "pending") -> Task:
        """Create a new task with a unique ID.

        Args:
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)
            status: Task status ("pending" or "completed")

        Returns:
            The newly created Task

        Raises:
            ValueError: If title is empty or too long
        """
        task = Task(
            task_id=self._next_id,
            title=title,
            description=description,
            status=status,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks sorted by creation order."""
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its ID.

        Args:
            task_id: The task ID to find

        Returns:
            The Task if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(
        self, task_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> Task:
        """Update an existing task's title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            The updated Task

        Raises:
            ValueError: If task not found or validation fails
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if task was deleted, False if not found
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False
        self._tasks.remove(task)
        return True

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle task status between pending and completed.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            The updated Task

        Raises:
            ValueError: If task not found
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        task.status = "completed" if task.status == "pending" else "pending"
        return task

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get all tasks with a specific status.

        Args:
            status: "pending" or "completed"

        Returns:
            List of tasks with the specified status
        """
        return [task for task in self._tasks if task.status == status]

    def clear_all(self) -> None:
        """Remove all tasks and reset ID counter."""
        self._tasks.clear()
        self._next_id = 1
