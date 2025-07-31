"""
SingleItemTracker schemas for request/response validation.
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
class ValueType(str, Enum):
    """Value types for SingleItemTracker."""
    NUMBER = "number"
    TEXT = "text"
    DECIMAL = "decimal"

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================
class UpdateActivityRequest(BaseModel):
    """Request schema for updating tracker activity."""
    value: Optional[str] = Field(None, description="Current value")
    time_added: Optional[datetime] = Field(None, description="When value was added")

class UpdateTrackerDetailsRequest(BaseModel):
    title: Optional[str] = Field(None, description="Tracker title")
    value_type: Optional[ValueType] = Field(None, description="Type of value to track")
    value_unit: Optional[str] = Field(None, description="Unit for tracker values")
    target_value: Optional[str] = Field(None, description="Target value for tracker")

class UpdateOrCreateTrackerDetailsRequest(BaseModel):
    widget_id: str = Field(..., description="Widget ID")
    title: str = Field(..., description="Tracker title")
    value_type: ValueType = Field(ValueType.NUMBER, description="Type of value to track")
    value_unit: Optional[str] = Field(None, description="Unit for tracker values")
    target_value: Optional[str] = Field(None, description="Target value for tracker")

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class TrackerDetailsResponse(BaseModel):
    """Response schema for tracker details."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    title: str
    value_type: str
    value_unit: Optional[str]
    target_value: Optional[str]
    created_at: datetime
    updated_at: datetime

class TrackerActivityResponse(BaseModel):
    """Response schema for tracker activity."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    singleitemtrackerdetails_id: str
    value: Optional[str]
    time_added: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class TrackerDetailsAndActivityResponse(BaseModel):
    """Response schema for tracker details and activity."""
    tracker_details: Optional[TrackerDetailsResponse]
    activity: Optional[TrackerActivityResponse] 