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
    SINGLEITEMTRACKER = "singleitemtracker"
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
# BASE RESPONSE MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response format"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")

class SuccessResponse(BaseModel):
    """Standard success response format"""
    message: str
    data: Optional[Dict[str, Any]] = None

# ============================================================================
# USER SCHEMAS
# ============================================================================

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
