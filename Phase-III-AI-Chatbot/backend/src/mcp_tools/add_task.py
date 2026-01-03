"""
MCP Tool: add_task

Creates a new task for the authenticated user with optional description and due date.
Implements the contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models import Task

logger = logging.getLogger(__name__)


# Input schema per contract
class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date in ISO8601 format (optional, must be future date)"
    )

    @field_validator('title')
    @classmethod
    def strip_title(cls, v: str) -> str:
        """Strip leading/trailing whitespace from title."""
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def validate_future_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is in the future if provided."""
        if v is not None:
            # Ensure timezone-aware comparison
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)

            if v <= now:
                raise ValueError("Due date must be in the future")

        return v


# Output schema per contract
class AddTaskOutput(BaseModel):
    """Output schema for add_task tool."""

    success: bool = Field(description="Operation success status")
    task: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Task object if successful"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if success=false"
    )


# Tool metadata for MCP registration
TOOL_METADATA = {
    "name": "add_task",
    "description": "Create a new task for the authenticated user. Accepts a title (required), optional description, and optional due date. Returns the created task with ID and timestamps.",
    "input_schema": AddTaskInput.model_json_schema(),
    "output_schema": AddTaskOutput.model_json_schema()
}


async def add_task(
    input_data: AddTaskInput,
    db: AsyncSession,
    context: Dict[str, Any]
) -> AddTaskOutput:
    """
    Execute add_task tool: create a new task for the user.

    Args:
        input_data: Validated input containing title, optional description, optional due_date
        db: Database session
        context: Execution context with user_id, request_id, timestamp

    Returns:
        AddTaskOutput with success status, task data, or error message

    Raises:
        No exceptions - all errors are caught and returned in error field
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(
                f"[{request_id}] add_task called without user_id in context"
            )
            return AddTaskOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        # Log tool execution start
        logger.info(
            f"[{request_id}] add_task tool executing for user_id={user_id}, "
            f"title='{input_data.title}'"
        )

        # Create task instance
        task = Task(
            user_id=user_id,
            title=input_data.title,
            description=input_data.description,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Add due_date if provided (already validated as future)
        if input_data.due_date:
            # Ensure timezone-aware
            if input_data.due_date.tzinfo is None:
                task.due_date = input_data.due_date.replace(tzinfo=timezone.utc)
            else:
                task.due_date = input_data.due_date

        # Persist to database
        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Log success
        logger.info(
            f"[{request_id}] add_task tool succeeded: task_id={task.id}, "
            f"title='{task.title}'"
        )

        # Build response per contract
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if hasattr(task, 'due_date') and task.due_date else None,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "user_id": task.user_id
        }

        return AddTaskOutput(
            success=True,
            task=task_dict
        )

    except ValueError as ve:
        # Validation errors (e.g., past due date)
        error_msg = str(ve)
        logger.warning(
            f"[{context.get('request_id', 'unknown')}] add_task validation error: {error_msg}"
        )
        return AddTaskOutput(
            success=False,
            error=error_msg
        )

    except Exception as e:
        # Database or unexpected errors
        error_msg = f"Failed to create task: {str(e)}"
        logger.error(
            f"[{context.get('request_id', 'unknown')}] add_task tool error: {error_msg}",
            exc_info=True
        )
        return AddTaskOutput(
            success=False,
            error=error_msg
        )


# Export tool components
__all__ = ['add_task', 'AddTaskInput', 'AddTaskOutput', 'TOOL_METADATA']
