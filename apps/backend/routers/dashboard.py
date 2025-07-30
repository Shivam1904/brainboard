"""
Dashboard Router - New API Structure
Handles dashboard widget management and daily widget retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date, datetime, timezone
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
        
        # Query DailyWidget table for today's widgets
        daily_widgets = db.query(DailyWidget).filter(
            DailyWidget.date == target_date,
            DailyWidget.delete_flag == False
        ).order_by(DailyWidget.priority.desc()).all()
        
        widgets_data = []
        for daily_widget in daily_widgets:
            # Get the first widget ID from the array for basic info
            # In practice, you might want to handle multiple widgets differently
            widget_id = daily_widget.widget_ids[0] if daily_widget.widget_ids else None
            
            # Get widget details if we have a widget ID
            widget_details = None
            if widget_id:
                widget_details = db.query(DashboardWidgetDetails).filter(
                    DashboardWidgetDetails.id == widget_id,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                ).first()
            
            widget_data = {
                "daily_widget_id": daily_widget.id,
                "widget_ids": daily_widget.widget_ids,
                "widget_type": daily_widget.widget_type,
                "priority": daily_widget.priority,
                "reasoning": daily_widget.reasoning,
                "date": daily_widget.date.isoformat(),
                "created_at": daily_widget.created_at.isoformat(),
                "updated_at": daily_widget.updated_at.isoformat()
            }
            
            # Add widget details if available
            if widget_details:
                widget_data.update({
                    "title": widget_details.title,
                    "category": widget_details.category,
                    "importance": widget_details.importance,
                    "frequency": widget_details.frequency
                })
            
            widgets_data.append(widget_data)
        
        return {
            "date": target_date.isoformat(),
            "widgets": widgets_data,
            "total_widgets": len(widgets_data),
            "ai_generated": bool(widgets_data),
            "last_updated": datetime.now(timezone.utc).isoformat()
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
                "id": widget.id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "frequency": widget.frequency,
                "importance": widget.importance,
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
    Creates a new widget in DashboardWidgetDetails with basic form data and widget-specific details.
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
            # Use provided todo_type or extract from widget type
            todo_type = request.todo_type or request.widget_type.replace("todo-", "")
            # Convert string date to Python date object
            due_date = None
            if request.due_date:
                due_date = datetime.strptime(request.due_date, '%Y-%m-%d').date()
            todo_details = ToDoDetails(
                widget_id=widget.id,
                title=request.title,
                todo_type=todo_type,  # 'habit', 'task', or 'event'
                due_date=due_date,  # Use provided due date
                created_by=user_id
            )
            db.add(todo_details)
        elif request.widget_type == "singleitemtracker":
            from models.database import SingleItemTrackerDetails
            tracker_details = SingleItemTrackerDetails(
                widget_id=widget.id,
                title=request.title,
                value_type=request.value_data_type or "number",  # Use provided type or default
                value_unit=request.value_data_unit or "units",   # Use provided unit or default
                target_value=request.target_value or "0",        # Use provided target or default
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
            # Use provided alarm time or default to 09:00
            alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
            alarm_details = AlarmDetails(
                widget_id=widget.id,
                title=request.title,
                alarm_times=alarm_times,
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

@router.post("/widget/updatewidget/{widget_id}")
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
        # Check if widget exists and belongs to user
        widget = db.query(DashboardWidgetDetails).filter(
            DashboardWidgetDetails.id == widget_id,
            DashboardWidgetDetails.user_id == user_id,
            DashboardWidgetDetails.delete_flag == False
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Update dashboard widget details
        widget.widget_type = request.widget_type
        widget.frequency = request.frequency
        widget.importance = request.importance
        widget.title = request.title
        widget.category = request.category
        widget.updated_at = datetime.now(timezone.utc)
        
        # Update corresponding details table entry based on widget type
        if request.widget_type in ["todo-habit", "todo-task", "todo-event"]:
            from models.database import ToDoDetails
            todo_details = db.query(ToDoDetails).filter(
                ToDoDetails.widget_id == widget_id
            ).first()
            
            if todo_details:
                todo_type = request.todo_type or request.widget_type.replace("todo-", "")
                todo_details.title = request.title
                todo_details.todo_type = todo_type
                # Convert string date to Python date object
                if request.due_date:
                    todo_details.due_date = datetime.strptime(request.due_date, '%Y-%m-%d').date()
                todo_details.updated_at = datetime.now(timezone.utc)
            else:
                # Create new todo details if they don't exist
                todo_type = request.todo_type or request.widget_type.replace("todo-", "")
                due_date = None
                if request.due_date:
                    due_date = datetime.strptime(request.due_date, '%Y-%m-%d').date()
                todo_details = ToDoDetails(
                    widget_id=widget_id,
                    title=request.title,
                    todo_type=todo_type,
                    due_date=due_date,
                    created_by=user_id
                )
                db.add(todo_details)
                
        elif request.widget_type == "singleitemtracker":
            from models.database import SingleItemTrackerDetails
            tracker_details = db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.widget_id == widget_id
            ).first()
            
            if tracker_details:
                tracker_details.title = request.title
                tracker_details.value_type = request.value_data_type or "number"
                tracker_details.value_unit = request.value_data_unit or "units"
                tracker_details.target_value = request.target_value or "0"
                tracker_details.updated_at = datetime.utcnow()
            else:
                # Create new tracker details if they don't exist
                tracker_details = SingleItemTrackerDetails(
                    widget_id=widget_id,
                    title=request.title,
                    value_type=request.value_data_type or "number",
                    value_unit=request.value_data_unit or "units",
                    target_value=request.target_value or "0",
                    created_by=user_id
                )
                db.add(tracker_details)
                
        elif request.widget_type == "websearch":
            from models.database import WebSearchDetails
            websearch_details = db.query(WebSearchDetails).filter(
                WebSearchDetails.widget_id == widget_id
            ).first()
            
            if websearch_details:
                websearch_details.title = request.title
                websearch_details.updated_at = datetime.utcnow()
            else:
                # Create new websearch details if they don't exist
                websearch_details = WebSearchDetails(
                    widget_id=widget_id,
                    title=request.title,
                    created_by=user_id
                )
                db.add(websearch_details)
                
        elif request.widget_type == "alarm":
            from models.database import AlarmDetails
            alarm_details = db.query(AlarmDetails).filter(
                AlarmDetails.widget_id == widget_id
            ).first()
            
            if alarm_details:
                alarm_details.title = request.title
                alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
                alarm_details.alarm_times = alarm_times
                alarm_details.updated_at = datetime.utcnow()
            else:
                # Create new alarm details if they don't exist
                alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
                alarm_details = AlarmDetails(
                    widget_id=widget_id,
                    title=request.title,
                    alarm_times=alarm_times,
                    created_by=user_id
                )
                db.add(alarm_details)
        
        db.commit()
        
        return {
            "message": "Widget updated successfully",
            "widget_id": widget.id,
            "widget_type": widget.widget_type,
            "title": widget.title
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update widget {widget_id} for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
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