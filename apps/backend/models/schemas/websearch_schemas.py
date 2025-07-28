from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# WEBSEARCH WIDGET SCHEMAS
# ============================================================================

class CreateWebSearchQueryRequest(BaseModel):
    """Request schema for creating a web search query"""
    dashboard_widget_id: str
    search_term: str = Field(..., min_length=1, max_length=200)

class WebSearchQueryResponse(BaseModel):
    """Response schema for web search query"""
    id: str
    dashboard_widget_id: str
    search_term: str
    created_at: datetime

    class Config:
        from_attributes = True

class WebSearchWidgetDataResponse(BaseModel):
    """Complete web search widget data response"""
    widget_id: str
    queries: List[WebSearchQueryResponse]
    recent_summaries: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {}

# ============================================================================
# WEB SUMMARY WIDGET SCHEMAS (standalone web summary functionality)
# ============================================================================

class CreateWidgetRequest(BaseModel):
    """Request schema for creating a web summary widget"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for the widget")

class CreateWidgetResponse(BaseModel):
    """Response schema for widget creation"""
    widget_id: str = Field(..., description="Unique widget identifier")
    user_id: str = Field(..., description="User identifier")
    summary: "SummaryResponse" = Field(..., description="First summary generated for the widget")
    widget_created_at: str = Field(..., description="ISO timestamp when widget was created")

class WidgetInfo(BaseModel):
    """Complete widget information"""
    widget_id: str
    user_id: str
    widget_type: str
    current_query: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    latest_summary: Optional["SummaryResponse"] = None
    created_at: str
    updated_at: str

class UpdateWidgetSettingsRequest(BaseModel):
    """Request schema for updating widget settings"""
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    update_frequency: Optional[str] = Field(None, description="How often to update (manual, daily, etc.)")
    max_results: Optional[int] = Field(None, ge=1, le=20, description="Maximum search results to process")

# ============================================================================
# AI SUMMARY SCHEMAS
# ============================================================================

class GenerateSummaryRequest(BaseModel):
    """Request schema for generating an AI summary"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query for summary generation")

class SummaryResponse(BaseModel):
    """Response schema for AI-generated summary"""
    id: str = Field(..., description="Summary ID")
    query: str = Field(..., description="Search query used")
    summary: str = Field(..., description="Generated summary text")
    sources: List[str] = Field(default_factory=list, description="List of source URLs")
    createdAt: str = Field(..., description="ISO timestamp when summary was created")

class SummaryHistoryResponse(BaseModel):
    """Response schema for summary history"""
    widget_id: str
    summaries: List[SummaryResponse]
    total: int

# Fix forward references
CreateWidgetResponse.model_rebuild()
WidgetInfo.model_rebuild()
