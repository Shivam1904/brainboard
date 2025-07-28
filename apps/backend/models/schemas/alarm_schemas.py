from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================================
# ALARM SCHEMAS
# ============================================================================

class AlarmType(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class CreateAlarmRequest(BaseModel):
    """Request schema for creating an alarm"""
    dashboard_widget_id: str
    title: str = Field(..., min_length=1, max_length=100)
    alarm_type: AlarmType
    alarm_times: List[str] = Field(..., min_items=1, description="List of times in HH:MM format")
    frequency_value: Optional[int] = Field(None, ge=1, le=60, description="For daily-5, weekly-2, etc.")
    specific_date: Optional[date] = Field(None, description="For one-time alarms")

class UpdateAlarmRequest(BaseModel):
    """Request schema for updating an alarm"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    alarm_type: Optional[AlarmType] = None
    alarm_times: Optional[List[str]] = Field(None, min_items=1)
    frequency_value: Optional[int] = Field(None, ge=1, le=60)
    specific_date: Optional[date] = None
    is_active: Optional[bool] = None

class UpdateAlarmStatusRequest(BaseModel):
    """Request schema for updating alarm status"""
    is_active: Optional[bool] = None
    is_snoozed: Optional[bool] = None
    snooze_minutes: Optional[int] = Field(None, ge=1, le=120, description="Minutes to snooze")

class AlarmResponse(BaseModel):
    """Response schema for alarm"""
    id: str
    dashboard_widget_id: str
    title: str
    alarm_type: str
    alarm_times: List[str]
    frequency_value: Optional[int] = None
    specific_date: Optional[date] = None
    is_active: bool
    is_snoozed: bool
    snooze_until: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    next_trigger_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AlarmWidgetDataResponse(BaseModel):
    """Complete alarm widget data response"""
    widget_id: str
    alarms: List[AlarmResponse]
    stats: Dict[str, Any] = {}  # Can include active count, next alarm, etc.
