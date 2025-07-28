from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================================
# TODO WIDGET SCHEMAS
# ============================================================================

class TaskFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONCE = "once"

class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM_LOW = 2
    MEDIUM = 3
    MEDIUM_HIGH = 4
    HIGH = 5

class CreateTodoTaskRequest(BaseModel):
    """Request schema for creating a todo task"""
    dashboard_widget_id: str
    content: str = Field(..., min_length=1, max_length=500)
    due_date: Optional[date] = None
    frequency: TaskFrequency = TaskFrequency.DAILY
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    category: Optional[str] = Field(None, max_length=50)
    is_recurring: bool = True

class UpdateTodoTaskRequest(BaseModel):
    """Request schema for updating a todo task"""
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    due_date: Optional[date] = None
    frequency: Optional[TaskFrequency] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = Field(None, max_length=50)
    is_done: Optional[bool] = None
    is_recurring: Optional[bool] = None

class TodoTaskResponse(BaseModel):
    """Response schema for todo task"""
    id: str
    dashboard_widget_id: str
    content: str
    due_date: Optional[date] = None
    frequency: TaskFrequency
    priority: Optional[int] = None
    category: Optional[str] = None
    is_done: bool
    is_recurring: bool
    last_completed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TodoWidgetStatsResponse(BaseModel):
    """Statistics for todo widget"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    tasks_by_priority: Dict[str, int]
    tasks_by_category: Dict[str, int]
    
class TodoWidgetDataResponse(BaseModel):
    """Complete todo widget data response"""
    widget_id: str
    date: date
    tasks: List[TodoTaskResponse]
    stats: TodoWidgetStatsResponse
