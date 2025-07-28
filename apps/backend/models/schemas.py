from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# Web Summary Widget Schemas
# ============================================================================

class CreateWidgetRequest(BaseModel):
    """Request model for creating a web summary widget"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for the widget")

class GenerateSummaryRequest(BaseModel):
    """Request model for generating a new summary"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for summary generation")

class SummaryResponse(BaseModel):
    """Response model for summary data (matches frontend expectations)"""
    id: str = Field(..., description="Summary ID")
    query: str = Field(..., description="Search query used")
    summary: str = Field(..., description="Generated summary text")
    sources: List[str] = Field(default_factory=list, description="List of source URLs")
    createdAt: str = Field(..., description="ISO timestamp when summary was created")

class CreateWidgetResponse(BaseModel):
    """Response model for widget creation"""
    widget_id: str = Field(..., description="Unique widget identifier")
    user_id: str = Field(..., description="User identifier")
    summary: SummaryResponse = Field(..., description="First summary generated for the widget")
    widget_created_at: str = Field(..., description="ISO timestamp when widget was created")

class WidgetInfo(BaseModel):
    """Complete widget information"""
    widget_id: str
    user_id: str
    widget_type: str
    current_query: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    latest_summary: Optional[SummaryResponse] = None
    created_at: str
    updated_at: str

class UpdateWidgetSettingsRequest(BaseModel):
    """Request model for updating widget settings"""
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    update_frequency: Optional[str] = Field(None, description="How often to update (manual, daily, etc.)")
    max_results: Optional[int] = Field(None, ge=1, le=20, description="Maximum search results to process")

class SummaryHistoryResponse(BaseModel):
    """Response model for summary history"""
    widget_id: str
    summaries: List[SummaryResponse]
    total: int
    has_more: bool

# ============================================================================
# Error Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response format"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")

# ============================================================================
# Base Models for Future Extensions
# ============================================================================

class WidgetBase(BaseModel):
    """Base widget model for future widget types"""
    widget_type: str = Field(..., description="Type of widget (web-summary, reminders, etc.)")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Widget-specific settings")

class CreateWidgetBase(WidgetBase):
    """Base model for creating any widget type"""
    pass

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
