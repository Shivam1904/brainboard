"""
WebSearch schemas for request/response validation.
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
    """Request schema for updating websearch activity."""
    status: Optional[str] = Field(None, description="Status: 'pending', 'completed', 'failed'")
    reaction: Optional[str] = Field(None, max_length=1000, description="User reaction to search results")
    summary: Optional[str] = Field(None, max_length=5000, description="AI-generated summary")
    source_json: Optional[Dict[str, Any]] = Field(None, description="Source data as JSON")

class UpdateWebSearchDetailsRequest(BaseModel):
    """Request schema for updating websearch details."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="WebSearch title")

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class WebSearchDetailsResponse(BaseModel):
    """Response schema for websearch details."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_id: str
    title: str
    created_at: datetime
    updated_at: datetime

class WebSearchActivityResponse(BaseModel):
    """Response schema for websearch activity."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    daily_widget_id: str
    widget_id: str
    websearchdetails_id: str
    status: str
    reaction: Optional[str]
    summary: Optional[str]
    source_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class WebSearchDetailsAndActivityResponse(BaseModel):
    """Response schema for websearch details and activity."""
    websearch_details: Optional[WebSearchDetailsResponse]
    activity: Optional[WebSearchActivityResponse]

class WebSearchAISummaryResponse(BaseModel):
    """Response schema for websearch AI summary."""
    model_config = ConfigDict(from_attributes=True)
    
    ai_summary_id: str
    widget_id: str
    query: str
    summary: str
    sources: List[Dict[str, str]]
    search_successful: bool
    results_count: int
    ai_model_used: Optional[str]
    generation_type: str
    created_at: datetime
    updated_at: datetime 