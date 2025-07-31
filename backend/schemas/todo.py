"""
TODO schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================
class UpdateActivityRequest(BaseModel):
    """Request schema for updating todo activity."""
    status: Optional[str] = Field(None, pattern="^(in progress|completed|pending)$")
    progress: Optional[int] = Field(None, ge=0, le=100)

class UpdateTodoDetailsRequest(BaseModel):
    """Request schema for updating todo details."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    todo_type: Optional[str] = Field(None, pattern="^(todo-habit|todo-task|todo-event)$")
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class TodoDetailsResponse(BaseModel):
    """Response schema for todo details."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    title: str
    todo_type: str
    description: Optional[str]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

class TodoActivityResponse(BaseModel):
    """Response schema for todo activity."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    daily_widget_id: str
    widget_id: str
    tododetails_id: str
    status: str
    progress: Optional[int]
    created_at: datetime
    updated_at: datetime

class TodoDetailsAndActivityResponse(BaseModel):
    """Response schema for todo details and activity."""
    todo_details: Optional[TodoDetailsResponse]
    activities: List[TodoActivityResponse] 