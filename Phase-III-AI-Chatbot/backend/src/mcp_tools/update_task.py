"""
MCP Tool: update_task

Updates task fields (partial update supported) for the authenticated user.
Implements the contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models import Task, get_utc_now

logger = logging.getLogger(__name__)


# Valid priority and category values
VALID_PRIORITIES = ["low", "medium", "high"]
VALID_CATEGORIES = ["work", "personal", "shopping", "health", "finance", "education", "other"]


# Input schema per contract
class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    task_id: int = Field(description="ID of the task to update (required)")
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="New task title (optional)")
    description: Optional[str] = Field(default=None, max_length=1000, description="New task description (optional)")
    priority: Optional[str] = Field(default=None, description="Task priority: low, medium, or high (optional)")
    category: Optional[str] = Field(default=None, description="Task category: work, personal, shopping, health, finance, education, other (optional)")
    due_date: Optional[datetime] = Field(default=None, description="New due date in ISO8601 format (optional)")

    @field_validator('title')
    @classmethod
    def strip_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from title if provided."""
        if v is not None:
            return v.strip()
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority is one of the allowed values."""
        if v is None:
            return None
        v = v.lower()
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category is one of the allowed values if provided."""
        if v is None:
            return None
        v = v.lower()
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v

    @field_validator('due_date')
    @classmethod
    def validate_future_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is in the future if provided."""
        if v is not None:
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError("Due date must be in the future")
        return v


# Output schema per contract
class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""
    success: bool = Field(description="Operation success status")
    task: Optional[Dict[str, Any]] = Field(default=None, description="Task object if successful")
    error: Optional[str] = Field(default=None, description="Error message if success=false")


# Tool metadata for MCP registration
TOOL_METADATA = {
    "name": "update_task",
    "description": "Update task fields like title, description, or due_date. Requires task_id and at least one field to update.",
    "input_schema": UpdateTaskInput.model_json_schema(),
    "output_schema": UpdateTaskOutput.model_json_schema()
}


async def update_task(
    input_data: UpdateTaskInput,
    db: AsyncSession,
    context: Dict[str, Any]
) -> UpdateTaskOutput:
    """
    Execute update_task tool: update task fields.
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(f"[{request_id}] update_task called without user_id in context")
            return UpdateTaskOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        # Validate that at least one update field is provided
        if all(v is None for v in [input_data.title, input_data.description, input_data.priority, input_data.category, input_data.due_date]):
            return UpdateTaskOutput(
                success=False,
                error="At least one field (title, description, priority, category, due_date) must be provided"
            )

        logger.info(f"[{request_id}] update_task tool executing for user_id={user_id}, task_id={input_data.task_id}")

        # Fetch task and verify ownership
        statement = select(Task).where(Task.id == input_data.task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"[{request_id}] update_task: Task {input_data.task_id} not found or access denied for user {user_id}")
            return UpdateTaskOutput(
                success=False,
                error=f"Task {input_data.task_id} not found or access denied"
            )

        # Apply updates
        if input_data.title is not None:
            task.title = input_data.title
        if input_data.description is not None:
            task.description = input_data.description
        if input_data.priority is not None:
            task.priority = input_data.priority
        if input_data.category is not None:
            task.category = input_data.category
        if input_data.due_date is not None:
            # Already validated as future date, use timezone-naive UTC for database compatibility
            if input_data.due_date.tzinfo is None:
                task.due_date = input_data.due_date.replace(tzinfo=timezone.utc).replace(tzinfo=None)
            else:
                task.due_date = input_data.due_date.replace(tzinfo=None)

        task.updated_at = get_utc_now()

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"[{request_id}] update_task tool succeeded: task_id={task.id}, title='{task.title}'")

        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "category": task.category,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "user_id": task.user_id
        }

        return UpdateTaskOutput(
            success=True,
            task=task_dict
        )

    except ValueError as ve:
        return UpdateTaskOutput(
            success=False,
            error=str(ve)
        )
    except Exception as e:
        error_msg = f"Failed to update task: {str(e)}"
        logger.error(f"[{context.get('request_id', 'unknown')}] update_task tool error: {error_msg}", exc_info=True)
        return UpdateTaskOutput(
            success=False,
            error=error_msg
        )


# Export tool components
__all__ = ['update_task', 'UpdateTaskInput', 'UpdateTaskOutput', 'TOOL_METADATA']
