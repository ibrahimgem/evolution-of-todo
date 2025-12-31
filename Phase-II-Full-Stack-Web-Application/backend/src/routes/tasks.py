from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from datetime import datetime, timezone
from ..database import get_db
from ..models import Task, User, TaskCreate, TaskRead, TaskUpdate
from ..auth import get_current_user
from ..exceptions import BusinessException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["tasks"])

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def get_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks for a specific user
    """
    # Ensure user can only access their own tasks
    if current_user.id != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.id} tried to access tasks for user {user_id}")
        raise BusinessException(
            message="Not authorized to access these tasks",
            error_code="UNAUTHORIZED_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get all tasks for the user, ordered by creation date
        result = await db.execute(
            select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        )
        tasks = result.scalars().all()

        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return tasks

    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to retrieve tasks",
            error_code="TASK_RETRIEVAL_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/{user_id}/tasks", response_model=TaskRead)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task for a specific user
    """
    # Ensure user can only create tasks for themselves
    if current_user.id != user_id:
        logger.warning(f"Unauthorized task creation attempt: user {current_user.id} tried to create task for user {user_id}")
        raise BusinessException(
            message="Not authorized to create tasks for this user",
            error_code="UNAUTHORIZED_CREATION",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Enhanced input validation
    title = task_data.title.strip() if task_data.title else ""
    if not title:
        raise BusinessException(
            message="Title is required and cannot be empty",
            error_code="INVALID_TITLE",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(title) > 200:
        raise BusinessException(
            message="Title must be 200 characters or less",
            error_code="TITLE_TOO_LONG",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    description = task_data.description.strip() if task_data.description else None
    if description and len(description) > 1000:
        raise BusinessException(
            message="Description must be 1000 characters or less",
            error_code="DESCRIPTION_TOO_LONG",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create new task
        task = Task(
            title=title,
            description=description,
            completed=task_data.completed or False,
            user_id=user_id
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")
        return task

    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to create task",
            error_code="TASK_CREATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID
    """
    # Ensure user can only access their own tasks
    if current_user.id != user_id:
        logger.warning(f"Unauthorized task access attempt: user {current_user.id} tried to access task {task_id} for user {user_id}")
        raise BusinessException(
            message="Not authorized to access this task",
            error_code="UNAUTHORIZED_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get specific task
        result = await db.execute(
            select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise BusinessException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"Retrieved task {task_id} for user {user_id}")
        return task

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to retrieve task",
            error_code="TASK_RETRIEVAL_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific task by ID
    """
    # Ensure user can only update their own tasks
    if current_user.id != user_id:
        logger.warning(f"Unauthorized task update attempt: user {current_user.id} tried to update task {task_id} for user {user_id}")
        raise BusinessException(
            message="Not authorized to update this task",
            error_code="UNAUTHORIZED_UPDATE",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get the existing task
        result = await db.execute(
            select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise BusinessException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Enhanced validation for update fields
        if task_update.title is not None:
            title = task_update.title.strip()
            if not title:
                raise BusinessException(
                    message="Title cannot be empty",
                    error_code="INVALID_TITLE",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if len(title) > 200:
                raise BusinessException(
                    message="Title must be 200 characters or less",
                    error_code="TITLE_TOO_LONG",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            task.title = title

        if task_update.description is not None:
            description = task_update.description.strip() if task_update.description else None
            if description and len(description) > 1000:
                raise BusinessException(
                    message="Description must be 1000 characters or less",
                    error_code="DESCRIPTION_TOO_LONG",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            task.description = description

        if task_update.completed is not None:
            task.completed = task_update.completed

        # Update the timestamp
        task.updated_at = datetime.now(timezone.utc)

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Updated task {task_id} for user {user_id}")
        return task

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to update task",
            error_code="TASK_UPDATE_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific task by ID
    """
    # Ensure user can only delete their own tasks
    if current_user.id != user_id:
        logger.warning(f"Unauthorized task deletion attempt: user {current_user.id} tried to delete task {task_id} for user {user_id}")
        raise BusinessException(
            message="Not authorized to delete this task",
            error_code="UNAUTHORIZED_DELETION",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get the task to delete
        result = await db.execute(
            select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise BusinessException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await db.delete(task)
        await db.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")
        return {"message": "Task deleted successfully"}

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to delete task",
            error_code="TASK_DELETION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle the completion status of a specific task
    """
    # Ensure user can only toggle completion for their own tasks
    if current_user.id != user_id:
        logger.warning(f"Unauthorized completion toggle attempt: user {current_user.id} tried to toggle task {task_id} for user {user_id}")
        raise BusinessException(
            message="Not authorized to update this task",
            error_code="UNAUTHORIZED_UPDATE",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get the task to toggle
        result = await db.execute(
            select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise BusinessException(
                message="Task not found",
                error_code="TASK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Toggle the completion status
        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Toggled completion status for task {task_id} (completed: {task.completed}) for user {user_id}")
        return task

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error toggling completion for task {task_id} for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to toggle task completion",
            error_code="TASK_TOGGLE_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{user_id}/tasks/stats")
async def get_task_stats(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task statistics for a user (total, completed, pending)
    """
    if current_user.id != user_id:
        raise BusinessException(
            message="Not authorized to access these statistics",
            error_code="UNAUTHORIZED_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get task counts
        total_result = await db.execute(
            select(Task).where(Task.user_id == user_id)
        )
        total_tasks = len(total_result.scalars().all())

        completed_result = await db.execute(
            select(Task).where(Task.user_id == user_id).where(Task.completed == True)
        )
        completed_tasks = len(completed_result.scalars().all())

        pending_tasks = total_tasks - completed_tasks

        return {
            "user_id": user_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        }

    except Exception as e:
        logger.error(f"Error getting task stats for user {user_id}: {str(e)}")
        raise BusinessException(
            message="Failed to retrieve task statistics",
            error_code="TASK_STATS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
