from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================================
# NEW TODO ITEM SCHEMAS (Task, Event, Habit)
# ============================================================================

class TodoItemType(str, Enum):
    TASK = "task"
    EVENT = "event"
    HABIT = "habit"

class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CreateTodoItemRequest(BaseModel):
    """Request schema for creating a todo item (Task/Event/Habit)"""
    dashboard_widget_id: str
    title: str = Field(..., min_length=1, max_length=200)
    item_type: TodoItemType
    category: Optional[str] = Field(None, max_length=50)
    priority: TodoPriority = TodoPriority.MEDIUM
    
    # Frequency and scheduling
    frequency: Optional[str] = None  # 'daily', 'weekly-2', 'daily-8', etc.
    frequency_times: Optional[List[str]] = None  # ['7am'], ['every 2 hr']
    
    # Dates
    due_date: Optional[date] = None  # For tasks and events
    scheduled_time: Optional[datetime] = None  # For events
    
    # Optional
    notes: Optional[str] = Field(None, max_length=1000)

class UpdateTodoItemRequest(BaseModel):
    """Request schema for updating a todo item"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[TodoPriority] = None
    frequency: Optional[str] = None
    frequency_times: Optional[List[str]] = None
    due_date: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)

class TodoItemResponse(BaseModel):
    """Response schema for todo item"""
    id: str
    dashboard_widget_id: str
    title: str
    item_type: TodoItemType
    category: Optional[str] = None
    priority: TodoPriority
    frequency: Optional[str] = None
    frequency_times: Optional[List[str]] = None
    is_completed: bool
    is_active: bool
    due_date: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    last_completed_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TodoWidgetStatsResponse(BaseModel):
    """Response schema for todo widget statistics"""
    total_items: int
    active_items: int
    completed_today: int
    overdue_items: int
    upcoming_events: int
    active_habits: int
    stats_by_type: Dict[str, int]
    stats_by_priority: Dict[str, int]

# ============================================================================
# LEGACY TODO TASK SCHEMAS (for backward compatibility)
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
    """DEPRECATED: Request schema for creating a todo task"""
    dashboard_widget_id: str
    content: str = Field(..., min_length=1, max_length=500)
    due_date: Optional[date] = None
    frequency: TaskFrequency = TaskFrequency.DAILY
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    category: Optional[str] = Field(None, max_length=50)
    is_recurring: bool = True

class UpdateTodoTaskRequest(BaseModel):
    """DEPRECATED: Request schema for updating a todo task"""
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    due_date: Optional[date] = None
    frequency: Optional[TaskFrequency] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = Field(None, max_length=50)
    is_done: Optional[bool] = None
    is_recurring: Optional[bool] = None

class TodoTaskResponse(BaseModel):
    """DEPRECATED: Response schema for todo task"""
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

class LegacyTodoWidgetStatsResponse(BaseModel):
    """DEPRECATED: Statistics for todo widget (legacy)"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    tasks_by_priority: Dict[str, int]
    tasks_by_category: Dict[str, int]
    
class LegacyTodoWidgetDataResponse(BaseModel):
    """DEPRECATED: Complete todo widget data response (legacy)"""
    widget_id: str
    date: date
    tasks: List[TodoTaskResponse]
    stats: LegacyTodoWidgetStatsResponse

# ============================================================================
# NEW UNIFIED TODO WIDGET RESPONSE SCHEMAS
# ============================================================================

class TodoWidgetDataResponse(BaseModel):
    """Complete todo widget data response (new unified version)"""
    widget_id: str
    date: date
    items: List[TodoItemResponse]  # New unified items
    tasks: List[TodoTaskResponse]  # Legacy tasks for backward compatibility
    stats: TodoWidgetStatsResponse

class BulkTodoActionRequest(BaseModel):
    """Request schema for bulk operations on todo items"""
    item_ids: List[str]
    action: str = Field(..., pattern="^(complete|activate|deactivate|delete)$")

class BulkTodoActionResponse(BaseModel):
    """Response schema for bulk operations"""
    success_count: int
    failed_count: int
    failed_items: List[str]
    message: str

# ============================================================================
# FREQUENCY PATTERN VALIDATION HELPERS
# ============================================================================

class FrequencyPattern:
    """Helper class for validating frequency patterns"""
    
    VALID_PATTERNS = [
        # Daily patterns
        "daily", "daily-2", "daily-3", "daily-4", "daily-6", "daily-8", "daily-12",
        # Weekly patterns  
        "weekly", "weekly-2", "weekly-3", "weekly-4",
        # Monthly patterns
        "monthly", "monthly-2", "monthly-3", "monthly-6",
        # One-time
        "once"
    ]
    
    @classmethod
    def is_valid(cls, frequency: str) -> bool:
        """Validate if frequency pattern is supported"""
        return frequency in cls.VALID_PATTERNS
    
    @classmethod
    def get_description(cls, frequency: str) -> str:
        """Get human-readable description of frequency"""
        if frequency == "daily":
            return "Every day"
        elif frequency.startswith("daily-"):
            hours = frequency.split("-")[1]
            return f"Every {hours} hours"
        elif frequency == "weekly":
            return "Every week"
        elif frequency.startswith("weekly-"):
            weeks = frequency.split("-")[1]
            return f"Every {weeks} weeks"
        elif frequency == "monthly":
            return "Every month"
        elif frequency.startswith("monthly-"):
            months = frequency.split("-")[1]
            return f"Every {months} months"
        elif frequency == "once":
            return "One-time only"
        else:
            return "Unknown frequency"
