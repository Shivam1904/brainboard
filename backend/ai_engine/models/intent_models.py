"""
Intent recognition and parameter extraction response models.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

# ============================================================================
# INTENT RESPONSE MODELS
# ============================================================================
class IntentResponse(BaseModel):
    """Response model for intent recognition."""
    
    intent: str = Field(..., description="Recognized intent (create_alarm, edit_alarm, delete_alarm, list_alarms)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    reasoning: str = Field(..., description="Reasoning for the intent classification")
    is_fallback: bool = Field(default=False, description="Whether this is a fallback response")
    fallback_attempt: int = Field(default=0, description="Current fallback attempt number")
    
    model_config = ConfigDict(from_attributes=True)

class ParameterExtractionResponse(BaseModel):
    """Response model for parameter extraction from follow-up messages."""
    
    updated_parameters: Dict[str, Any] = Field(..., description="Updated parameters from the message")
    missing_parameters: List[str] = Field(default_factory=list, description="Still missing parameters")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in parameter extraction")
    reasoning: str = Field(..., description="Reasoning for parameter extraction")
    
    model_config = ConfigDict(from_attributes=True)

class FallbackResponse(BaseModel):
    """Response model for fallback scenarios."""
    
    message: str = Field(..., description="User-friendly fallback message")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions for user")
    can_retry: bool = Field(default=True, description="Whether the system can retry intent recognition")
    
    model_config = ConfigDict(from_attributes=True) 