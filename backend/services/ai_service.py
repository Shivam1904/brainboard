"""
AI service for handling all OpenAI LLM interactions.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import json
import logging
from typing import Dict, Any, Optional, List
from ai_engine.models.llm_client import LLMClient
from ai_engine.prompts.intent_recognition import (
    WidgetTypeClassificationPrompts,
    ParameterExtractionPrompts
)
from ai_engine.prompts.parameter_extraction import ParameterExtractionPrompts as LegacyParameterExtractionPrompts
from ai_engine.prompts.followup_questions import FollowupQuestionPrompts
from ai_engine.prompts.confirmation_messages import ConfirmationMessagePrompts
from ai_engine.models.intent_models import ParameterExtractionResponse

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# AI SERVICE CLASS
# ============================================================================
class AIService:
    """Service for handling all OpenAI LLM interactions."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.llm_client = LLMClient()
    
    async def recognize_intent(self, user_message: str, fallback_attempt: int = 0, conversation_history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Recognize user intent using two-step dynamic approach."""
        try:
            # Step 1: Widget Type Classification
            widget_type = await self._classify_widget_type(user_message, conversation_history)
            
            if not widget_type or widget_type == "none":
                # No widget type found - generate dynamic fallback response
                return await self._generate_dynamic_fallback_response(user_message, conversation_history)
            
            # Step 2: Parameter Extraction with Dynamic Follow-up
            return await self._extract_parameters_with_dynamic_response(user_message, widget_type, conversation_history)
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return None
    
    async def _classify_widget_type(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Optional[str]:
        """Step 1: Classify widget type from user message."""
        try:
            messages = WidgetTypeClassificationPrompts.create_messages(user_message, conversation_history)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for widget type classification")
                return None
            
            # Clean and parse JSON response
            try:
                cleaned_response = self._clean_json_response(response)
                data = json.loads(cleaned_response)
                return data.get("widget_type")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse widget type classification response as JSON: {e}")
                logger.error(f"Raw response: {response}")
                logger.error(f"Cleaned response: {cleaned_response if 'cleaned_response' in locals() else 'N/A'}")
                return None
                
        except Exception as e:
            logger.error(f"Error in widget type classification: {e}")
            return None
    
    async def _extract_parameters_with_dynamic_response(self, user_message: str, widget_type: str, conversation_history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Step 2: Extract parameters and generate dynamic response."""
        try:
            messages = ParameterExtractionPrompts.create_messages(user_message, widget_type, conversation_history)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for parameter extraction")
                return self._create_fallback_extraction_response(widget_type, user_message)
            
            # Clean and parse JSON response
            try:
                # Clean the response to handle markdown formatting
                cleaned_response = self._clean_json_response(response)
                data = json.loads(cleaned_response)
                
                return {
                    "intent_found": data.get("intent_found", False),
                    "widget_type": data.get("widget_type"),
                    "parameters": data.get("parameters", {}),
                    "missing_parameters": data.get("missing_parameters", []),
                    "message": data.get("message", ""),
                    "confidence": data.get("confidence", 0.0)
                }
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse parameter extraction response as JSON: {e}")
                logger.error(f"Raw response: {response}")
                logger.error(f"Cleaned response: {cleaned_response if 'cleaned_response' in locals() else 'N/A'}")
                return self._create_fallback_extraction_response(widget_type, user_message)
                
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            return self._create_fallback_extraction_response(widget_type, user_message)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response to handle markdown formatting and other issues."""
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = response.strip()
        
        # Remove ```json and ``` markers
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        # Try to find JSON object boundaries
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx + 1]
        
        return response
    
    def _create_fallback_extraction_response(self, widget_type: str, user_message: str) -> Dict[str, Any]:
        """Create a fallback response when parameter extraction fails."""
        # Define required parameters for each widget type
        required_params = {
            "todo-task": ["title", "due_date"],
            "todo-habit": ["title"],
            "alarm": ["title", "alarm_time"],
            "singleitemtracker": ["title", "value_unit", "target_value"],
            "websearch": ["title"]
        }
        
        # Generate a comprehensive fallback message based on widget type
        fallback_messages = {
            "todo-task": "I'll help you create a task. I need a title for the task and when it's due. For example: 'Submit project report' and 'by Friday' or 'in 2 weeks'.",
            "todo-habit": "I'll help you create a habit. What should I call it? For example: 'Exercise daily' or 'Read 30 minutes'.",
            "alarm": "I'll help you create an alarm. I need a title for the alarm and what time it should go off. For example: 'Wake up' and '6 AM' or 'Take medication' and '9 PM'.",
            "singleitemtracker": "I'll help you create a tracker. I need a title, what unit to track in, and your target value. For example: 'Weight tracker', 'kg', and '70' or 'Mood tracker', 'scale 1-10', and '8'.",
            "websearch": "I'll help you create a web search. What should I call it? For example: 'Research AI companies' or 'Find productivity apps'."
        }
        
        message = fallback_messages.get(widget_type, "I'll help you create a widget. What should I call it?")
        missing_params = required_params.get(widget_type, ["title"])
        
        return {
            "intent_found": True,
            "widget_type": widget_type,
            "parameters": {},
            "missing_parameters": missing_params,
            "message": message,
            "confidence": 0.7
        }
    
    async def _generate_dynamic_fallback_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate dynamic fallback response when no widget type is recognized."""
        try:
            # Create a simple prompt for generating fallback response
            system_prompt = """You are a helpful AI assistant for Brainboard dashboard. 

The user's message doesn't seem to be about creating a widget. Generate a natural, helpful response that:

1. Acknowledges their message briefly
2. Explains what you can help with (widget creation)
3. Provides 2-3 examples of what they can ask for

Be conversational and helpful. Keep it under 3 sentences. Don't use JSON formatting."""

            # Build conversation context
            conversation_text = ""
            if conversation_history:
                for msg in conversation_history[-2:]:  # Last 2 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_text += f"{role}: {msg['content']}\n"
            
            conversation_text += f"User: {user_message}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation_text}
            ]
            
            response = await self.llm_client.call_openai(messages)
            
            if response and response.strip():
                return {
                    "intent_found": False,
                    "widget_type": None,
                    "parameters": {},
                    "missing_parameters": [],
                    "message": response.strip(),
                    "confidence": 0.0
                }
            else:
                # Fallback to hardcoded response if AI fails
                return {
                    "intent_found": False,
                    "widget_type": None,
                    "parameters": {},
                    "missing_parameters": [],
                    "message": "I can help you create widgets for your dashboard! You can create todo tasks, habits, alarms, trackers, or web search widgets. What would you like to create?",
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error generating dynamic fallback response: {e}")
            return {
                "intent_found": False,
                "widget_type": None,
                "parameters": {},
                "missing_parameters": [],
                "message": "I can help you create widgets for your dashboard! You can create todo tasks, habits, alarms, trackers, or web search widgets. What would you like to create?",
                "confidence": 0.0
            }
    
    async def extract_parameters(
        self, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> Optional[ParameterExtractionResponse]:
        """Extract parameters from follow-up message using legacy approach for backward compatibility."""
        try:
            messages = LegacyParameterExtractionPrompts.create_messages(
                user_message, current_intent, existing_parameters, missing_parameters
            )
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for parameter extraction")
                return None
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return ParameterExtractionResponse(
                    updated_parameters=data.get("updated_parameters", {}),
                    missing_parameters=data.get("missing_parameters", []),
                    confidence=data.get("confidence", 0.0),
                    reasoning=data.get("reasoning", "")
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            return None
    
    async def generate_followup_question(
        self, 
        intent: str, 
        missing_parameters: List[str], 
        current_context: str = ""
    ) -> Optional[str]:
        """Generate follow-up question for missing information."""
        try:
            messages = FollowupQuestionPrompts.create_messages(intent, missing_parameters, current_context)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for follow-up question")
                return None
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None
    
    async def generate_confirmation(self, intent: str, result: Dict[str, Any]) -> Optional[str]:
        """Generate confirmation message for successful widget creation."""
        try:
            if result.get("success"):
                messages = ConfirmationMessagePrompts.create_success_messages(intent, result)
            else:
                messages = ConfirmationMessagePrompts.create_error_messages(intent, result.get("message", ""))
            
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for confirmation")
                return None
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating confirmation: {e}")
            return None
    
    def get_fallback_message(self, attempt: int) -> str:
        """Get fallback message for specific attempt number (deprecated - using dynamic responses)."""
        # This method is kept for backward compatibility but should not be used
        fallback_messages = {
            1: "I'm having trouble understanding. Could you try rephrasing your request?",
            2: "I'm still not sure what you need. Can you be more specific?",
            3: "Let me try a different approach. What exactly would you like to create?"
        }
        return fallback_messages.get(attempt, fallback_messages[3]) 