from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================================
# SINGLE ITEM TRACKER SCHEMAS
# ============================================================================

class ValueType(str, Enum):
    NUMBER = "number"
    TEXT = "text"
    DECIMAL = "decimal"

class CreateSingleItemTrackerRequest(BaseModel):
    """Request schema for creating a single item tracker"""
    dashboard_widget_id: str
    item_name: str = Field(..., min_length=1, max_length=100)
    item_unit: Optional[str] = Field(None, max_length=20)
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    value_type: ValueType = ValueType.NUMBER

class UpdateSingleItemTrackerRequest(BaseModel):
    """Request schema for updating a single item tracker"""
    item_name: Optional[str] = Field(None, min_length=1, max_length=100)
    item_unit: Optional[str] = Field(None, max_length=20)
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    value_type: Optional[ValueType] = None

class UpdateValueRequest(BaseModel):
    """Request schema for updating tracker value"""
    value: str = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)

class SingleItemTrackerLogResponse(BaseModel):
    """Response schema for tracker log entry"""
    id: str
    value: str
    date: date
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SingleItemTrackerResponse(BaseModel):
    """Response schema for single item tracker"""
    id: str
    dashboard_widget_id: str
    item_name: str
    item_unit: Optional[str] = None
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    value_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SingleItemTrackerWithLogsResponse(BaseModel):
    """Response schema for tracker with recent logs"""
    id: str
    dashboard_widget_id: str
    item_name: str
    item_unit: Optional[str] = None
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    value_type: str
    created_at: datetime
    updated_at: datetime
    recent_logs: List[SingleItemTrackerLogResponse] = []
    
    class Config:
        from_attributes = True

class SingleItemTrackerStatsResponse(BaseModel):
    """Statistics for single item tracker"""
    total_entries: int
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    progress_percentage: Optional[float] = None  # If target is numeric
    last_updated: Optional[date] = None
    streak_days: int = 0  # Days with consecutive entries

class SingleItemTrackerWidgetDataResponse(BaseModel):
    """Complete single item tracker widget data response"""
    widget_id: str
    tracker: SingleItemTrackerResponse
    stats: SingleItemTrackerStatsResponse
    recent_logs: List[SingleItemTrackerLogResponse] = []
