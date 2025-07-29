"""
Todo Router - API endpoints for todo operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from core.database import get_db
from services.todo_service import TodoService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["todo"])

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    from models.database import User
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        default_user = User(
            email="default@brainboard.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user.id

# ============================================================================
# TODO ENDPOINTS
# ============================================================================

@router.get("/getTodayTodoList/{todo_type}")
async def get_today_todo_list(
    todo_type: str,
    db: Session = Depends(get_db)
):
    """
    Get today's todo activities filtered by type (habit/task)
    """
    try:
        service = TodoService(db)
        todos = service.get_today_todo_list(todo_type)
        
        return {
            "todo_type": todo_type,
            "todos": todos,
            "total_todos": len(todos)
        }
    except Exception as e:
        logger.error(f"Error getting today's todo list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get today's todo list: {str(e)}"
        )

@router.post("/updateActivity/{activity_id}")
async def update_todo_activity(
    activity_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update todo activity status and progress
    """
    try:
        service = TodoService(db)
        result = service.update_activity(activity_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update todo activity: {str(e)}"
        )

@router.get("/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}")
async def get_todo_item_details_and_activity(
    daily_widget_id: str,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get todo item details and activity for a specific widget
    """
    try:
        service = TodoService(db)
        result = service.get_todo_details_and_activity(daily_widget_id, widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo item not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting todo item details and activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get todo item details and activity: {str(e)}"
        )

@router.get("/getTodoDetails/{widget_id}")
async def get_todo_details(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get todo details for a specific widget
    """
    try:
        service = TodoService(db)
        result = service.get_todo_details(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting todo details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get todo details: {str(e)}"
        )

@router.post("/updateDetails/{todo_details_id}")
async def update_todo_details(
    todo_details_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update todo details
    """
    try:
        service = TodoService(db)
        result = service.update_todo_details(todo_details_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update todo details: {str(e)}"
        ) 