"""
Chat routes for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import json
import uuid
import logging
from datetime import datetime

from schemas.chat import ChatRequest, ChatResponse, SessionInfo, ChatSessionList
from orchestrators.chat_orchestrator import ChatOrchestrator
from services.session_service import SessionService
from db.session import get_session, AsyncSessionLocal

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Connection management
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    """Manages WebSocket connections and provides utility methods."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_thinking_step(self, connection_id: str, step: str, details: Optional[str] = None):
        """Send a thinking step update to the client."""
        message = {
            "type": "thinking",
            "step": step,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
    
    async def send_response(self, connection_id: str, response: str, session_id: Optional[str] = None, is_complete: bool = False):
        """Send the final AI response to the client."""
        message = {
            "type": "response",
            "content": response,
            "session_id": session_id,
            "is_complete": is_complete,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
    
    async def send_component(self, connection_id: str, content: str, component: Dict[str, Any], session_id: Optional[str] = None, is_complete: bool = False):
        """Send a component message to the client."""
        message = {
            "type": "component",
            "content": content,
            "component": component,
            "session_id": session_id,
            "is_complete": is_complete,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
    
    async def send_error(self, connection_id: str, error: str):
        """Send an error message to the client."""
        message = {
            "type": "error",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)

# Global connection manager
manager = ConnectionManager()

# ============================================================================
# ROUTES
# ============================================================================

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    connection_id = str(uuid.uuid4())
    
    try:
        # Accept the connection
        await manager.connect(websocket, connection_id)
        
        # Send connection confirmation
        await manager.send_message(connection_id, {
            "type": "connection",
            "connection_id": connection_id,
            "message": "Connected to Brainboard Chat",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Initialize chat orchestrator
        db_session = AsyncSessionLocal()
        orchestrator = ChatOrchestrator(db_session)
        
        # Default user ID for development (you can modify this later)
        user_id = "user_001"
        current_session_id = None
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                user_message = message_data.get("message", "")
                session_id = message_data.get("session_id")
                
                if not user_message.strip():
                    await manager.send_error(connection_id, "Empty message received")
                    continue
                
                # Send initial thinking step
                await manager.send_thinking_step(connection_id, "session_management", "Processing your message...")
                
                # Process message with orchestrator
                try:
                    # Create a callback function for real-time updates
                    async def websocket_callback(step: str, details: Optional[str] = None):
                        await manager.send_thinking_step(connection_id, step, details)
                    
                    # Process the message
                    response = await orchestrator.process_message(
                        user_message=user_message,
                        user_id=user_id,
                        session_id=session_id,
                        websocket_callback=websocket_callback
                    )
                    
                    # Send final response or component
                    if response.get("component"):
                        await manager.send_component(
                            connection_id=connection_id,
                            content=response.get("message", ""),
                            component=response.get("component"),
                            session_id=response.get("session_id"),
                            is_complete=response.get("is_complete", False)
                        )
                    else:
                        await manager.send_response(
                            connection_id=connection_id,
                            response=response.get("message", "No response generated"),
                            session_id=response.get("session_id"),
                            is_complete=response.get("is_complete", True)
                        )
                    
                    # Update current session ID
                    current_session_id = response.get("session_id")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await manager.send_error(connection_id, f"Error processing message: {str(e)}")
                
            except json.JSONDecodeError:
                await manager.send_error(connection_id, "Invalid JSON format")
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected during message handling: {connection_id}")
                break
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                try:
                    await manager.send_error(connection_id, "Internal server error")
                except:
                    break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        manager.disconnect(connection_id)
        try:
            if 'db_session' in locals():
                await db_session.close()
        except:
            pass

@router.get("/health")
async def chat_health():
    """Health check endpoint for chat service."""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

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