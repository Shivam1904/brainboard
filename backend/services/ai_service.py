"""
AI service for OpenAI LLM interactions.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import json
import logging
from typing import Dict, Any, List, Optional
from ai_engine.models.llm_client import LLMClient
from ai_engine.prompts.intent_recognition import IntentRecognitionPrompts
from ai_engine.prompts.parameter_extraction import ParameterExtractionPrompts
from ai_engine.prompts.followup_questions import FollowupQuestionPrompts
from ai_engine.prompts.confirmation_messages import ConfirmationMessagePrompts
from ai_engine.models.intent_models import IntentResponse, ParameterExtractionResponse

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
    
    async def recognize_intent(self, user_message: str, fallback_attempt: int = 0) -> Optional[IntentResponse]:
        """Recognize user intent from message."""
        try:
            messages = IntentRecognitionPrompts.create_messages(user_message, fallback_attempt)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for intent recognition")
                return None
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return IntentResponse(
                    intent=data.get("intent", "unknown"),
                    confidence=data.get("confidence", 0.0),
                    parameters=data.get("parameters", {}),
                    reasoning=data.get("reasoning", ""),
                    is_fallback=fallback_attempt > 0,
                    fallback_attempt=fallback_attempt
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return None
    
    async def extract_parameters(
        self, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> Optional[ParameterExtractionResponse]:
        """Extract parameters from follow-up message."""
        try:
            messages = ParameterExtractionPrompts.create_messages(
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
        """Generate confirmation message for successful operation."""
        try:
            if result.get("success"):
                messages = ConfirmationMessagePrompts.create_success_messages(intent, result)
            else:
                messages = ConfirmationMessagePrompts.create_error_messages(intent, result.get("message", ""))
            
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for confirmation message")
                return None
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating confirmation message: {e}")
            return None
    
    def get_fallback_message(self, attempt: int) -> str:
        """Get predefined fallback message."""
        from ai_engine.prompts.intent_recognition import IntentRecognitionPrompts
        return IntentRecognitionPrompts.get_fallback_prompt(attempt) 