"""
AI schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import date

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class DailyPlanRequest(BaseModel):
    """Request schema for daily plan generation."""
    target_date: Optional[date] = Field(None, description="Date for plan generation (defaults to today)")
    user_id: Optional[str] = Field(None, description="User ID (defaults to authenticated user)")

class WebSummaryRequest(BaseModel):
    """Request schema for web summary generation."""
    target_date: Optional[date] = Field(None, description="Date for summary generation (defaults to today)")
    user_id: Optional[str] = Field(None, description="User ID (defaults to authenticated user)")

class ActivityGenerationRequest(BaseModel):
    """Request schema for activity generation from AI plan."""
    target_date: Optional[date] = Field(None, description="Date for activity generation (defaults to today)")
    user_id: Optional[str] = Field(None, description="User ID (defaults to authenticated user)")

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DailyPlanResponse(BaseModel):
    """Response schema for daily plan generation."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Plan generation data")
    target_date: str = Field(..., description="Target date in ISO format")

class WebSummaryResponse(BaseModel):
    """Response schema for web summary generation."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Summary generation data")
    target_date: str = Field(..., description="Target date in ISO format")

class ActivityGenerationResponse(BaseModel):
    """Response schema for activity generation."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Activity generation data")
    target_date: str = Field(..., description="Target date in ISO format")

# ============================================================================
# DETAILED DATA SCHEMAS
# ============================================================================

class WidgetInfo(BaseModel):
    """Schema for widget information in AI context."""
    id: str = Field(..., description="Widget ID")
    title: str = Field(..., description="Widget title")
    widget_type: str = Field(..., description="Type of widget")
    importance: float = Field(..., description="Widget importance score")
    frequency: str = Field(..., description="Widget frequency")
    category: str = Field(..., description="Widget category")

class AIPlanItem(BaseModel):
    """Schema for individual AI plan item."""
    widget_id: str = Field(..., description="Widget ID")
    selected: bool = Field(..., description="Whether widget is selected for today")
    priority: str = Field(..., description="Priority level (HIGH, MEDIUM, LOW)")
    reasoning: str = Field(..., description="AI reasoning for selection")

class AIOutputMetadata(BaseModel):
    """Schema for AI output metadata."""
    ai_model_used: Optional[str] = Field(None, description="AI model used")
    ai_prompt_used: Optional[str] = Field(None, description="Prompt sent to AI")
    ai_response_time: Optional[str] = Field(None, description="Time taken for AI response")
    confidence_score: Optional[str] = Field(None, description="AI confidence score")
    generation_type: str = Field(..., description="Generation type (ai_generated or fallback)")

class DailyPlanData(BaseModel):
    """Schema for daily plan generation data."""
    message: str = Field(..., description="Success message")
    date: str = Field(..., description="Target date")
    widgets_processed: int = Field(..., description="Total widgets processed")
    permanent_widgets_added: int = Field(..., description="Permanent widgets added")
    ai_widgets_processed: int = Field(..., description="AI-processed widgets")

class WebSummaryData(BaseModel):
    """Schema for web summary generation data."""
    message: str = Field(..., description="Success message")
    date: str = Field(..., description="Target date")
    summaries_generated: int = Field(..., description="Number of summaries generated")

class ActivityGenerationData(BaseModel):
    """Schema for activity generation data."""
    message: str = Field(..., description="Success message")
    date: str = Field(..., description="Target date")
    activities_created: int = Field(..., description="Number of activities created")

# ============================================================================
# TOOL SCHEMAS
# ============================================================================

class ToolResponse(BaseModel):
    """Schema for tool responses."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")
    target_date: Optional[str] = Field(None, description="Target date in ISO format")

# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class AIErrorResponse(BaseModel):
    """Schema for AI operation errors."""
    status: str = Field("error", description="Error status")
    message: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

# New AI Service Schemas
class NewAIChatRequest(BaseModel):
    """Request schema for new AI chat."""
    user_message: str
    user_tasks: List[str]
    todays_date: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class NewAIChatResponse(BaseModel):
    """Response schema for new AI chat."""
    success: bool
    message: str
    intent: str
    should_continue_chat: bool
    response_type: str
    widget_data: Optional[Dict[str, Any]] = None
    missing_fields: Optional[List[str]] = None 