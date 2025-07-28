from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class WidgetType(str, Enum):
    TODO = "todo"
    WEBSEARCH = "websearch" 
    ALARM = "alarm"
    CALENDAR = "calendar"
    HABITTRACKER = "habittracker"
    NOTIFICATIONS = "notifications"
    REMINDER = "reminder"
    SINGLETRACKER = "singletracker"
    THISHOUR = "thishour"

class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class WidgetSize(str, Enum):
    SMALL = "small"      # 8x6
    MEDIUM = "medium"    # 10x8 or 8x10
    LARGE = "large"      # 12x10

# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class DashboardWidgetBase(BaseModel):
    """Base schema for dashboard widgets"""
    title: str = Field(..., min_length=1, max_length=100)
    widget_type: WidgetType
    frequency: FrequencyType
    category: Optional[str] = None
    importance: Optional[int] = Field(None, ge=1, le=5)
    settings: Optional[Dict[str, Any]] = None

class CreateDashboardWidgetRequest(DashboardWidgetBase):
    """Request schema for creating a dashboard widget"""
    pass

class UpdateDashboardWidgetRequest(BaseModel):
    """Request schema for updating a dashboard widget"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[FrequencyType] = None
    category: Optional[str] = None
    importance: Optional[int] = Field(None, ge=1, le=5)
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DashboardWidgetResponse(DashboardWidgetBase):
    """Response schema for dashboard widgets"""
    id: str
    user_id: str
    is_active: bool
    last_shown_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WidgetDataResponse(BaseModel):
    """Schema for widget data (content specific to each widget type)"""
    widget_id: str
    widget_type: WidgetType
    data: Dict[str, Any]  # Widget-specific data structure

class DashboardTodayResponse(BaseModel):
    """Response schema for today's dashboard"""
    date: date
    user_id: str
    widgets: List[Dict[str, Any]]  # Complete widget info + data
    total_widgets: int
    generated_at: datetime

class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics"""
    total_widgets: int
    active_widgets: int
    today_widgets: int
    generated_at: str

# ============================================================================
# WIDGET-SPECIFIC SCHEMAS
# ============================================================================

# Todo Widget Schemas
class TodoTaskBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    due_date: Optional[date] = None

class CreateTodoTaskRequest(TodoTaskBase):
    dashboard_widget_id: str

class UpdateTodoTaskRequest(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    due_date: Optional[date] = None
    is_done: Optional[bool] = None

class TodoTaskResponse(TodoTaskBase):
    id: str
    dashboard_widget_id: str
    is_done: bool
    created_at: datetime

    class Config:
        from_attributes = True

# WebSearch Widget Schemas
class WebSearchQueryBase(BaseModel):
    search_term: str = Field(..., min_length=1, max_length=200)

class CreateWebSearchQueryRequest(WebSearchQueryBase):
    dashboard_widget_id: str

class WebSearchQueryResponse(WebSearchQueryBase):
    id: str
    dashboard_widget_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Alarm Widget Schemas
class AlarmBase(BaseModel):
    next_trigger_time: Optional[datetime] = None

class CreateAlarmRequest(AlarmBase):
    dashboard_widget_id: str

class UpdateAlarmRequest(BaseModel):
    next_trigger_time: Optional[datetime] = None
    is_snoozed: Optional[bool] = None

class AlarmResponse(AlarmBase):
    id: str
    dashboard_widget_id: str
    is_snoozed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Habit Tracker Schemas
class HabitBase(BaseModel):
    streak: int = Field(default=0, ge=0)

class CreateHabitRequest(HabitBase):
    dashboard_widget_id: str

class HabitResponse(HabitBase):
    id: str
    dashboard_widget_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class HabitLogBase(BaseModel):
    date: date
    status: str = Field(..., pattern="^(completed|missed|partial)$")

class CreateHabitLogRequest(HabitLogBase):
    habit_id: str

class HabitLogResponse(HabitLogBase):
    id: str
    habit_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# LEGACY WEB SUMMARY WIDGET SCHEMAS (Keep for backward compatibility)
# ============================================================================

class CreateWidgetRequest(BaseModel):
    """Request model for creating a web summary widget"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for the widget")

class GenerateSummaryRequest(BaseModel):
    """Request model for generating a new summary"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for summary generation")

class SummaryResponse(BaseModel):
    """Response model for summary data (matches frontend expectations)"""
    id: str = Field(..., description="Summary ID")
    query: str = Field(..., description="Search query used")
    summary: str = Field(..., description="Generated summary text")
    sources: List[str] = Field(default_factory=list, description="List of source URLs")
    createdAt: str = Field(..., description="ISO timestamp when summary was created")

class CreateWidgetResponse(BaseModel):
    """Response model for widget creation"""
    widget_id: str = Field(..., description="Unique widget identifier")
    user_id: str = Field(..., description="User identifier")
    summary: SummaryResponse = Field(..., description="First summary generated for the widget")
    widget_created_at: str = Field(..., description="ISO timestamp when widget was created")

class WidgetInfo(BaseModel):
    """Complete widget information"""
    widget_id: str
    user_id: str
    widget_type: str
    current_query: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    latest_summary: Optional[SummaryResponse] = None
    created_at: str
    updated_at: str

class UpdateWidgetSettingsRequest(BaseModel):
    """Request model for updating widget settings"""
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    update_frequency: Optional[str] = Field(None, description="How often to update (manual, daily, etc.)")
    max_results: Optional[int] = Field(None, ge=1, le=20, description="Maximum search results to process")

class SummaryHistoryResponse(BaseModel):
    """Response model for summary history"""
    widget_id: str
    summaries: List[SummaryResponse]
    total: int
    has_more: bool

# ============================================================================
# Error Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response format"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")

# ============================================================================
# Base Models for Future Extensions
# ============================================================================

class WidgetBase(BaseModel):
    """Base widget model for future widget types"""
    widget_type: str = Field(..., description="Type of widget (web-summary, reminders, etc.)")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Widget-specific settings")

class CreateWidgetBase(WidgetBase):
    """Base model for creating any widget type"""
    pass

class SummaryBase(BaseModel):
    """Base summary model"""
    query: str = Field(..., min_length=1, max_length=1000)

class SummaryCreate(SummaryBase):
    """Model for creating summaries"""
    pass

class Summary(SummaryBase):
    """Complete summary model"""
    id: str
    user_id: str
    summary: str
    sources: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Base user model"""
    email: str
    full_name: Optional[str] = None

class User(UserBase):
    """Complete user model"""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
