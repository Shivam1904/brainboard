"""
Session service for conversation memory management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ai_engine.models.session_memory import SessionMemory

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default session timeout in minutes
DEFAULT_SESSION_TIMEOUT = 30

# ============================================================================
# SESSION SERVICE CLASS
# ============================================================================
class SessionService:
    """Service for managing conversation session memory."""
    
    def __init__(self, session_timeout_minutes: int = DEFAULT_SESSION_TIMEOUT):
        """Initialize the session service."""
        self.session_timeout_minutes = session_timeout_minutes
        self._sessions: Dict[str, SessionMemory] = {}
    
    def get_or_create_session(self, session_id: Optional[str], user_id: str) -> SessionMemory:
        """Get existing session or create a new one."""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            
            # Check if session has expired
            if session.is_expired(self.session_timeout_minutes):
                logger.info(f"Session {session_id} has expired, creating new session")
                del self._sessions[session_id]
            else:
                return session
        
        # Create new session
        session = SessionMemory(user_id=user_id)
        self._sessions[session.session_id] = session
        logger.info(f"Created new session: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get session by ID."""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # Check if session has expired
        if session.is_expired(self.session_timeout_minutes):
            logger.info(f"Session {session_id} has expired")
            del self._sessions[session_id]
            return None
        
        return session
    
    def save_session(self, session: SessionMemory) -> None:
        """Save session to memory."""
        self._sessions[session.session_id] = session
        logger.debug(f"Saved session: {session.session_id}")
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if session.is_expired(self.session_timeout_minutes):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information for debugging."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "current_intent": session.current_intent,
            "filled_params": session.filled_params,
            "pending_params": session.pending_params,
            "fallback_attempts": session.fallback_attempts,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "is_expired": session.is_expired(self.session_timeout_minutes),
            "conversation_history_count": len(session.conversation_history)
        }
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sessions."""
        self.cleanup_expired_sessions()
        
        return {
            session_id: self.get_session_info(session_id)
            for session_id in self._sessions.keys()
        }
    
    def get_session_count(self) -> int:
        """Get count of active sessions."""
        self.cleanup_expired_sessions()
        return len(self._sessions)
    
    def update_session_parameters(self, session_id: str, new_parameters: Dict[str, Any]) -> bool:
        """Update session parameters."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.update_parameters(new_parameters)
        self.save_session(session)
        return True
    
    def set_session_pending_parameters(self, session_id: str, pending_params: list[str]) -> bool:
        """Set pending parameters for session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.set_pending_parameters(pending_params)
        self.save_session(session)
        return True
    
    def increment_fallback_attempts(self, session_id: str) -> bool:
        """Increment fallback attempts for session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.increment_fallback_attempts()
        self.save_session(session)
        return True 