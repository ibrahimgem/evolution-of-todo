"""
MCP Tool: complete_task

Marks a task as complete or incomplete for the authenticated user.
Implements the contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models import Task

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
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(f"[{request_id}] complete_task called without user_id in context")
            return CompleteTaskOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        logger.info(f"[{request_id}] complete_task tool executing for user_id={user_id}, task_id={input_data.task_id}, completed={input_data.completed}")

        # Fetch task and verify ownership
        statement = select(Task).where(Task.id == input_data.task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"[{request_id}] complete_task: Task {input_data.task_id} not found or access denied for user {user_id}")
            return CompleteTaskOutput(
                success=False,
                error=f"Task {input_data.task_id} not found or access denied"
            )

        # Update task
        task.completed = input_data.completed
        task.updated_at = datetime.now(timezone.utc)

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"[{request_id}] complete_task tool succeeded: task_id={task.id}, title='{task.title}', completed={task.completed}")

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

    except Exception as e:
        error_msg = f"Failed to complete task: {str(e)}"
        logger.error(f"[{context.get('request_id', 'unknown')}] complete_task tool error: {error_msg}", exc_info=True)
        return CompleteTaskOutput(
            success=False,
            error=error_msg
        )


# Export tool components
__all__ = ['complete_task', 'CompleteTaskInput', 'CompleteTaskOutput', 'TOOL_METADATA']
