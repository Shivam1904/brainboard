"""
New AI Service - Configuration-driven implementation using AIOrchestrator
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrators.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

class NewAIService:
    """Configuration-driven AI service that uses AIOrchestrator for all operations."""
    
    def __init__(self, db_session: AsyncSession = None):
        """Initialize the new AI service with orchestrator."""
        self.orchestrator = AIOrchestrator(db_session)
        self.db_session = db_session
    
    async def process_user_message(
        self, 
        user_message: str, 
        user_tasks: List[str], 
        todays_date: str,
        conversation_history: List[Dict[str, str]] = None,
        websocket_callback: Optional[Callable] = None,
        connection_id: str = "default",
        existing_context: Any = None
    ) -> Dict[str, Any]:
        """
        Main method to process user message using the AI orchestrator.
        """
        try:
            # Delegate to orchestrator with websocket callback support
            result = await self.orchestrator.process_user_message(
                user_message, user_tasks, todays_date, conversation_history, websocket_callback, connection_id, existing_context
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            # Send error via websocket if callback available
            if websocket_callback:
                try:
                    await websocket_callback("error_handling", f"Service error: {str(e)}")
                except Exception as ws_error:
                    logger.error(f"Error sending websocket error: {ws_error}")
            
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "intent": "",
                "should_continue_chat": True
            }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration from the orchestrator."""
        return self.orchestrator.get_configuration_summary()
    
    def get_orchestrator(self) -> AIOrchestrator:
        """Get the underlying orchestrator for direct access if needed."""
        return self.orchestrator 