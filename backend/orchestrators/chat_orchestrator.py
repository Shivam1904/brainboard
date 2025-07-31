"""
Chat orchestrator for coordinating conversation flow.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, Optional
from services.intent_service import IntentService
from services.session_service import SessionService
from services.ai_service import AIService
from ai_engine.tools.tool_registry import ToolRegistry
from ai_engine.models.session_memory import SessionMemory

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# CHAT ORCHESTRATOR CLASS
# ============================================================================
class ChatOrchestrator:
    """Main conversation coordinator for AI chat functionality."""
    
    def __init__(self, db_session):
        """Initialize the chat orchestrator."""
        self.intent_service = IntentService()
        self.session_service = SessionService()
        self.ai_service = AIService()
        self.tool_registry = ToolRegistry()
        self.db_session = db_session
        
        # Register tools
        from ai_engine.tools.alarm_tool import AlarmTool
        alarm_tool = AlarmTool(db_session)
        self.tool_registry.register_tool(alarm_tool)
    
    async def process_message(
        self, 
        user_message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return AI response.
        
        Args:
            user_message: User's message
            user_id: User identifier
            session_id: Optional session ID for continuing conversation
            
        Returns:
            Response dictionary with message, session info, and status
        """
        try:
            # Get or create session
            session = self.session_service.get_or_create_session(session_id, user_id)
            
            # Add user message to conversation history
            session.add_message("user", user_message)
            
            # Determine if this is a new conversation or continuation
            if not session.current_intent:
                # New conversation - recognize intent
                return await self._handle_new_conversation(session, user_message)
            else:
                # Continuing conversation - extract parameters
                return await self._handle_continuing_conversation(session, user_message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": "I'm sorry, but I encountered an error. Please try again.",
                "session_id": session_id,
                "is_complete": True,
                "error": str(e)
            }
    
    async def _handle_new_conversation(self, session: SessionMemory, user_message: str) -> Dict[str, Any]:
        """Handle a new conversation by recognizing intent."""
        # Try intent recognition with fallback mechanism
        max_fallback_attempts = 3
        intent_response = None
        
        for attempt in range(max_fallback_attempts + 1):
            intent_response = await self.intent_service.recognize_intent(user_message, attempt)
            
            if intent_response and intent_response.intent != "unknown":
                break
            
            if attempt < max_fallback_attempts:
                session.increment_fallback_attempts()
                fallback_message = self.ai_service.get_fallback_message(attempt + 1)
                session.add_message("assistant", fallback_message)
                
                return {
                    "message": fallback_message,
                    "session_id": session.session_id,
                    "is_complete": False,
                    "intent": "unknown",
                    "fallback_attempt": attempt + 1
                }
        
        # If we still don't have a valid intent after all attempts
        if not intent_response or intent_response.intent == "unknown":
            return {
                "message": "I'm sorry, but I can only help with alarm-related requests. I don't have tools available for other types of requests. Please try asking about alarms instead.",
                "session_id": session.session_id,
                "is_complete": True,
                "intent": "unknown",
                "fallback_attempt": max_fallback_attempts
            }
        
        # Store intent and parameters
        session.current_intent = intent_response.intent
        session.original_message = user_message
        session.update_parameters(intent_response.parameters)
        
        # Check if we have all required parameters
        missing_params = self.intent_service.get_missing_parameters(
            intent_response.intent, session.filled_params
        )
        session.set_pending_parameters(missing_params)
        
        # Save session
        self.session_service.save_session(session)
        
        if missing_params:
            # Generate follow-up question
            followup_question = await self.ai_service.generate_followup_question(
                intent_response.intent, missing_params, user_message
            )
            
            if not followup_question:
                followup_question = "I need more information to help you. Could you please provide the missing details?"
            
            session.add_message("assistant", followup_question)
            self.session_service.save_session(session)
            
            return {
                "message": followup_question,
                "session_id": session.session_id,
                "is_complete": False,
                "intent": intent_response.intent,
                "missing_parameters": missing_params
            }
        else:
            # Execute tool
            return await self._execute_tool_and_respond(session)
    
    async def _handle_continuing_conversation(self, session: SessionMemory, user_message: str) -> Dict[str, Any]:
        """Handle continuing conversation by extracting parameters."""
        # Extract additional parameters from follow-up message
        param_response = await self.intent_service.extract_parameters(
            user_message, 
            session.current_intent, 
            session.filled_params, 
            session.pending_params
        )
        
        if param_response:
            # Update session with new parameters
            session.update_parameters(param_response.updated_parameters)
            session.set_pending_parameters(param_response.missing_parameters)
        
        # Check if we now have all required parameters
        missing_params = self.intent_service.get_missing_parameters(
            session.current_intent, session.filled_params
        )
        session.set_pending_parameters(missing_params)
        
        # Save session
        self.session_service.save_session(session)
        
        if missing_params:
            # Still missing parameters - generate follow-up question
            followup_question = await self.ai_service.generate_followup_question(
                session.current_intent, missing_params, user_message
            )
            
            if not followup_question:
                followup_question = "I still need more information. Could you please provide the missing details?"
            
            session.add_message("assistant", followup_question)
            self.session_service.save_session(session)
            
            return {
                "message": followup_question,
                "session_id": session.session_id,
                "is_complete": False,
                "intent": session.current_intent,
                "missing_parameters": missing_params
            }
        else:
            # Execute tool
            return await self._execute_tool_and_respond(session)
    
    async def _execute_tool_and_respond(self, session: SessionMemory) -> Dict[str, Any]:
        """Execute tool and generate response."""
        try:
            # Prepare parameters for tool execution
            tool_params = {
                "intent": session.current_intent,
                **session.filled_params
            }
            
            # Execute tool
            result = await self.tool_registry.execute_tool("alarm_tool", tool_params, session.user_id)
            
            # Generate confirmation message
            confirmation = await self.ai_service.generate_confirmation(session.current_intent, result)
            
            if not confirmation:
                confirmation = result.get("message", "Operation completed successfully.")
            
            session.add_message("assistant", confirmation)
            
            # Clear session if operation was successful
            if result.get("success"):
                self.session_service.clear_session(session.session_id)
                is_complete = True
            else:
                self.session_service.save_session(session)
                is_complete = False
            
            return {
                "message": confirmation,
                "session_id": session.session_id,
                "is_complete": is_complete,
                "intent": session.current_intent,
                "created_resource": result.get("data") if result.get("success") else None,
                "success": result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            error_message = "I'm sorry, but there was an error processing your request. Please try again."
            session.add_message("assistant", error_message)
            self.session_service.save_session(session)
            
            return {
                "message": error_message,
                "session_id": session.session_id,
                "is_complete": False,
                "intent": session.current_intent,
                "error": str(e)
            } 