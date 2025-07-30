"""
Dashboard Router - New API Structure
Handles dashboard widget management and daily widget retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date
import logging

from core.database import get_db
from models.database import User
from models.schemas.dashboard_schemas import CreateWidgetRequest, UpdateDailyWidgetRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboard"])

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        # Create default user if not exists
        default_user = User(
            email="default@brainboard.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user.id

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/getTodayWidgetList")
async def get_today_widget_list(
    target_date: Optional[date] = Query(None, description="Date for dashboard (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get today's widget list from table DailyWidget
    Returns AI-generated daily widget selections for the specified date.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.get_today_widget_list(target_date, user_id)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get today's widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get today's widgets: {str(e)}"
        )

@router.get("/getAllWidgetList")
async def get_all_widget_list(
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all dashboard widgets for the user
    Returns all widget configurations from DashboardWidgetDetails.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.get_all_widget_list(user_id)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get all widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get all widgets: {str(e)}"
        )

@router.post("/widget/addnew")
async def add_new_widget(
    request: CreateWidgetRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Add new dashboard widget
    Creates a new widget in DashboardWidgetDetails with basic form data and widget-specific details.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.create_widget(request, user_id)
        
        return result
    except Exception as e:
        logger.error(f"Failed to create widget for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget: {str(e)}"
        )

@router.post("/widget/updateWidgetDetails/{widget_id}")
async def update_widget(
    widget_id: str,
    request: CreateWidgetRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Update existing dashboard widget
    Updates a widget in DashboardWidgetDetails and its corresponding details table.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.update_widget(widget_id, request, user_id)
        
        return result
    except ValueError as e:
        if str(e) == "Widget not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update widget {widget_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
        )

@router.post("/widget/addtotoday/{widget_id}")
async def add_widget_to_today(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Add a widget to today's dashboard
    Creates entries in DailyWidget and corresponding activity tables.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.add_widget_to_today(widget_id, user_id)
        
        return result
    except ValueError as e:
        if str(e) == "Widget not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        elif str(e) == "Widget is already in today's dashboard":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Widget is already in today's dashboard"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to add widget {widget_id} to today's dashboard for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add widget to today's dashboard: {str(e)}"
        )


@router.post("/widgets/updateDailyWidget/{daily_widget_id}")
async def update_daily_widget_active(
    daily_widget_id: str,
    request: UpdateDailyWidgetRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Update the is_active column for a DailyWidget (activate/deactivate widget)
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        result = service_factory.dashboard_service.update_daily_widget_active(daily_widget_id, request.is_active)
        
        return result
    except ValueError as e:
        if str(e) == "DailyWidget not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DailyWidget not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update is_active: {str(e)}"
        )

@router.get("/getTodoList/{todo_type}")
async def get_todo_list_by_type(
    todo_type: str,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get todo list filtered by type (habit/task)
    Returns all todo details for the specified type.
    """
    try:
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(db)
        todos = service_factory.todo_service.get_todo_list_by_type(todo_type)
        
        return {
            "todo_type": todo_type,
            "todos": todos,
            "total_todos": len(todos)
        }
    except Exception as e:
        logger.error(f"Error getting todo list by type {todo_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get todo list: {str(e)}"
        ) 