"""Task data model with validation."""

from datetime import datetime
from typing import Optional


class Task:
    """Represents a todo task."""

    # Validation constants
    TITLE_MIN_LENGTH = 1
    TITLE_MAX_LENGTH = 200
    DESCRIPTION_MAX_LENGTH = 1000
    VALID_STATUSES = ("pending", "completed")

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str = "",
        status: str = "pending",
        created_at: Optional[datetime] = None,
    ):
        """Initialize a Task instance.

        Args:
            task_id: Unique identifier for the task
            title: Title of the task (1-200 characters)
            description: Detailed description of the task (optional, max 1000 chars)
            status: Status of the task ("pending" or "completed")
            created_at: Timestamp when task was created (defaults to now)
        """
        # Use setters for validation
        self.id = task_id
        self.title = title
        self.description = description
        self.status = status
        self._created_at = created_at or datetime.now()

    @property
    def id(self) -> int:
        """Get the task ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Set the task ID."""
        if not isinstance(value, int) or value < 1:
            raise ValueError("Task ID must be a positive integer")
        self._id = value

    @property
    def title(self) -> str:
        """Get the task title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set the task title with validation."""
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        value = value.strip()
        if not self.TITLE_MIN_LENGTH <= len(value) <= self.TITLE_MAX_LENGTH:
            raise ValueError(
                f"Title must be {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters"
            )
        self._title = value

    @property
    def description(self) -> str:
        """Get the task description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set the task description with validation."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        value = value.strip()
        if len(value) > self.DESCRIPTION_MAX_LENGTH:
            raise ValueError(
                f"Description must be {self.DESCRIPTION_MAX_LENGTH} characters or less"
            )
        self._description = value

    @property
    def status(self) -> str:
        """Get the task status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Set the task status with validation."""
        if not isinstance(value, str):
            raise TypeError("Status must be a string")
        value = value.strip().lower()
        if value not in self.VALID_STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        self._status = value

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime) -> None:
        """Set the creation timestamp."""
        if not isinstance(value, datetime):
            raise TypeError("created_at must be a datetime object")
        self._created_at = value

    def __repr__(self) -> str:
        """Return a string representation of the Task."""
        return (
            f"Task(id={self._id!r}, title={self._title!r}, "
            f"status={self._status!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Task."""
        if not isinstance(other, Task):
            return NotImplemented
        return (
            self._id == other._id
            and self._title == other._title
            and self._description == other._description
            and self._status == other._status
        )

    def to_dict(self) -> dict:
        """Convert Task to a dictionary."""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "status": self._status,
            "created_at": self._created_at.isoformat(),
        }
