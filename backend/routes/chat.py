"""
Chat routes for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from schemas.chat import ChatRequest, ChatResponse, SessionInfo, ChatSessionList
from orchestrators.chat_orchestrator import ChatOrchestrator
from services.session_service import SessionService
from db.session import get_session

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# ============================================================================
# ROUTES
# ============================================================================
@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session)
) -> ChatResponse:
    """
    Process a chat message and return AI response.
    
    This endpoint handles natural language conversation for alarm management.
    It supports multi-turn conversations with session memory and fallback mechanisms.
    """
    try:
        # Initialize chat orchestrator
        orchestrator = ChatOrchestrator(db)
        
        # Process the message
        result = await orchestrator.process_message(
            user_message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Convert to response model
        return ChatResponse(
            message=result["message"],
            session_id=result["session_id"],
            is_complete=result["is_complete"],
            intent=result.get("intent"),
            missing_parameters=result.get("missing_parameters"),
            created_resource=result.get("created_resource"),
            success=result.get("success"),
            fallback_attempt=result.get("fallback_attempt"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/sessions", response_model=ChatSessionList)
async def list_sessions() -> ChatSessionList:
    """
    List all active chat sessions.
    
    This endpoint is useful for debugging and monitoring active conversations.
    """
    try:
        session_service = SessionService()
        sessions_info = session_service.get_all_sessions()
        total_count = session_service.get_session_count()
        
        # Convert to response model
        sessions = {}
        for session_id, info in sessions_info.items():
            if info:  # Skip None values
                sessions[session_id] = SessionInfo(**info)
        
        return ChatSessionList(
            sessions=sessions,
            total_count=total_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str) -> SessionInfo:
    """
    Get information about a specific chat session.
    
    This endpoint provides detailed information about a conversation session.
    """
    try:
        session_service = SessionService()
        session_info = session_service.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return SessionInfo(**session_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting session: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str) -> Dict[str, Any]:
    """
    Clear a specific chat session.
    
    This endpoint allows manual cleanup of conversation sessions.
    """
    try:
        session_service = SessionService()
        success = session_service.clear_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "message": f"Session {session_id} cleared successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
        )

@router.post("/cleanup")
async def cleanup_sessions() -> Dict[str, Any]:
    """
    Clean up expired sessions.
    
    This endpoint manually triggers cleanup of expired conversation sessions.
    """
    try:
        session_service = SessionService()
        cleaned_count = session_service.cleanup_expired_sessions()
        
        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cleaning up sessions: {str(e)}"
        ) 