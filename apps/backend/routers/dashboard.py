"""
Dashboard Router - New API Structure
Handles dashboard widget management and daily widget retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date, datetime
import logging

from core.database import get_db
from models.database import User, DashboardWidgetDetails, DailyWidget
from models.schemas.dashboard_schemas import CreateWidgetRequest, UpdateWidgetRequest

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
        if target_date is None:
            target_date = date.today()
        
        daily_widgets = db.query(DailyWidget).filter(
            DailyWidget.date == target_date,
            DailyWidget.delete_flag == False
        ).order_by(DailyWidget.priority.desc()).all()
        
        widgets_data = []
        for daily_widget in daily_widgets:
            widget_data = {
                # "id": widget.id,
                "daily_widget_id": daily_widget.dashboard_widget_id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "category": widget.category,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "position": daily_widget.position,
                "grid_position": daily_widget.grid_position or widget.grid_size,
                "is_pinned": daily_widget.is_pinned,
                "ai_reasoning": daily_widget.ai_reasoning,
                "settings": widget.settings,
                "created_at": widget.created_at,
                "updated_at": widget.updated_at
            }
            widgets_data.append(widget_data)
        
        return {
            "date": target_date.isoformat(),
            "widgets": widgets_data,
            "total_widgets": len(widgets_data),
            "ai_generated": bool(widgets_data),
            "last_updated": datetime.utcnow().isoformat()
        }
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
        widgets = db.query(DashboardWidgetDetails).filter(
            DashboardWidgetDetails.user_id == user_id,
            DashboardWidgetDetails.delete_flag == False
        ).order_by(DashboardWidgetDetails.importance.desc()).all()
        
        widgets_data = []
        for widget in widgets:
            widget_data = {
                # "id": widget.id,
                "daily_widget_id": daily_widget.dashboard_widget_id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "frequency": widget.frequency,
                "importance": widget.importance,
                "title": widget.title,
                "category": widget.category,
                "created_at": widget.created_at.isoformat(),
                "updated_at": widget.updated_at.isoformat()
            }
            widgets_data.append(widget_data)
        
        return {
            "widgets": widgets_data,
            "total_widgets": len(widgets_data)
        }
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
    Creates a new widget in DashboardWidgetDetails with basic form data.
    """
    try:
        # Create new dashboard widget
        widget = DashboardWidgetDetails(
            user_id=user_id,
            widget_type=request.widget_type,
            frequency=request.frequency,
            importance=request.importance,
            title=request.title,
            category=request.category,
            created_by=user_id
        )
        
        db.add(widget)
        db.commit()
        db.refresh(widget)
        
        # Create corresponding details table entry based on widget type
        if request.widget_type in ["todo-habit", "todo-task", "todo-event"]:
            from models.database import ToDoDetails
            # Extract todo type from widget type
            todo_type = request.widget_type.replace("todo-", "")
            todo_details = ToDoDetails(
                widget_id=widget.id,
                title=request.title,
                todo_type=todo_type,  # 'habit', 'task', or 'event'
                created_by=user_id
            )
            db.add(todo_details)
        elif request.widget_type == "singleitemtracker":
            from models.database import SingleItemTrackerDetails
            tracker_details = SingleItemTrackerDetails(
                widget_id=widget.id,
                title=request.title,
                value_type="number",  # Default to number
                created_by=user_id
            )
            db.add(tracker_details)
        elif request.widget_type == "websearch":
            from models.database import WebSearchDetails
            websearch_details = WebSearchDetails(
                widget_id=widget.id,
                title=request.title,
                created_by=user_id
            )
            db.add(websearch_details)
        elif request.widget_type == "alarm":
            from models.database import AlarmDetails
            alarm_details = AlarmDetails(
                widget_id=widget.id,
                title=request.title,
                alarm_times=["09:00"],  # Default time
                created_by=user_id
            )
            db.add(alarm_details)
        
        db.commit()
        
        return {
            "message": "Widget created successfully",
            "widget_id": widget.id,
            "widget_type": widget.widget_type,
            "title": widget.title
        }
    except Exception as e:
        logger.error(f"Failed to create widget for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget: {str(e)}"
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
        from services.todo_service import TodoService
        service = TodoService(db)
        todos = service.get_todo_list_by_type(todo_type)
        
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