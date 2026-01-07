"""
MCP Tool: complete_task
Marks a task as complete or incomplete for authenticated user.
Implements contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models import Task
from ..models import get_utc_now

logger = logging.getLogger(__name__)

# Input schema per contract
class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    task_id: int = Field(description="ID of the task to update (required)")
    completed: bool = Field(description="Completion status (required)")

# Output schema per contract
class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task tool."""
    success: bool = Field(description="Operation success status")
    task: Optional[Dict[str, Any]] = Field(default=None, description="Task object if successful")
    error: Optional[str] = Field(default=None, description="Error message if success=false")

# Tool metadata for MCP registration
TOOL_METADATA = {
    "name": "complete_task",
    "description": "Mark a task as complete or incomplete. Requires task_id and a boolean for completed status.",
    "input_schema": CompleteTaskInput.model_json_schema(),
    "output_schema": CompleteTaskOutput.model_json_schema()
}

async def complete_task(
    input_data: CompleteTaskInput,
    db: AsyncSession,
    context: Dict[str, Any]
) -> CompleteTaskOutput:
    """
    Execute complete_task tool: mark a task as complete or incomplete.

    Args:
        input_data: Validated input containing task_id and completed status
        db: Database session
        context: Execution context with user_id, request_id, timestamp

    Returns:
        CompleteTaskOutput with success status, task data, or error message
    Raises:
        No exceptions - all errors are caught and returned in error field
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(
                f"[{request_id}] complete_task called without user_id in context"
            )
            return CompleteTaskOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        # Log tool execution start
        logger.info(
            f"[{request_id}] complete_task tool executing for user_id={user_id}, "
            f"task_id={input_data.task_id}, completed={input_data.completed}"
        )

        # Fetch task and verify ownership
        statement = select(Task).where(Task.id == input_data.task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(
                f"[{request_id}] complete_task: Task {input_data.task_id} not found or access denied for user {user_id}"
            )
            return CompleteTaskOutput(
                success=False,
                error=f"Task {input_data.task_id} not found or access denied"
            )

        # Update task
        task.completed = input_data.completed
        task.updated_at = get_utc_now()

        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Log success
        logger.info(
            f"[{request_id}] complete_task tool succeeded: task_id={task.id}, "
            f"completed={task.completed}"
        )

        # Build response per contract
        task_dict = {
            "id": task.id,
            "title": task.title,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat()
        }

        return CompleteTaskOutput(
            success=True,
            task=task_dict
        )

    except ValueError as ve:
        # Validation errors (e.g., past due date)
        error_msg = str(ve)
        logger.warning(
            f"[{context.get('request_id', 'unknown')}] complete_task validation error: {error_msg}"
        )
        return CompleteTaskOutput(
            success=False,
            error=error_msg
        )

    except Exception as e:
        # Database or unexpected errors
        error_msg = f"Failed to complete task: {str(e)}"
        logger.error(
            f"[{context.get('request_id', 'unknown')}] complete_task tool error: {error_msg}",
            exc_info=True
        )
        return CompleteTaskOutput(
            success=False,
            error=error_msg
        )

# Export tool components
__all__ = ['complete_task', 'CompleteTaskInput', 'CompleteTaskOutput', 'TOOL_METADATA']
