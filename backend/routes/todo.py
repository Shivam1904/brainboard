"""
TODO routes for todo management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from db.dependency import get_db_session_dependency
from services.todo_service import TodoService
from schemas.todo import (
    UpdateActivityRequest, 
    UpdateTodoDetailsRequest,
    TodoDetailsAndActivityResponse,
    TodoDetailsResponse
)
from utils.errors import raise_not_found, raise_database_error

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# DEPENDENCIES
# ============================================================================
def get_default_user_id(db: AsyncSession = Depends(get_db_session_dependency)) -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

# ============================================================================
# TODO ENDPOINTS
# ============================================================================
@router.get("/getTodoDetailsAndActivity/{widget_id}", response_model=TodoDetailsAndActivityResponse)
async def get_todo_details_and_activity(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get todo details and activity for a widget."""
    try:
        service = TodoService(db)
        return await service.get_todo_details_and_activity(widget_id, user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get todo details: {str(e)}")

@router.post("/updateStatus/{activity_id}")
async def update_status(
    activity_id: str,
    status: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update todo activity status."""
    try:
        service = TodoService(db)
        return await service.update_status(activity_id, user_id, status)
    except Exception as e:
        raise raise_database_error(f"Failed to update status: {str(e)}")

@router.post("/updateProgress/{activity_id}")
async def update_progress(
    activity_id: str,
    progress: int,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update todo activity progress."""
    try:
        service = TodoService(db)
        return await service.update_progress(activity_id, user_id, progress)
    except Exception as e:
        raise raise_database_error(f"Failed to update progress: {str(e)}")

@router.post("/updateActivity/{activity_id}")
async def update_activity(
    activity_id: str,
    update_data: UpdateActivityRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update a todo activity."""
    try:
        service = TodoService(db)
        return await service.update_activity(activity_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update activity: {str(e)}")

@router.get("/getTodoDetails/{widget_id}", response_model=TodoDetailsResponse)
async def get_todo_details(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get todo details for a widget."""
    try:
        service = TodoService(db)
        result = await service.get_todo_details(widget_id, user_id)
        if not result:
            raise raise_not_found("Todo details not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get todo details: {str(e)}")

@router.post("/updateDetails/{todo_details_id}")
async def update_todo_details(
    todo_details_id: str,
    update_data: UpdateTodoDetailsRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update todo details."""
    try:
        service = TodoService(db)
        return await service.update_todo_details(todo_details_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update todo details: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_todos(
    user_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all todos for a user."""
    try:
        service = TodoService(db)
        return await service.get_user_todos(user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get user todos: {str(e)}")

@router.get("/getTodoList/{todo_type}")
async def get_todo_list_by_type(
    todo_type: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get todos by type (todo-habit, todo-task, todo-event)."""
    try:
        service = TodoService(db)
        return await service.get_todos_by_type(user_id, todo_type)
    except Exception as e:
        raise raise_database_error(f"Failed to get todos by type: {str(e)}") 