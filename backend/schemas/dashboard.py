"""
Dashboard schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class TodayWidgetListResponse(BaseModel):
    """Response schema for today's widget list."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_ids: List[str]
    widget_type: str
    priority: str
    reasoning: Optional[str]
    date: str  # ISO format
    is_active: bool

class AddWidgetToTodayResponse(BaseModel):
    """Response schema for adding widget to today."""
    success: bool
    message: str
    daily_widget_id: Optional[str] = None
    widget_ids: Optional[List[str]] = None

class RemoveWidgetFromTodayResponse(BaseModel):
    """Response schema for removing widget from today."""
    success: bool
    message: str
    daily_widget_id: Optional[str] = None
    remaining_widgets: Optional[List[str]] = None 