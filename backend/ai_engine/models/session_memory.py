"""
Session memory data structures for conversation state management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid

# ============================================================================
# SESSION MEMORY MODELS
# ============================================================================
class ConversationHistory(BaseModel):
    """Individual conversation message."""
    
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    
    model_config = ConfigDict(from_attributes=True)

class SessionMemory(BaseModel):
    """Session memory for conversation state management."""
    
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    current_intent: Optional[str] = Field(None, description="Current conversation intent")
    filled_params: Dict[str, Any] = Field(default_factory=dict, description="Filled parameters")
    pending_params: List[str] = Field(default_factory=list, description="Still pending parameters")
    original_message: Optional[str] = Field(None, description="Original user message")
    conversation_history: List[ConversationHistory] = Field(default_factory=list, description="Conversation history")
    fallback_attempts: int = Field(default=0, description="Number of fallback attempts made")
    max_fallback_attempts: int = Field(default=3, description="Maximum allowed fallback attempts")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    model_config = ConfigDict(from_attributes=True)
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.updated_at + timedelta(minutes=timeout_minutes)
    
    def can_retry_fallback(self) -> bool:
        """Check if fallback retry is still allowed."""
        return self.fallback_attempts < self.max_fallback_attempts
    
    def increment_fallback_attempts(self) -> None:
        """Increment fallback attempt counter."""
        self.fallback_attempts += 1
        self.updated_at = datetime.now()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        message = ConversationHistory(role=role, content=content)
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """Update filled parameters and remove from pending."""
        for key, value in new_params.items():
            if value is not None:
                self.filled_params[key] = value
                if key in self.pending_params:
                    self.pending_params.remove(key)
        self.updated_at = datetime.now()
    
    def set_pending_parameters(self, params: List[str]) -> None:
        """Set the list of pending parameters."""
        self.pending_params = params
        self.updated_at = datetime.now()
    
    def clear_session(self) -> None:
        """Clear session data for new conversation."""
        self.current_intent = None
        self.filled_params = {}
        self.pending_params = []
        self.original_message = None
        self.fallback_attempts = 0
        self.updated_at = datetime.now() 