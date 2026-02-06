"""
AI WebSocket Manager
Manages WebSocket connections for AI chat functionality.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import WebSocket



logger = logging.getLogger(__name__)

class AIWebSocketManager:
    """Manages WebSocket connections for AI chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_contexts: Dict[str, Any] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        # Create default context directly using context connection manager
        # We'll create a basic context here and let the orchestrator handle it properly
        from services.context_connection_manager import ContextConnectionManager
        context_manager = ContextConnectionManager()
        context = context_manager.get_context(connection_id)
        
        # Set a default user ID for the context
        context.user_id = "user_001"
        
        self.connection_contexts[connection_id] = context
        
        logger.info(f"AI WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_contexts:
            del self.connection_contexts[connection_id]
        logger.info(f"AI WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
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
    
    async def send_response(self, connection_id: str, response: Dict[str, Any]):
        """Send the final AI response to the client."""
        message = {
            "type": "response",
            "content": response,
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
    
    def get_context(self, connection_id: str) -> Any:
        """Get the context for a specific connection."""
        return self.connection_contexts.get(connection_id)
    
    def update_context(self, connection_id: str, context: Any) -> None:
        """Update the context for a specific connection."""
        self.connection_contexts[connection_id] = context 