"""
Todo Widget Router
API endpoints for todo task management with frequency-based filtering

Special Features:
- Widget-level frequency (daily/weekly/monthly)
- Task-level frequency (daily/weekly/monthly/once)
- Smart task filtering based on both frequencies
- Priority-based task ordering
- Category-based task grouping
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import logging

from core.database import get_db
from models.database_models import TodoTask, DashboardWidget
from models.schemas import (
    CreateTodoTaskRequest, 
    UpdateTodoTaskRequest, 
    TodoTaskResponse,
    TodoWidgetDataResponse,
    TodoWidgetStatsResponse,
    TaskFrequency,
    TaskPriority
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/widgets/todo", tags=["todo"])

def _should_show_task_today(task: TodoTask, target_date: date = None) -> bool:
    """
    Determine if a task should appear today based on its frequency
    
    Logic:
    - 'daily': Show every day
    - 'weekly': Show once per week (every 7 days from creation)
    - 'monthly': Show once per month (every 30 days from creation)
    - 'once': Show only if not completed or if due date is today/past
    """
    if target_date is None:
        target_date = date.today()
    
    # For one-time tasks
    if task.frequency == TaskFrequency.ONCE:
        # Show if not done, or if due date is today/overdue
        if not task.is_done:
            if task.due_date is None:
                return True
            return task.due_date <= target_date
        return False
    
    # For recurring tasks
    if not task.is_recurring:
        return not task.is_done
    
    # Daily tasks always show (unless completed today)
    if task.frequency == TaskFrequency.DAILY:
        if task.last_completed_date == target_date:
            return False  # Already completed today
        return True
    
    # Weekly tasks - show every 7 days
    if task.frequency == TaskFrequency.WEEKLY:
        days_since_creation = (target_date - task.created_at.date()).days
        if task.last_completed_date:
            days_since_completion = (target_date - task.last_completed_date).days
            return days_since_completion >= 7
        return days_since_creation % 7 == 0
    
    # Monthly tasks - show every 30 days
    if task.frequency == TaskFrequency.MONTHLY:
        days_since_creation = (target_date - task.created_at.date()).days
        if task.last_completed_date:
            days_since_completion = (target_date - task.last_completed_date).days
            return days_since_completion >= 30
        return days_since_creation % 30 == 0
    
    return True

@router.post("/tasks", response_model=TodoTaskResponse)
async def create_task(
    task_data: CreateTodoTaskRequest,
    db: Session = Depends(get_db)
):
    """Create a new todo task with frequency settings"""
    try:
        # Verify widget exists and is a todo widget
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == task_data.dashboard_widget_id,
            DashboardWidget.widget_type == "todo"
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=404,
                detail="Todo widget not found"
            )
        
        # Create task with enhanced fields
        task = TodoTask(
            dashboard_widget_id=task_data.dashboard_widget_id,
            content=task_data.content,
            due_date=task_data.due_date,
            frequency=task_data.frequency,
            priority=task_data.priority or TaskPriority.MEDIUM,
            category=task_data.category,
            is_done=False,
            is_recurring=task_data.is_recurring
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"Created todo task: {task.id} with frequency: {task.frequency}")
        return TodoTaskResponse.from_orm(task)
        
    except Exception as e:
        logger.error(f"Error creating todo task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/today", response_model=TodoWidgetDataResponse)
async def get_today_tasks(
    widget_id: str,
    target_date: Optional[date] = Query(None, description="Target date (defaults to today)"),
    db: Session = Depends(get_db)
):
    """
    Get today's tasks for a todo widget with smart frequency filtering
    
    Returns tasks that should appear today based on:
    1. Widget frequency (from dashboard settings)
    2. Task frequency (individual task settings)
    3. Completion status and recurrence rules
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        # Verify widget exists
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.widget_type == "todo"
        ).first()
        
        if not widget:
            raise HTTPException(status_code=404, detail="Todo widget not found")
        
        # Get all tasks for this widget
        all_tasks = db.query(TodoTask).filter(
            TodoTask.dashboard_widget_id == widget_id
        ).all()
        
        # Filter tasks based on frequency logic
        today_tasks = []
        for task in all_tasks:
            if _should_show_task_today(task, target_date):
                today_tasks.append(task)
        
        # Sort by priority (high to low), then by due date, then by creation time
        today_tasks.sort(key=lambda t: (
            -(t.priority or 3),  # Higher priority first
            t.due_date or date.max,  # Earlier due dates first
            t.created_at
        ))
        
        # Generate statistics
        total_tasks = len(today_tasks)
        completed_tasks = sum(1 for task in today_tasks if task.is_done)
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Group by priority
        tasks_by_priority = {}
        for priority in [1, 2, 3, 4, 5]:
            tasks_by_priority[str(priority)] = sum(1 for t in today_tasks if (t.priority or 3) == priority)
        
        # Group by category
        tasks_by_category = {}
        for task in today_tasks:
            category = task.category or "uncategorized"
            tasks_by_category[category] = tasks_by_category.get(category, 0) + 1
        
        stats = TodoWidgetStatsResponse(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            completion_rate=completion_rate,
            tasks_by_priority=tasks_by_priority,
            tasks_by_category=tasks_by_category
        )
        
        task_responses = [TodoTaskResponse.from_orm(task) for task in today_tasks]
        
        return TodoWidgetDataResponse(
            widget_id=widget_id,
            date=target_date,
            tasks=task_responses,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting today's tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/all", response_model=List[TodoTaskResponse])
async def get_all_tasks(
    widget_id: str,
    include_completed: bool = Query(False, description="Include completed tasks"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[int] = Query(None, description="Filter by priority (1-5)"),
    db: Session = Depends(get_db)
):
    """Get all tasks for a widget with optional filtering"""
    try:
        query = db.query(TodoTask).filter(TodoTask.dashboard_widget_id == widget_id)
        
        if not include_completed:
            query = query.filter(TodoTask.is_done == False)
        
        if category:
            query = query.filter(TodoTask.category == category)
        
        if priority:
            query = query.filter(TodoTask.priority == priority)
        
        tasks = query.order_by(
            TodoTask.priority.desc(),
            TodoTask.due_date,
            TodoTask.created_at
        ).all()
        
        return [TodoTaskResponse.from_orm(task) for task in tasks]
        
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}", response_model=TodoTaskResponse)
async def update_task(
    task_id: str,
    update_data: UpdateTodoTaskRequest,
    db: Session = Depends(get_db)
):
    """Update a todo task"""
    try:
        task = db.query(TodoTask).filter(TodoTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields if provided
        if update_data.content is not None:
            task.content = update_data.content
        if update_data.due_date is not None:
            task.due_date = update_data.due_date
        if update_data.frequency is not None:
            task.frequency = update_data.frequency
        if update_data.priority is not None:
            task.priority = update_data.priority
        if update_data.category is not None:
            task.category = update_data.category
        if update_data.is_recurring is not None:
            task.is_recurring = update_data.is_recurring
        
        # Handle completion status change
        if update_data.is_done is not None:
            old_status = task.is_done
            task.is_done = update_data.is_done
            
            # If marking as complete, update last_completed_date
            if not old_status and update_data.is_done:
                task.last_completed_date = date.today()
                logger.info(f"Task {task_id} marked complete on {date.today()}")
        
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return TodoTaskResponse.from_orm(task)
        
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    is_done: bool,
    db: Session = Depends(get_db)
):
    """Quick endpoint to toggle task completion status"""
    try:
        task = db.query(TodoTask).filter(TodoTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        old_status = task.is_done
        task.is_done = is_done
        
        # Update completion tracking
        if not old_status and is_done:
            task.last_completed_date = date.today()
        elif old_status and not is_done:
            # If unchecking, you might want to clear last_completed_date
            # or leave it for tracking purposes
            pass
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        
        return {
            "id": task.id,
            "content": task.content,
            "is_done": task.is_done,
            "last_completed_date": task.last_completed_date.isoformat() if task.last_completed_date else None,
            "updated_at": task.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Delete a todo task"""
    try:
        task = db.query(TodoTask).filter(TodoTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
        
        return {"message": f"Task {task_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TodoTaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific todo task"""
    try:
        task = db.query(TodoTask).filter(TodoTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TodoTaskResponse.from_orm(task)
        
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
