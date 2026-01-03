"""
MCP Tool: list_tasks

Retrieves user's tasks with optional filtering by status and pagination support.
Implements the contract defined in specs/003-ai-chatbot/contracts/mcp-tools.yaml.
"""
import logging
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from src.models import Task

logger = logging.getLogger(__name__)


# Input schema per contract
class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    status: Literal["all", "complete", "incomplete"] = Field(
        default="all",
        description="Filter by completion status"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum tasks to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )


# Output schema per contract
class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""

    success: bool = Field(description="Operation success status")
    tasks: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of tasks if successful"
    )
    total: Optional[int] = Field(
        default=None,
        description="Total count of tasks matching filter"
    )
    offset: Optional[int] = Field(
        default=None,
        description="Pagination offset used"
    )
    limit: Optional[int] = Field(
        default=None,
        description="Limit used"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if success=false"
    )


# Tool metadata for MCP registration
TOOL_METADATA = {
    "name": "list_tasks",
    "description": "Retrieve user's tasks with optional filtering by completion status (all, complete, incomplete) and pagination support. Returns tasks ordered by creation date (newest first) with full details including id, title, description, completion status, due date, and timestamps.",
    "input_schema": ListTasksInput.model_json_schema(),
    "output_schema": ListTasksOutput.model_json_schema()
}


async def list_tasks(
    input_data: ListTasksInput,
    db: AsyncSession,
    context: Dict[str, Any]
) -> ListTasksOutput:
    """
    Execute list_tasks tool: retrieve user's tasks with filtering and pagination.

    Args:
        input_data: Validated input containing status filter, limit, offset
        db: Database session
        context: Execution context with user_id, request_id, timestamp

    Returns:
        ListTasksOutput with success status, tasks list, pagination info, or error message

    Raises:
        No exceptions - all errors are caught and returned in error field
    """
    try:
        user_id = context.get("user_id")
        request_id = context.get("request_id", "unknown")

        if not user_id:
            logger.error(
                f"[{request_id}] list_tasks called without user_id in context"
            )
            return ListTasksOutput(
                success=False,
                error="Authentication required: user_id not found in context"
            )

        # Log tool execution start
        logger.info(
            f"[{request_id}] list_tasks tool executing for user_id={user_id}, "
            f"status={input_data.status}, limit={input_data.limit}, offset={input_data.offset}"
        )

        # Build base query - filter by user_id
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if input_data.status == "complete":
            query = query.where(Task.completed == True)
        elif input_data.status == "incomplete":
            query = query.where(Task.completed == False)
        # "all" status - no additional filter needed

        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()

        # Order by created_at DESC (newest first)
        query = query.order_by(Task.created_at.desc())

        # Apply pagination
        query = query.offset(input_data.offset).limit(input_data.limit)

        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()

        # Convert tasks to dictionaries per contract
        tasks_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            tasks_list.append(task_dict)

        # Log success
        logger.info(
            f"[{request_id}] list_tasks tool succeeded: "
            f"returned {len(tasks_list)} tasks, total={total_count}"
        )

        return ListTasksOutput(
            success=True,
            tasks=tasks_list,
            total=total_count,
            offset=input_data.offset,
            limit=input_data.limit
        )

    except Exception as e:
        # Database or unexpected errors
        error_msg = f"Failed to list tasks: {str(e)}"
        logger.error(
            f"[{context.get('request_id', 'unknown')}] list_tasks tool error: {error_msg}",
            exc_info=True
        )
        return ListTasksOutput(
            success=False,
            error=error_msg
        )


# Export tool components
__all__ = ['list_tasks', 'ListTasksInput', 'ListTasksOutput', 'TOOL_METADATA']
