"""
AI Orchestrator - Simplified version that only handles AI responses and context updates
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
import time
from pathlib import Path

from ai_engine.models.llm_client import LLMClient
from services.ai_prompt_preprocessing import AIPromptPreprocessing

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Simplified AI orchestrator that only handles AI responses and context updates."""
    
    def __init__(self, db_session: AsyncSession = None):
        """Initialize the simplified AI orchestrator."""
        # Initialize AI components
        self.llm_client = LLMClient()
        self.db_session = db_session
        
        # Initialize AI prompt preprocessing service
        self.ai_prompt_preprocessing = AIPromptPreprocessing(db_session) if db_session else None
        
        # Conversation history storage per connection
        self.conversation_store = {}
    
    def create_default_context(self, connection_id: str = "default") -> Any:
        """Create a default context with initial values for a new connection."""
        class DefaultContext:
            def __init__(self):
                self.user_id = "user_001"  # Default user ID
                self.current_intent = "unknown"
                self.collected_variables = []
                self.missing_variables = []
                self.round = "normal"
                self.user_chats = []
                self.connection_id = connection_id
                self.created_at = time.time()
                # Initialize additional attributes that BasicContext has
                self.user_tasks = []
                self.todays_date = datetime.now().strftime("%Y-%m-%d")
                self.last_updated = time.time()
            
            def to_dict(self):
                """Convert context to dictionary for JSON serialization."""
                return {
                    'user_id': self.user_id,
                    'current_intent': self.current_intent,
                    'collected_variables': self.collected_variables,
                    'missing_variables': self.missing_variables,
                    'round': self.round,
                    'user_chats': self.user_chats,
                    'connection_id': self.connection_id,
                    'created_at': self.created_at,
                    'user_tasks': self.user_tasks,
                    'todays_date': self.todays_date,
                    'last_updated': self.last_updated
                }
            
            def to_string(self):
                """Convert context to JSON string for debugging."""
                return json.dumps(self.to_dict(), indent=2)
        return DefaultContext()
    
    def reconstruct_context_from_dict(self, context_dict: Dict[str, Any], connection_id: str) -> Any:
        """Reconstruct a context object from a dictionary."""
        # Create new context object
        context = self.create_default_context(connection_id)
        
        # Update with dictionary values
        for key, value in context_dict.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        return context
    
    def _get_conversation_history(self, connection_id: str = "default") -> List[Dict[str, Any]]:
        """Get conversation history for a specific connection."""
        if connection_id not in self.conversation_store:
            self.conversation_store[connection_id] = []
        return self.conversation_store[connection_id]
    
    def _add_to_conversation_history(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Add a message to conversation history for a specific connection."""
        if connection_id not in self.conversation_store:
            self.conversation_store[connection_id] = []
        
        # Add the message
        self.conversation_store[connection_id].append(message)
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversation_store[connection_id]) > 20:
            self.conversation_store[connection_id] = self.conversation_store[connection_id][-20:]
    
    def cleanup_conversation(self, connection_id: str) -> None:
        """Clean up conversation history for a closed connection."""
        if connection_id in self.conversation_store:
            del self.conversation_store[connection_id]
            print(f"🧹 Cleaned up conversation history for connection: {connection_id}")
    
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
        Simplified method to process user message - only gets AI response and updates context.
        """
        try:
            # Send initial thinking step
            await self._send_thinking_step(websocket_callback, "message_processing", "Processing your message...")
            
            # Use existing context or create new one if none exists
            if existing_context:
                context = existing_context
                # Update context with latest data
                context.user_tasks = user_tasks
                context.todays_date = todays_date
                context.last_updated = time.time()
                print(f"🔍 Using existing context for connection: {connection_id}")
            else:
                # Build context for AI using stored conversation history
                stored_history = self._get_conversation_history(connection_id)
                
                # Create new BasicContext with session storage
                class BasicContext:
                    def __init__(self):
                        self.user_tasks = user_tasks
                        self.todays_date = todays_date
                        self.user_chats = stored_history.copy()
                        self.connection_id = connection_id
                        self.user_id = f"user_{connection_id}"  # Generate user_id from connection_id
                        self.created_at = time.time()
                        # Initialize optional attributes that might be set later
                        self.current_intent = None
                        self.collected_variables = []
                        self.missing_variables = []
                        self.round = "normal"
                        self.last_updated = time.time()
                    
                    def to_dict(self):
                        """Convert context to dictionary for JSON serialization."""
                        return {
                            'user_tasks': self.user_tasks,
                            'todays_date': self.todays_date,
                            'user_chats': self.user_chats,
                            'connection_id': self.connection_id,
                            'user_id': self.user_id,
                            'created_at': self.created_at,
                            'current_intent': self.current_intent,
                            'collected_variables': self.collected_variables,
                            'missing_variables': self.missing_variables,
                            'round': self.round,
                            'last_updated': self.last_updated
                        }
                    
                    def to_string(self):
                        """Convert context to JSON string for debugging."""
                        return json.dumps(self.to_dict())
                
                context = BasicContext()
                print(f"🔍 Created new context for connection: {connection_id}")
            
            
            # Add current user message to context and store
            user_message_obj = {
                "role": "user",
                "msg": user_message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Always append to user_chats since we ensure it exists
            context.user_chats.append(user_message_obj)
            
            self._add_to_conversation_history(connection_id, user_message_obj)
            
            # Debug: Print context after adding message
            print(f"🔍 Context created with {len(context.user_chats)} messages from session storage")
            print(f"🔍 Current message added to context.user_chats")
            
            
            # Send AI response generation step
            await self._send_thinking_step(websocket_callback, "ai_response_generation", "Generating AI response...")

            # Get AI response using the ai_prompt_preprocessing service
            ai_response = await self._get_ai_response(context)
            
            if not ai_response:
                await self._send_thinking_step(websocket_callback, "error_handling", "AI response generation failed")
                return {
                    "success": False,
                    "message": "Failed to get AI response",
                    "intent": "",
                    "should_continue_chat": True
                }
            
            # Send AI response processing step
            await self._send_thinking_step(websocket_callback, "ai_response_processing", "Processing AI response...")
            
            print(f"🔄🔄🔄 DEBUG: previous context: {context.to_string()}")
            # Update context with AI response data
            updated_context = await self._update_context_with_ai_response(context, ai_response)
            
            print(f"🔄🔄🔄 DEBUG: Updated context: {updated_context.to_string()}")

            # Send completion step
            await self._send_thinking_step(websocket_callback, "completion", "Processing complete")
            
            # Determine which response message to use based on AI response
            response_message = self._get_appropriate_response_message(ai_response)
            
            # Store AI response in conversation history
            ai_response_obj = {
                "role": "ai",
                "msg": response_message,
                "timestamp": datetime.now().isoformat(),
                "ai_data": ai_response
            }
            self._add_to_conversation_history(connection_id, ai_response_obj)
            
            return {
                "success": True,
                "message": response_message,
                "intent": ai_response.get("intent", ""),
                "should_continue_chat": True,
                "response_type": "ai_response",
                "ai_response": ai_response,
                "context_updated": True,
                "updated_context": context.to_dict()  # Return context as dictionary
            }
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            await self._send_thinking_step(websocket_callback, "error_handling", f"Error: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "intent": "",
                "should_continue_chat": True
            }
    
    async def _get_ai_response(self, context: Any) -> Optional[Dict[str, Any]]:
        """Get response from AI using the ai_prompt_preprocessing service."""
        try:
            if not self.ai_prompt_preprocessing:
                raise Exception("AI prompt preprocessing service not available")
            
            # Get the compiled prompt from the preprocessing service using existing context
            prompt_data = await self.ai_prompt_preprocessing.compile_ai_prompt(
                context=context  # Use the existing context directly
            )
            
            # Compile the final prompt string
            prompt = self.ai_prompt_preprocessing.compile_prompt_string(prompt_data)
            
            messages = [
                {"role": "system", "content": "You are a conversational task management AI that interprets user conversations and outputs structured JSON in a fixed schema. You help users create, edit, and analyze their tasks and habits. Always respond with valid JSON following the exact field specifications provided."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.llm_client.call_openai(messages)
            print(f"🟢🟢🟢🟢 AI RESPONSE GENERATION STEP RESPONSE: {response}")
            
            if not response:
                logger.error("No response from OpenAI")
                return None
            
            # Parse JSON response using robust parsing utility
            parsed_response = self._clean_json_response(response)
            if not parsed_response:
                logger.error("Failed to parse AI response")
                return None
            return parsed_response
                
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return None
    
    async def _update_context_with_ai_response(self, context: Any, ai_response: Dict[str, Any]) -> Any:
        """Update the context with data from the AI response."""
        try:
            # Extract intent from AI response
            intent = ai_response.get("intent", None)
            
            # Update context with intent
            if hasattr(context, ''):
                context.current_intent = intent
            
            # Process collected variables based on the fields
            collected_variables = []
            missing_variables = []
            
            if intent and ai_response:
                # Get the required and optional variables for this intent from variable config
                intent_variables = self._get_intent_variables(intent)
                
                for var_name, var_config in intent_variables.items():
                    var_value = ai_response.get(var_name)
                    
                    if var_value is not None and var_value != "" and var_value != []:
                        # Variable is collected
                        collected_variables.append({
                            "name": var_name,
                            "value": var_value,
                            "is_required": var_config.get("is_required", False),
                            "description": var_config.get("description", "")
                        })
                    elif var_config.get("is_required", False):
                        # Required variable is missing
                        missing_variables.append(var_name)
                    else:
                        # Optional variable is missing (could be added to missing_variables if needed)
                        pass
            
            # Update context with collected and missing variables
            if hasattr(context, 'collected_variables'):
                context.collected_variables = collected_variables
            else:
                context.collected_variables = collected_variables
                
            if hasattr(context, 'missing_variables'):
                context.missing_variables = missing_variables
            else:
                context.missing_variables = missing_variables
            
            # Update round if this is a try_harder attempt
            if intent != "unknown" and hasattr(context, 'round'):
                context.round = "normal"  # Reset to normal after successful intent recognition
            
            # Add timestamp of last update
            if hasattr(context, 'last_updated'):
                context.last_updated = time.time()
            
            print(f"🔄 Context updated with intent: {intent}")
            print(f"🔄 Collected variables: {len(collected_variables)}")
            print(f"🔄 Missing variables: {len(missing_variables)}")
            return context
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            return context
    
    def _get_intent_variables(self, intent: str) -> Dict[str, Dict[str, Any]]:
        """Get variables configuration for a specific intent."""
        try:
            # Load variable config if not already loaded
            if not hasattr(self, '_variable_config'):
                self._load_variable_config()
            
            intent_variables = {}
            variables = self._variable_config.get('variables', {})
            
            for var_name, var_config in variables.items():
                if var_config.get('intent_type') == intent:
                    intent_variables[var_name] = var_config
            print(f"🟢🟢🟢🟢 INTENT VARIABLES: {intent_variables}")
            return intent_variables
            
        except Exception as e:
            logger.error(f"Error getting intent variables: {e}")
            return {}
    
    def _load_variable_config(self):
        """Load variable configuration from YAML file."""
        try:
            import yaml
            config_file = Path(__file__).parent.parent / "variable_config.yaml"
            with open(config_file, 'r') as f:
                self._variable_config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load variable config: {e}")
            self._variable_config = {}
    
    def _get_appropriate_response_message(self, ai_response: Dict[str, Any]) -> str:
        """Determine which response message to use based on AI response completeness."""
        try:
            intent = ai_response.get("intent", "")
            fields = ai_response.get("fields", {})
            
            if not intent or intent == "":
                return ai_response.get("fallback_response", "I'm not sure what you'd like to do. Can you clarify?")
            
            # Get the required and optional variables for this intent
            intent_variables = self._get_intent_variables(intent)
            
            if not intent_variables:
                return ai_response.get("partial_success_response", "I understand your intent but need more information.")
            
            # Check if all required fields are present
            required_fields = [var_name for var_name, var_config in intent_variables.items() 
                             if var_config.get("is_required", False)]
            
            # Check if at least one optional field is present
            optional_fields = [var_name for var_name, var_config in intent_variables.items() 
                             if not var_config.get("is_required", False)]
            
            required_filled = all(fields.get(field) is not None and fields.get(field) != "" and fields.get(field) != [] 
                                for field in required_fields)
            optional_filled = any(fields.get(field) is not None and fields.get(field) != "" and fields.get(field) != [] 
                                for field in optional_fields)
            
            # Determine which response to use based on completeness
            if required_filled and optional_filled:
                return ai_response.get("success_response", "Great! I have all the information needed.")
            elif required_filled:
                return ai_response.get("partial_success_response", "I have the basic information, but could use some additional details.")
            else:
                return ai_response.get("partial_success_response", "I need some more information to help you properly.")
                
        except Exception as e:
            logger.error(f"Error determining response message: {e}")
            return ai_response.get("fallback_response", "I received your message but encountered an error processing it.")
    
    def _clean_json_response(self, response: str) -> Dict[str, Any]:
        """Clean JSON response to handle markdown formatting and common JSON issues."""
        if not response:
            return {}
        
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        # Find JSON object boundaries
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx + 1]
        
        # Clean common JSON issues
        response = response.strip()
        
        # Remove trailing commas before closing braces/brackets
        import re
        # Remove trailing commas before } or ]
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        
        # Remove trailing commas at the end of lines
        response = re.sub(r',(\s*\n\s*[}\]])', r'\1', response)
        
        # Try to parse the cleaned JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cleaned JSON: {e}")
            return {}
    
    async def _send_thinking_step(self, websocket_callback: Optional[Callable], step: str, details: str):
        """Send thinking step via WebSocket if callback provided."""
        if websocket_callback:
            try:
                await websocket_callback(step, details)
            except Exception as e:
                logger.error(f"Error sending thinking step: {e}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "orchestrator_type": "simplified",
            "ai_prompt_preprocessing": "Initialized" if self.ai_prompt_preprocessing else "Not available",
            "llm_client": "Initialized" if self.llm_client else "Not available",
            "db_session": "Available" if self.db_session else "Not available"
        } 