"""
AI Orchestrator - Refactored to use separate services for context, database, and validation
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
import pprint

from ai_engine.models.llm_client import LLMClient
from services.ai_prompt_preprocessing import AIPromptPreprocessing
from services.context_connection_manager import ContextConnectionManager
from services.context_service import ContextService
from services.validation_engine import ValidationEngine
from services.config_loader import AIConfigLoader
from db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Refactored AI orchestrator that coordinates between separate services."""
    
    def __init__(self):
        """Initialize the AI orchestrator."""
        self.llm_client = LLMClient()
        
        # Initialize database session
        self.db_session = None  # Will be initialized when needed
        
        # Initialize services with the same database session
        self.context_connection_manager = ContextConnectionManager()
        self.context_service = ContextService()
        
        # Initialize validation engine with config loader
        self.validation_engine = ValidationEngine()
        
        
        self.ai_prompt_preprocessing = AIPromptPreprocessing()
    
    async def _get_db_session(self) -> AsyncSession:
        """Get a database session, creating one if needed."""
        if self.db_session is None:
            self.db_session = AsyncSessionLocal()
            logger.info("Created new database session")
        return self.db_session
    
    async def _close_db_session(self):
        """Close the database session if it exists."""
        if self.db_session is not None:
            try:
                await self.db_session.close()
                self.db_session = None
                logger.info("Closed database session")
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
    
    async def process_user_message(
        self,
        user_message: str,
        user_tasks: List[str] = None,
        todays_date: str = None,
        conversation_history: List[Dict[str, str]] = None,
        websocket_callback: Optional[Callable] = None,
        connection_id: str = "default",
        existing_context: Any = None
    ) -> None:  # No return value - orchestrator handles everything
        """
        Main orchestrator flow - coordinates all services to process user message.
        All responses and context updates are handled internally via WebSocket.
        """
        try:
            # Get context from context connection manager or use existing context
            await self._ping_thinking_step(websocket_callback, "getting_context", "Getting conversation context...")
            if existing_context:
                context = existing_context
                logger.info(f"Using existing context with {len(getattr(context, 'user_chats', []))} messages")
            else:
                context = await self.context_connection_manager.get_context(connection_id)
                logger.info(f"Retrieved context from manager with {len(getattr(context, 'user_chats', []))} messages")
            
            # Store additional context information if provided
            if user_tasks:
                context.user_tasks = user_tasks
            if todays_date:
                context.todays_date = todays_date
            if conversation_history:
                context.conversation_history = conversation_history
            
            # First context update: Add user message to conversation history
            await self._ping_thinking_step(websocket_callback, "updating_conversation", "Updating conversation history...")
            context = await self.context_service.update_conversation_history(user_message, context)
            logger.info(f"After updating conversation history: {len(getattr(context, 'user_chats', []))} messages")
            
            # Store the updated context back to the connection manager
            self.context_connection_manager.store_context(connection_id, context)
            
            # Get processed input using context + db session
            await self._ping_thinking_step(websocket_callback, "processing_input", "Processing your message...")
            if not self.ai_prompt_preprocessing:
                raise Exception("AI prompt preprocessing service not available - database session required")
            db_session = await self._get_db_session()
            processed_input = await self.ai_prompt_preprocessing.compile_prompt_string(context, db_session)
            
            # Run AI engine to get response
            await self._ping_thinking_step(websocket_callback, "running_ai", "Generating AI response...")
            ai_response = await self._run_ai_engine(processed_input)
            
            # Validate the AI response
            await self._ping_thinking_step(websocket_callback, "validating_response", "Validating AI response...")
            valid_response = await self._validate_ai_response(ai_response)
            
            # Second context update: Update context with AI response and variables
            await self._ping_thinking_step(websocket_callback, "updating_context", "Updating conversation context...")
            variable_config = self.ai_prompt_preprocessing.variable_config if self.ai_prompt_preprocessing else {}
            
            context = await self.context_service.update_with_ai_response(valid_response, context, variable_config)
            logger.info(f"After updating with AI response: {len(getattr(context, 'user_chats', []))} messages")
            
            # Store the final updated context back to the connection manager
            self.context_connection_manager.store_context(connection_id, context)
            
            # Send final response via WebSocket
            response_data = {
                "success": True,
                "ai_response": valid_response,
                "context": self.context_service.get_context_summary(context)
            }
            await self._ping_response(websocket_callback, response_data)
            return response_data
            
            # Context is automatically managed by the orchestrator - no need to return it
            
        except Exception as e:
            logger.error(f"Error in orchestrator flow: {e}")
            await self._ping_error(websocket_callback, {"error": str(e)})
        finally:
            # Don't close the database session here - keep it open for the connection
            # It will be closed when cleanup_conversation is called
            pass
    
    async def _validate_ai_response(self, ai_response: Any) -> Dict[str, Any]:
        """Validate AI response using the validation engine."""
        return await self.validation_engine.validate_ai_response(ai_response)

    async def _run_ai_engine(self, processed_input: str) -> Dict[str, Any]:
        """Run AI engine using processed input."""
        messages = [
            {"role": "system", "content": "You are a conversational task management AI that interprets user conversations and outputs structured JSON in a fixed schema. You help users create, edit, and analyze their tasks and habits. Always respond with valid JSON following the exact field specifications provided."},
            {"role": "user", "content": processed_input}
        ]
        
        response = await self.llm_client.call_openai(messages)
        print(f"🟢🟢🟢🟢 AI RESPONSE: {response}")
        return response or {}
    
    async def _ping_response(self, websocket_callback: Optional[Callable], response_data: Dict[str, Any]):
        """Ping response via WebSocket."""
        if websocket_callback:
            try:
                await websocket_callback("response", response_data)
            except Exception as e:
                logger.error(f"Error pinging response: {e}")
    

    async def _ping_thinking_step(self, websocket_callback: Optional[Callable], step: str, details: str):
        """Ping thinking step via WebSocket."""
        if websocket_callback:
            try:
                await websocket_callback(step, details)
            except Exception as e:
                logger.error(f"Error pinging thinking step: {e}")
    
    async def _ping_error(self, websocket_callback: Optional[Callable], error_data: Dict[str, Any]):
        """Ping error via WebSocket."""
        if websocket_callback:
            try:
                await websocket_callback("error", error_data)
            except Exception as e:
                logger.error(f"Error pinging error: {e}")

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "orchestrator_type": "refactored",
            "ai_prompt_preprocessing": "Initialized" if self.ai_prompt_preprocessing else "Not available",
            "llm_client": "Initialized" if self.llm_client else "Not available",
            "db_session": "Available" if self.db_session is not None else "Not available",
            "services": {
                "context_connection_manager": "Initialized",
                "context_service": "Initialized", 
                "validation_engine": "Initialized"
            }
        }
    
    def cleanup_conversation(self, connection_id: str) -> None:
        """Clean up conversation resources for a connection."""
        try:
            # Clean up connection in the context connection manager
            self.context_connection_manager.disconnect_connection(connection_id)
            
            # Clean up database session if it exists
            if self.db_session is not None:
                try:
                    # Use the async close method
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If we're in an async context, schedule the close
                            asyncio.create_task(self._close_db_session())
                        else:
                            # If we're not in an async context, just close directly
                            loop.run_until_complete(self._close_db_session())
                    except RuntimeError:
                        # No event loop, just close directly
                        pass
                except Exception as e:
                    logger.error(f"Error closing database session: {e}")
            
            logger.info(f"Cleaned up conversation for connection: {connection_id}")
        except Exception as e:
            logger.error(f"Error cleaning up conversation for {connection_id}: {e}") 