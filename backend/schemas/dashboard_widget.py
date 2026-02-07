"""
Dashboard Widget Schemas - Consolidated schemas for all widget types.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class DashboardWidgetBase(BaseModel):
    """Base schema for dashboard widgets."""
    widget_type: str = Field(..., description="Type of widget: 'alarm', 'todo', 'single_item_tracker', 'websearch'")
    frequency: str = Field(default="daily", description="Frequency: 'daily', 'weekly', 'monthly'")
    frequency_details: Optional[Dict[str, Any]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance on 0.0 to 1.0 scale")
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: bool = Field(default=False, description="If True, widget is automatically included in daily plans")


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema for creating a dashboard widget."""
    widget_config: Dict[str, Any] = Field(default_factory=dict, description="Widget-specific configuration")


class DashboardWidgetUpdate(BaseModel):
    """Schema for updating a dashboard widget."""
    widget_type: Optional[str] = None  # Included for compatibility but won't be updated
    frequency: Optional[str] = None
    frequency_details: Optional[Dict[str, Any]] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: Optional[bool] = None
    widget_config: Optional[Dict[str, Any]] = None


class WidgetPriorityResponse(BaseModel):
    """Response for widget priority for a given date (past performance / importance)."""
    priority: str = Field(..., description="One of: critical, medium, low")
    reason: str = Field(..., description="Short explanation for the priority")


class DashboardWidgetResponse(DashboardWidgetBase):
    """Schema for dashboard widget response."""
    id: str
    widget_config: Dict[str, Any]
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    delete_flag: bool = False

    class Config:
        from_attributes = True


# Widget-specific creation schemas
class AlarmWidgetCreate(BaseModel):
    """Schema for creating an alarm widget."""
    frequency: str = Field(default="daily")
    frequency_details: Optional[Dict[str, Any]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    title: str = Field(default="Alarm")
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: bool = Field(default=False)
    
    # Alarm-specific configuration
    alarm_times: List[str] = Field(default_factory=list, description="List of alarm times in HH:MM format")
    target_value: Optional[str] = None
    is_snoozable: bool = Field(default=True)


class TodoWidgetCreate(BaseModel):
    """Schema for creating a todo widget."""
    frequency: str = Field(default="daily")
    frequency_details: Optional[Dict[str, Any]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    title: str = Field(default="Todo")
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: bool = Field(default=False)
    
    # Todo-specific configuration
    todo_type: str = Field(default="todo-habit", description="Type: 'todo-habit', 'todo-task', 'todo-event'")
    due_date: Optional[str] = None


class TrackerWidgetCreate(BaseModel):
    """Schema for creating a single item tracker widget."""
    frequency: str = Field(default="daily")
    frequency_details: Optional[Dict[str, Any]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    title: str = Field(default="Tracker")
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: bool = Field(default=False)
    
    # Tracker-specific configuration
    value_type: str = Field(default="number", description="Type of value: 'number', 'text', etc.")
    value_unit: Optional[str] = None
    target_value: Optional[str] = None


class WebSearchWidgetCreate(BaseModel):
    """Schema for creating a websearch widget."""
    frequency: str = Field(default="daily")
    frequency_details: Optional[Dict[str, Any]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    title: str = Field(default="Web Search")
    description: Optional[str] = None
    category: Optional[str] = None
    is_permanent: bool = Field(default=False)
    
    # WebSearch-specific configuration
    search_query: str
    frequency: str = Field(default="daily", description="Search frequency")


# Activity data schemas
class ActivityData(BaseModel):
    """Base schema for activity data."""
    pass


class AlarmActivityData(ActivityData):
    """Schema for alarm activity data."""
    started_at: Optional[str] = None
    snoozed_at: Optional[str] = None
    snooze_until: Optional[str] = None
    snooze_count: int = Field(default=0)


class TodoActivityData(ActivityData):
    """Schema for todo activity data."""
    status: str = Field(default="not_started", description="Status: 'not_started', 'in_progress', 'completed'")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    started_at: Optional[str] = None


class TrackerActivityData(ActivityData):
    """Schema for single item tracker activity data."""
    value: str = Field(default="0")
    time_added: Optional[str] = None
    notes: Optional[str] = None


class WebSearchActivityData(ActivityData):
    """Schema for websearch activity data."""
    status: str = Field(default="pending", description="Status: 'pending', 'completed'")
    reaction: Optional[str] = None
    summary: Optional[str] = None
    source_json: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None 