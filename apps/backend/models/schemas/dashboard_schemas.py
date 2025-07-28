from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base_schemas import WidgetType, FrequencyType, WidgetSize

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
    widget_type: str
    title: str
    size: WidgetSize = WidgetSize.MEDIUM
    data: Dict[str, Any] = Field(default_factory=dict)

class DashboardTodayResponse(BaseModel):
    """Response schema for today's dashboard"""
    date: date
    widgets: List[WidgetDataResponse]
    stats: Dict[str, Any] = Field(default_factory=dict)

class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics"""
    total_widgets: int
    active_widgets: int
    widgets_by_type: Dict[str, int]
    widgets_by_frequency: Dict[str, int]
