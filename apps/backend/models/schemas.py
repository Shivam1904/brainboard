from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ReminderBase(BaseModel):
    """Base reminder model"""
    text: str = Field(..., min_length=1, max_length=500)
    due_date: Optional[datetime] = None

class ReminderCreate(ReminderBase):
    """Model for creating reminders"""
    pass

class ReminderUpdate(BaseModel):
    """Model for updating reminders"""
    text: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

class Reminder(ReminderBase):
    """Complete reminder model"""
    id: str
    user_id: str
    completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

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
