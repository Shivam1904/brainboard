"""
Todo Widget Router
4 Core API endpoints for todo item management (Task/Event/Habit)

Endpoints:
- POST /items - Create Task/Event/Habit
- GET /items/{item_id} - Get Item
- POST /items/{item_id} - Update Item Value/Status
- DELETE /items/{item_id} - Delete Item

Examples:
- India Shopping | Task | daily | health | High
- Gym | Habit | weekly-2 | health | Low | [7am]
- Drink Water | Habit | daily-8 | health | High | [every 2 hr]
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import logging
import json

from core.database import get_db
from models.database_models import TodoItem, DashboardWidget
from models.schemas.todo_schemas import (
    CreateTodoItemRequest,
    UpdateTodoItemRequest,
    TodoItemResponse,
    TodoItemType,
    TodoPriority
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["todo"])

# ============================================================================
# TODO ITEM API - 4 Core Endpoints Only
# ============================================================================

@router.post("/items", response_model=TodoItemResponse)
async def create_todo_item(
    request: CreateTodoItemRequest,
    db: Session = Depends(get_db)
):
    """Create a new todo item (Task, Event, or Habit)"""
    try:
        # Verify widget exists
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == request.dashboard_widget_id
        ).first()
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard widget not found"
            )
        
        # Create new todo item
        todo_item = TodoItem(
            dashboard_widget_id=request.dashboard_widget_id,
            title=request.title,
            item_type=request.item_type.value,
            category=request.category,
            priority=request.priority.value,
            frequency=request.frequency,
            frequency_times=json.dumps(request.frequency_times) if request.frequency_times else None,
            due_date=request.due_date,
            scheduled_time=request.scheduled_time,
            notes=request.notes,
            is_completed=False,
            is_active=True
        )
        
        db.add(todo_item)
        db.commit()
        db.refresh(todo_item)
        
        logger.info(f"Created {request.item_type} todo item: {todo_item.id}")
        return _format_todo_item_response(todo_item)
        
    except Exception as e:
        logger.error(f"Error creating todo item: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo item"
        )

@router.get("/items/{item_id}", response_model=TodoItemResponse)
async def get_todo_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific todo item"""
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found"
        )
    
    return _format_todo_item_response(item)

@router.post("/items/{item_id}", response_model=TodoItemResponse)
async def update_todo_item_status(
    item_id: str,
    completed: Optional[bool] = Query(None, description="Mark as completed or not"),
    active: Optional[bool] = Query(None, description="Mark as active or not"),
    db: Session = Depends(get_db)
):
    """Update todo item status (completion/active state)"""
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found"
        )
    
    updated = False
    
    if completed is not None:
        item.is_completed = completed
        if completed:
            item.last_completed_date = date.today()
        updated = True
    
    if active is not None:
        item.is_active = active
        updated = True
    
    if updated:
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        
        status_msg = []
        if completed is not None:
            status_msg.append("completed" if completed else "incomplete")
        if active is not None:
            status_msg.append("active" if active else "inactive")
        
        logger.info(f"Todo item {item_id} marked as {', '.join(status_msg)}")
    
    return _format_todo_item_response(item)

@router.delete("/items/{item_id}")
async def delete_todo_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    """Delete a todo item"""
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found"
        )
    
    db.delete(item)
    db.commit()
    
    logger.info(f"Deleted todo item: {item_id}")
    return {"message": "Todo item deleted successfully"}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_todo_item_response(item: TodoItem) -> TodoItemResponse:
    """Format TodoItem for API response"""
    frequency_times = None
    if item.frequency_times:
        try:
            frequency_times = json.loads(item.frequency_times)
        except (json.JSONDecodeError, TypeError):
            frequency_times = None
    
    return TodoItemResponse(
        id=item.id,
        dashboard_widget_id=item.dashboard_widget_id,
        title=item.title,
        item_type=TodoItemType(item.item_type),
        category=item.category,
        priority=TodoPriority(item.priority),
        frequency=item.frequency,
        frequency_times=frequency_times,
        is_completed=item.is_completed,
        is_active=item.is_active,
        due_date=item.due_date,
        scheduled_time=item.scheduled_time,
        last_completed_date=item.last_completed_date,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at
    )