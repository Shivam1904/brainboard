"""
Chat request and response schemas.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict

# ============================================================================
# CHAT SCHEMAS
# ============================================================================
class ChatRequest(BaseModel):
    """Request schema for chat messages."""
    
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for continuing conversation")
    user_id: str = Field(..., description="User identifier")
    
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    """Response schema for chat messages."""
    
    message: str = Field(..., description="AI assistant's response")
    session_id: str = Field(..., description="Session ID for conversation tracking")
    is_complete: bool = Field(..., description="Whether the conversation is complete")
    intent: Optional[str] = Field(None, description="Recognized intent")
    missing_parameters: Optional[List[str]] = Field(None, description="Missing parameters")
    created_resource: Optional[Dict[str, Any]] = Field(None, description="Created resource data")
    success: Optional[bool] = Field(None, description="Whether the operation was successful")
    fallback_attempt: Optional[int] = Field(None, description="Current fallback attempt number")
    error: Optional[str] = Field(None, description="Error message if any")
    
    model_config = ConfigDict(from_attributes=True)

class SessionInfo(BaseModel):
    """Session information for debugging."""
    
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    current_intent: Optional[str] = Field(None, description="Current conversation intent")
    filled_params: Dict[str, Any] = Field(default_factory=dict, description="Filled parameters")
    pending_params: List[str] = Field(default_factory=list, description="Pending parameters")
    fallback_attempts: int = Field(..., description="Number of fallback attempts")
    created_at: str = Field(..., description="Session creation time")
    updated_at: str = Field(..., description="Last update time")
    is_expired: bool = Field(..., description="Whether session has expired")
    conversation_history_count: int = Field(..., description="Number of messages in history")
    
    model_config = ConfigDict(from_attributes=True)

class ChatSessionList(BaseModel):
    """List of active chat sessions."""
    
    sessions: Dict[str, SessionInfo] = Field(..., description="Active sessions")
    total_count: int = Field(..., description="Total number of active sessions")
    
    model_config = ConfigDict(from_attributes=True) 