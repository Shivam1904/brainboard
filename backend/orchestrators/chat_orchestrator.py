"""
Chat orchestrator for coordinating conversation flow.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, Optional, List
from services.intent_service import IntentService
from services.session_service import SessionService
from services.ai_service import AIService
from ai_engine.tools.tool_registry import ToolRegistry
from ai_engine.models.session_memory import SessionMemory
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# CONTEXT CLASS
# ============================================================================
class ConversationContext:
    """Context object containing all conversation state."""
    
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.intent: Optional[str] = None
        self.widget_type: Optional[str] = None
        self.parameters: Dict[str, Any] = {}
        self.missing_parameters: List[str] = []
        self.chat_history: List[Dict[str, str]] = []
        self.prompt: str = ""
        self.is_complete: bool = False
        self.error: Optional[str] = None
    
    def add_message(self, role: str, content: str):
        """Add message to chat history."""
        self.chat_history.append({"role": role, "content": content})
    
    def update_parameters(self, new_params: Dict[str, Any]):
        """Update parameters and recalculate missing ones."""
        self.parameters.update(new_params)
    
    def set_missing_parameters(self, missing: List[str]):
        """Set missing parameters."""
        self.missing_parameters = missing
    
    def has_all_parameters(self) -> bool:
        """Check if all required parameters are present."""
        return len(self.missing_parameters) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for AI processing."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "intent": self.intent,
            "widget_type": self.widget_type,
            "parameters": self.parameters,
            "missing_parameters": self.missing_parameters,
            "chat_history": self.chat_history,
            "prompt": self.prompt,
            "is_complete": self.is_complete,
            "error": self.error
        }

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
        
        # Register available tools
        self._register_tools()
    
    def _register_tools(self):
        """Register available tools."""
        from ai_engine.tools.alarm_tool import AlarmTool
        alarm_tool = AlarmTool(self.db_session)
        self.tool_registry.register_tool(alarm_tool)
    
    async def process_message(
        self, 
        user_message: str, 
        user_id: str, 
        session_id: Optional[str] = None,
        websocket_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Process a user message and return AI response."""
        try:
            # Create context and initialize session
            context = await self._create_context(user_id, session_id, user_message, websocket_callback)
            if not context:
                return self._create_error_response("Session creation failed", session_id)
            
            # Process the conversation with unified flow
            return await self._process_conversation(context, user_message, websocket_callback)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return self._create_error_response(str(e), session_id)
    
    async def _create_context(self, user_id: str, session_id: Optional[str], user_message: str, websocket_callback: Optional[callable]) -> Optional[ConversationContext]:
        """Create conversation context and initialize session."""
        await self._send_thinking_step(websocket_callback, "session_management", "Initializing session...")
        
        # Get or create session
        session = self.session_service.get_or_create_session(session_id, user_id)
        if not session:
            return None
        
        # Create context from session state
        context = ConversationContext(user_id, session.session_id)
        context.add_message("user", user_message)
        
        # Load existing state if available
        if session.current_intent:
            context.intent = session.current_intent
            context.widget_type = session.current_intent.replace('create_', '')
            context.parameters = session.filled_params.copy()
            context.missing_parameters = session.pending_params.copy()
            
            # Load chat history
            for message in session.conversation_history:
                context.add_message(message.role, message.content)
        
        return context
    
    async def _process_conversation(self, context: ConversationContext, user_message: str, websocket_callback: Optional[callable]) -> Dict[str, Any]:
        """Unified conversation processing flow."""
        # Store current context for intent recognition to access
        self._current_context = context
        
        # Step 1: Recognize or update intent
        await self._send_thinking_step(websocket_callback, "intent_recognition", "Analyzing your request...")
        
        if not context.intent:
            # New conversation - recognize intent
            intent_response = await self._recognize_intent(user_message, websocket_callback)
            
            # Handle AI fallback responses directly
            if intent_response and not intent_response.get("intent_found", False):
                # AI provided a fallback response - return it directly
                context.add_message("assistant", intent_response.get("message", ""))
                await self._save_session_state(context)
                return {
                    "message": intent_response.get("message", ""),
                    "session_id": context.session_id,
                    "is_complete": False,
                    "fallback_attempt": intent_response.get("fallback_attempt", 1)
                }
            
            if not intent_response:
                return self._create_unsupported_response(context.session_id)
            
            # Store intent and parameters
            context.intent = f"create_{intent_response.get('widget_type')}"
            context.widget_type = intent_response.get("widget_type")
            context.parameters = intent_response.get("parameters", {})
            context.missing_parameters = intent_response.get("missing_parameters", [])
            
            # Use message from intent recognition if available
            if intent_response.get("message"):
                context.add_message("assistant", intent_response["message"])
        
        else:
            # Continuing conversation - extract additional parameters
            await self._send_thinking_step(websocket_callback, "parameter_extraction", "Extracting additional parameters...")
            
            # Log AI request for parameter extraction
            await self._send_ai_log(websocket_callback, "REQUEST", "Parameter Extraction", {
                "user_message": user_message,
                "current_intent": context.intent,
                "existing_parameters": context.parameters,
                "missing_parameters": context.missing_parameters
            })
            
            param_response = await self.intent_service.extract_parameters(
                user_message, context.intent, context.parameters, context.missing_parameters
            )
            
            # Log AI response for parameter extraction
            await self._send_ai_log(websocket_callback, "RESPONSE", "Parameter Extraction Response", param_response)
            
            if param_response:
                context.update_parameters(param_response.updated_parameters)
                context.set_missing_parameters(param_response.missing_parameters)
            
            # Recalculate missing parameters
            missing_params = self.intent_service.get_missing_parameters(context.intent, context.parameters)
            context.set_missing_parameters(missing_params)
        
        # Step 2: Save session state
        await self._save_session_state(context)
        
        # Step 3: Check if we need more parameters
        if not context.has_all_parameters():
            return await self._request_missing_parameters(context, websocket_callback)
        else:
            return await self._execute_widget_creation(context, websocket_callback)
    
    async def _recognize_intent(self, user_message: str, websocket_callback: Optional[callable]) -> Optional[Dict[str, Any]]:
        """Recognize user intent with fallback mechanism."""
        max_attempts = 3
        for attempt in range(max_attempts + 1):
            if attempt > 0:
                await self._send_thinking_step(websocket_callback, "intent_processing", f"Retrying intent recognition (attempt {attempt + 1})...")
            
            # Log AI request
            await self._send_ai_log(websocket_callback, "REQUEST", f"Intent Recognition Attempt {attempt + 1}", {
                "user_message": user_message,
                "attempt": attempt
            })
            
            # Convert context chat history to the format expected by AI service
            conversation_history = None
            if hasattr(self, '_current_context') and self._current_context:
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in self._current_context.chat_history
                ]
            
            intent_response = await self.intent_service.recognize_intent(user_message, attempt, conversation_history)
            
            # Log AI response
            await self._send_ai_log(websocket_callback, "RESPONSE", f"Intent Recognition Response {attempt + 1}", intent_response)
            
            if intent_response and intent_response.get("intent_found", False) and intent_response.get("confidence", 0) >= 0.6:
                return intent_response
            
            if attempt < max_attempts:
                # Return AI's fallback response directly
                return intent_response
        
        return None
    
    async def _save_session_state(self, context: ConversationContext):
        """Save current context state to session."""
        session = self.session_service.get_session(context.session_id)
        if session:
            session.current_intent = context.intent
            session.filled_params = context.parameters.copy()
            session.pending_params = context.missing_parameters.copy()
            
            # Update chat history
            for message in context.chat_history:
                if not any(m.content == message["content"] for m in session.conversation_history):
                    session.add_message(message["role"], message["content"])
            
            self.session_service.save_session(session)
    
    async def _request_missing_parameters(self, context: ConversationContext, websocket_callback: Optional[callable]) -> Dict[str, Any]:
        """Request missing parameters from user."""
        await self._send_thinking_step(websocket_callback, "response_generation", "Generating follow-up question...")
        
        # Generate follow-up question
        followup_question = await self._generate_followup_question(context)
        context.add_message("assistant", followup_question)
        
        # Save updated session
        await self._save_session_state(context)
        
        return self._create_followup_response(context, followup_question)
    
    async def _generate_followup_question(self, context: ConversationContext) -> str:
        """Generate follow-up question for missing parameters."""
        # Log AI request
        await self._send_ai_log(None, "REQUEST", "Follow-up Question Generation", {
            "intent": context.intent,
            "missing_parameters": context.missing_parameters,
            "chat_history": context.chat_history[-1]["content"] if context.chat_history else ""
        })
        
        followup_question = await self.ai_service.generate_followup_question(
            context.intent, context.missing_parameters, context.chat_history[-1]["content"] if context.chat_history else ""
        )
        
        # Log AI response
        await self._send_ai_log(None, "RESPONSE", "Follow-up Question Response", {
            "followup_question": followup_question
        })
        
        # Always return AI's response, never create fallback
        return followup_question
    
    async def _execute_widget_creation(self, context: ConversationContext, websocket_callback: Optional[callable]) -> Dict[str, Any]:
        """Execute widget creation and return response."""
        await self._send_thinking_step(websocket_callback, "tool_execution", "Executing your request...")
        
        # Handle non-alarm widgets (simulate success for now)
        if context.widget_type != "alarm" and not self.tool_registry.has_tool(f"{context.widget_type}_tool"):
            return self._simulate_widget_creation(context)
        
        # Execute actual tool
        result = await self._execute_tool(context)
        
        await self._send_thinking_step(websocket_callback, "response_generation", "Generating final response...")
        
        # Log AI request for confirmation
        await self._send_ai_log(websocket_callback, "REQUEST", "Confirmation Generation", {
            "intent": context.intent,
            "tool_result": result
        })
        
        # Always use AI's confirmation message
        confirmation = await self.ai_service.generate_confirmation(context.intent, result)
        
        # Log AI response
        await self._send_ai_log(websocket_callback, "RESPONSE", "Confirmation Response", {
            "confirmation": confirmation
        })
        
        context.add_message("assistant", confirmation)
        
        # Handle success/failure
        if result.get("success"):
            self.session_service.clear_session(context.session_id)
            context.is_complete = True
        else:
            await self._save_session_state(context)
            context.is_complete = False
        
        return {
            "message": confirmation,
            "session_id": context.session_id,
            "is_complete": context.is_complete,
            "intent": context.intent,
            "widget_type": context.widget_type,
            "created_resource": result.get("data") if result.get("success") else None,
            "success": result.get("success", False)
        }
    
    def _simulate_widget_creation(self, context: ConversationContext) -> Dict[str, Any]:
        """Simulate successful widget creation for non-alarm types."""
        # Use AI's response instead of hardcoded message
        confirmation = f"✅ {context.widget_type.replace('-', ' ').title()} widget created successfully!"
        context.add_message("assistant", confirmation)
        context.is_complete = True
        
        self.session_service.clear_session(context.session_id)
        
        return {
            "message": confirmation,
            "session_id": context.session_id,
            "is_complete": True,
            "intent": context.intent,
            "widget_type": context.widget_type,
            "created_resource": {
                "widget_type": context.widget_type,
                "parameters": context.parameters
            },
            "success": True
        }
    
    async def _execute_tool(self, context: ConversationContext) -> Dict[str, Any]:
        """Execute the appropriate tool for widget creation."""
        tool_name = f"{context.widget_type}_tool"
        
        if not self.tool_registry.has_tool(tool_name):
            tool_name = "alarm_tool"  # Fallback
            logger.info(f"Using alarm_tool as fallback for {context.widget_type} widget")
        
        tool_params = {
            "intent": context.intent,
            "widget_type": context.widget_type,
            **context.parameters
        }
        
        return await self.tool_registry.execute_tool(tool_name, tool_params, context.user_id)
    
    async def _send_ai_log(self, websocket_callback: Optional[callable], log_type: str, title: str, data: Any):
        """Send AI request/response log via WebSocket."""
        if websocket_callback:
            import json
            try:
                # Convert data to JSON-serializable format
                if isinstance(data, dict):
                    serializable_data = json.dumps(data, indent=2, default=str)
                else:
                    serializable_data = str(data)
                
                await websocket_callback("ai_log", {
                    "type": log_type,
                    "title": title,
                    "data": serializable_data,
                    "timestamp": str(datetime.now())
                })
            except Exception as e:
                logger.error(f"Error sending AI log: {e}")
    
    async def _send_thinking_step(self, websocket_callback: Optional[callable], step: str, details: str):
        """Send thinking step via WebSocket if callback provided."""
        if websocket_callback:
            await websocket_callback(step, details)
    
    def _create_error_response(self, error_message: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "message": f"I'm sorry, but I encountered an error. Please try again.",
            "session_id": session_id,
            "is_complete": True,
            "error": error_message
        }
    
    def _create_unsupported_response(self, session_id: str) -> Dict[str, Any]:
        """Create response for unsupported requests."""
        return {
            "message": "I'm sorry, but I can only help with widget creation requests. I can help you create todo tasks, habits, alarms, trackers, or web search widgets. Please try asking about creating a widget instead.",
            "session_id": session_id,
            "is_complete": True,
            "intent": "unknown"
        }
    
    def _create_followup_response(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Create standardized followup response."""
        response = {
            "message": message,
            "session_id": context.session_id,
            "is_complete": False,
            "intent": context.intent,
            "widget_type": context.widget_type,
            "missing_parameters": context.missing_parameters
        }
        
        # Add form component if appropriate
        if self._should_send_form(context):
            response["component"] = {
                "id": f"form_{context.session_id}",
                "type": f"{context.widget_type}-form",
                "props": {
                    "filledParams": context.parameters,
                    "missingParams": context.missing_parameters
                }
            }
        
        return response
    
    def _should_send_form(self, context: ConversationContext) -> bool:
        """Check if we should send a form component."""
        return context.intent is not None and len(context.parameters) > 0 