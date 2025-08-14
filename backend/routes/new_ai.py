"""
Unified WebSocket route for AI chat - handles everything in one place like the original ai.py
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import AsyncSessionLocal
from services.new_ai_service import NewAIService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Service"])

class AIWebSocketManager:
    """Manages WebSocket connections for AI chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_contexts: Dict[str, Any] = {}  # Store context per connection
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        # Create and store context for this connection
        from orchestrators.ai_orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()
        context = orchestrator.create_default_context(connection_id)
        self.connection_contexts[connection_id] = context
        
        logger.info(f"AI WebSocket connected: {connection_id}")
        # print(f"AI WebSocket connected: {connection_id}")
        # print(f"🔍 Context created for connection: {connection_id}") 
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_contexts:
            del self.connection_contexts[connection_id]
        logger.info(f"AI WebSocket disconnected: {connection_id}")
        # print(f"AI WebSocket disconnected: {connection_id}")
        # print(f"🔍 Context cleaned up for connection: {connection_id}") 
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                # print(f"AI WebSocket sent message: {message}") 
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                # print(f"Error sending message to {connection_id}: {e}") 
                self.disconnect(connection_id)
    
    async def send_thinking_step(self, connection_id: str, step: str, details: str):
        """Send a thinking step update to the client."""
        message = {
            "type": "thinking",
            "step": step,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
        # print(f"AI WebSocket sent thinking step: {message}") 
    
    async def send_response(self, connection_id: str, response: Dict[str, Any]):
        """Send the final AI response to the client."""
        message = {
            "type": "response",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
        # print(f"AI WebSocket sent response: {message}")

    async def send_error(self, connection_id: str, error: str):
        """Send an error message to the client."""
        message = {
            "type": "error",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(connection_id, message)
        # print(f"AI WebSocket sent error: {message}")
    
    def get_context(self, connection_id: str) -> Any:
        """Get the context for a specific connection."""
        return self.connection_contexts.get(connection_id)
    
    def update_context(self, connection_id: str, context: Any) -> None:
        """Update the context for a specific connection."""
        self.connection_contexts[connection_id] = context 

# Global WebSocket manager
ai_manager = AIWebSocketManager()

@router.websocket("/ws")
async def websocket_ai(websocket: WebSocket):
    """
    Main WebSocket endpoint for AI chat - handles everything in one place.
    Connect to: ws://localhost:8000/api/v1/ai/ws
    """
    connection_id = str(uuid.uuid4())
    
    
    try:
        # Accept the connection
        
        await ai_manager.connect(websocket, connection_id)
        
        # Send connection confirmation
        
        await ai_manager.send_message(connection_id, {
            "type": "connection",
            "connection_id": connection_id,
            "message": "Connected to Brainboard AI Service",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Initialize AI service
        
        db_session = AsyncSessionLocal()
        ai_service = NewAIService(db_session)
        
        # Send welcome message
        
        await ai_manager.send_thinking_step(connection_id, "welcome", "AI service ready! Send me a message to get started.")
        
        # Handle incoming messages
        
        while True:
            try:
                # Receive message from client
                
                data = await websocket.receive_text()
                
                
                message_data = json.loads(data)
                
                
                user_message = message_data.get("message", "")
                user_tasks = message_data.get("user_tasks", [])
                todays_date = message_data.get("todays_date", datetime.now().strftime("%Y-%m-%d"))
                conversation_history = message_data.get("conversation_history", [])
                
                
                # print(f"   - user_message: {user_message}")
                # print(f"   - user_tasks: {user_tasks}")
                # print(f"   - todays_date: {todays_date}")
                # print(f"   - conversation_history: {conversation_history}")
                
                if not user_message:
                    # print(f"🟡 NO MESSAGE PROVIDED: {connection_id}")
                    await ai_manager.send_error(connection_id, "No message provided")
                    continue
                
                
                
                # Create websocket callback for real-time updates
                async def websocket_callback(step: str, details: str):
                    """Callback function to send real-time updates via WebSocket."""
                    try:
                        
                        await ai_manager.send_thinking_step(connection_id, step, details)
                    except Exception as e:
                        # print(f"🔴 ERROR IN WEBSOCKET CALLBACK: {connection_id} - {e}")
                        logger.error(f"Error in websocket callback: {e}")
                
                # Get existing context for this connection
                existing_context = ai_manager.get_context(connection_id)
                if not existing_context:
                    # print(f"🔴 ERROR: No context found for connection: {connection_id}")
                    await ai_manager.send_error(connection_id, "Connection context not found")
                    continue
                
                # Process the message with real-time updates using existing context
                response = await ai_service.process_user_message(
                    user_message=user_message,
                    user_tasks=user_tasks,
                    todays_date=todays_date,
                    conversation_history=conversation_history,
                    websocket_callback=websocket_callback,
                    connection_id=connection_id,
                    existing_context=existing_context
                )
                
                
                
                # Store updated context back in the AI manager
                if response.get("context_updated") and "updated_context" in response:
                    # Reconstruct context object from dictionary using the orchestrator
                    context_dict = response["updated_context"]
                    new_context = ai_service.get_orchestrator().reconstruct_context_from_dict(context_dict, connection_id)
                    ai_manager.update_context(connection_id, new_context)
                    # print(f"🔍 Context updated for connection: {connection_id}")
                
                # Send final response
                await ai_manager.send_response(connection_id, response)
                
                
            except json.JSONDecodeError as e:
                # print(f"🔴 JSON DECODE ERROR: {connection_id} - {e}")
                await ai_manager.send_error(connection_id, "Invalid JSON format")
            except WebSocketDisconnect:
                # print(f"🟡 WEBSOCKET DISCONNECTED DURING MESSAGE HANDLING: {connection_id}")
                logger.info(f"AI WebSocket disconnected during message handling: {connection_id}")
                break
            except Exception as e:
                # print(f"🔴 ERROR HANDLING AI MESSAGE: {connection_id} - {e}")
                logger.error(f"Error handling AI message: {e}")
                try:
                    await ai_manager.send_error(connection_id, f"Internal server error: {str(e)}")
                except:
                    break
                
    except WebSocketDisconnect:
        # print(f"🟡 WEBSOCKET DISCONNECTED: {connection_id}")
        logger.info(f"AI WebSocket disconnected: {connection_id}")
    except Exception as e:
        # print(f"🔴 WEBSOCKET ERROR: {connection_id} - {e}")
        logger.error(f"AI WebSocket error: {e}")
    finally:
        # Clean up connection
        
        ai_manager.disconnect(connection_id)
        
        # Clean up conversation history
        try:
            ai_service.get_orchestrator().cleanup_conversation(connection_id)
        except Exception as e:
            # print(f"🔴 ERROR CLEANING UP CONVERSATION: {connection_id} - {e}")
            logger.error(f"Error cleaning up conversation: {e}")
        
        try:
            if 'db_session' in locals():
                await db_session.close()
                
        except Exception as e:
            print(f"🔴 ERROR CLOSING DATABASE SESSION: {connection_id} - {e}")

@router.get("/health")
async def health_check():
    """Health check for the AI service."""
    return {"status": "healthy", "service": "AI Service"}

@router.get("/websocket/health")
async def websocket_health():
    """Health check endpoint for AI WebSocket service."""
    return {
        "status": "healthy",
        "active_connections": len(ai_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    } 