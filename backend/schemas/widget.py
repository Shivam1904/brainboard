"""
Widget schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class WidgetResponse(BaseModel):
    """Response schema for user widgets."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_type: str
    title: str
    category: str
    frequency: str
    importance: float
    is_permanent: bool
    created_at: datetime
    updated_at: datetime

class WidgetTypeResponse(BaseModel):
    """Response schema for widget types."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: str
    category: str
    icon: str
    count: int
    config_schema: Dict[str, Any]

class WidgetCategoryResponse(BaseModel):
    """Response schema for widget categories."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: str
    icon: str 