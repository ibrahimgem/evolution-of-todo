"""
MCP Tool: delete_task

Permanently deletes a task for the authenticated user.
Implements the contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models import Task

logger = logging.getLogger(__name__)


# Input schema per contract
class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    task_id: int = Field(description="ID of the task to delete (required)")


# Output schema per contract
class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""
    success: bool = Field(description="Operation success status")
    message: Optional[str] = Field(default=None, description="Detailed message if successful")
    deleted_task_id: Optional[int] = Field(default=None, description="ID of the deleted task")
    error: Optional[str] = Field(default=None, description="Error message if success=false")


# Tool metadata for MCP registration
TOOL_METADATA = {
    "name": "delete_task",
    "description": "Permanently delete a task. Requires task_id.",
    "input_schema": DeleteTaskInput.model_json_schema(),
    "output_schema": DeleteTaskOutput.model_json_schema()
}


async def delete_task(
    input_data: DeleteTaskInput,
    db: AsyncSession,
    context: Dict[str, Any]
) -> DeleteTaskOutput:
    """
    Execute delete_task tool: permanently delete a task.
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(f"[{request_id}] delete_task called without user_id in context")
            return DeleteTaskOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        logger.info(f"[{request_id}] delete_task tool executing for user_id={user_id}, task_id={input_data.task_id}")

        # Fetch task and verify ownership
        statement = select(Task).where(Task.id == input_data.task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"[{request_id}] delete_task: Task {input_data.task_id} not found or access denied for user {user_id}")
            return DeleteTaskOutput(
                success=False,
                error=f"Task {input_data.task_id} not found or access denied"
            )

        # Delete task
        await db.delete(task)
        await db.commit()

        logger.info(f"[{request_id}] delete_task tool succeeded: task_id={input_data.task_id}")

        return DeleteTaskOutput(
            success=True,
            message=f"Task {input_data.task_id} deleted successfully",
            deleted_task_id=input_data.task_id
        )

    except Exception as e:
        error_msg = f"Failed to delete task: {str(e)}"
        logger.error(f"[{context.get('request_id', 'unknown')}] delete_task tool error: {error_msg}", exc_info=True)
        return DeleteTaskOutput(
            success=False,
            error=error_msg
        )


# Export tool components
__all__ = ['delete_task', 'DeleteTaskInput', 'DeleteTaskOutput', 'TOOL_METADATA']
