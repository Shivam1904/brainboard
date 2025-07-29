from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class WidgetType(str, Enum):
    TODO_HABIT = "todo-habit"
    TODO_TASK = "todo-task"
    TODO_EVENT = "todo-event"
    ALARM = "alarm"
    SINGLEITEMTRACKER = "singleitemtracker"
    WEBSEARCH = "websearch"

class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Priority(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"

class CreateWidgetRequest(BaseModel):
    """Request schema for creating a new dashboard widget"""
    widget_type: WidgetType
    frequency: Frequency
    importance: float = Field(..., ge=0.0, le=1.0)
    title: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)

class UpdateWidgetRequest(BaseModel):
    """Request schema for updating a dashboard widget"""
    frequency: Optional[Frequency] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)

class WidgetResponse(BaseModel):
    """Response schema for dashboard widget"""
    id: str
    widget_type: WidgetType
    frequency: Frequency
    importance: float
    title: str
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DailyWidgetResponse(BaseModel):
    """Response schema for daily widget"""
    daily_widget_id: str
    widget_ids: List[str]
    widget_type: WidgetType
    priority: Priority
    reasoning: Optional[str] = None
    date: str
    created_at: datetime

    class Config:
        from_attributes = True

class TodayWidgetListResponse(BaseModel):
    """Response schema for today's widget list"""
    date: str
    widgets: List[DailyWidgetResponse]
    total_widgets: int
    ai_generated: bool
    last_updated: str

class AllWidgetListResponse(BaseModel):
    """Response schema for all widget list"""
    widgets: List[WidgetResponse]
    total_widgets: int
