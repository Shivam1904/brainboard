"""
Alarm schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================
class UpdateActivityRequest(BaseModel):
    """Request schema for updating alarm activity."""
    started_at: Optional[datetime] = None
    snoozed_at: Optional[datetime] = None
    snooze_until: Optional[datetime] = None
    snooze_count: Optional[int] = Field(None, ge=0)

class UpdateAlarmDetailsRequest(BaseModel):
    """Request schema for updating alarm details."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    alarm_times: Optional[List[str]] = None
    target_value: Optional[str] = Field(None, max_length=200)
    is_snoozable: Optional[bool] = None

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class AlarmDetailsResponse(BaseModel):
    """Response schema for alarm details."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    alarm_times: List[str]
    is_snoozable: bool
    target_value: Optional[str]
    created_at: datetime
    updated_at: datetime

class AlarmActivityResponse(BaseModel):
    """Response schema for alarm activity."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    alarmdetails_id: str
    started_at: Optional[datetime]
    snoozed_at: Optional[datetime]
    snooze_until: Optional[datetime]
    snooze_count: int
    created_at: datetime
    updated_at: datetime

class AlarmDetailsAndActivityResponse(BaseModel):
    """Response schema for alarm details and activity."""
    alarm_details: Optional[AlarmDetailsResponse]
    activities: List[AlarmActivityResponse] 