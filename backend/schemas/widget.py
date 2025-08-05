"""
Widget schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================
class WidgetType(str, Enum):
    ALARM = "alarm"
    TODO_HABIT = "todo-habit"
    TODO_TASK = "todo-task"
    TODO_EVENT = "todo-event"
    SINGLEITEMTRACKER = "singleitemtracker"
    WEBSEARCH = "websearch"
    AI_CHAT = "aiChat"
    CALENDAR = "calendar"

class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================
class CreateWidgetRequest(BaseModel):
    """Request schema for creating a new dashboard widget"""
    widget_type: WidgetType
    frequency: Frequency
    importance: float = Field(..., ge=0.0, le=1.0)
    title: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    
    # Todo-specific fields
    description: Optional[str] = Field(None, max_length=500, description="Description for todo widgets")
    due_date: Optional[str] = Field(None, description="Due date for todo widgets (YYYY-MM-DD format)")
    
    # Alarm-specific fields
    alarm_time: Optional[str] = Field(None, description="Time of day for alarm (HH:MM format)")
    
    # SingleItemTracker-specific fields
    value_type: Optional[str] = Field(None, description="Type of value to track: number, text, decimal")
    value_unit: Optional[str] = Field(None, description="Unit for tracker values: kg, pages, steps, etc.")
    target_value: Optional[str] = Field(None, description="Target value for tracker")

class UpdateWidgetRequest(BaseModel):
    """Request schema for updating a dashboard widget"""
    frequency: Optional[Frequency] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class WidgetResponse(BaseModel):
    """Response schema for dashboard widget"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_type: str
    frequency: str
    importance: float
    title: str
    category: Optional[str] = None
    is_permanent: bool
    created_at: datetime
    updated_at: datetime

class WidgetTypeResponse(BaseModel):
    """Response schema for widget type information"""
    id: str
    name: str
    description: str
    category: str
    icon: str
    count: int = 0
    config_schema: Dict[str, Any]

class WidgetCategoryResponse(BaseModel):
    """Response schema for widget category information"""
    id: str
    name: str
    description: str
    icon: str

class CreateWidgetResponse(BaseModel):
    """Response schema for widget creation"""
    success: bool
    message: str
    widget_id: Optional[str] = None
    widget_type: Optional[str] = None
    title: Optional[str] = None 