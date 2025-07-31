"""
Intent service for intent recognition and parameter extraction.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, List, Optional
from .ai_service import AIService
from ai_engine.models.intent_models import IntentResponse, ParameterExtractionResponse

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Supported intents
SUPPORTED_INTENTS = ["create_alarm", "edit_alarm", "delete_alarm", "list_alarms"]

# Required parameters for each intent
REQUIRED_PARAMETERS = {
    "create_alarm": ["title", "alarm_times"],
    "edit_alarm": ["widget_id"],
    "delete_alarm": ["widget_id"],
    "list_alarms": []
}

# ============================================================================
# INTENT SERVICE CLASS
# ============================================================================
class IntentService:
    """Service for intent recognition and parameter extraction."""
    
    def __init__(self):
        """Initialize the intent service."""
        self.ai_service = AIService()
    
    async def recognize_intent(self, user_message: str, fallback_attempt: int = 0) -> Optional[IntentResponse]:
        """Recognize user intent with fallback mechanism."""
        try:
            # Try AI-based intent recognition
            intent_response = await self.ai_service.recognize_intent(user_message, fallback_attempt)
            
            if not intent_response:
                logger.warning("AI intent recognition failed, using fallback")
                return self._create_fallback_response(fallback_attempt)
            
            # Validate intent
            if intent_response.intent not in SUPPORTED_INTENTS and intent_response.intent != "unknown":
                logger.warning(f"Unsupported intent: {intent_response.intent}")
                intent_response.intent = "unknown"
                intent_response.confidence = 0.0
            
            return intent_response
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return self._create_fallback_response(fallback_attempt)
    
    def _create_fallback_response(self, fallback_attempt: int) -> IntentResponse:
        """Create a fallback response when AI recognition fails."""
        return IntentResponse(
            intent="unknown",
            confidence=0.0,
            parameters={},
            reasoning="AI recognition failed, using fallback",
            is_fallback=True,
            fallback_attempt=fallback_attempt
        )
    
    async def extract_parameters(
        self, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> Optional[ParameterExtractionResponse]:
        """Extract parameters from follow-up message."""
        try:
            if current_intent not in SUPPORTED_INTENTS:
                logger.warning(f"Unsupported intent for parameter extraction: {current_intent}")
                return None
            
            return await self.ai_service.extract_parameters(
                user_message, current_intent, existing_parameters, missing_parameters
            )
            
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            return None
    
    def get_missing_parameters(self, intent: str, filled_parameters: Dict[str, Any]) -> List[str]:
        """Get list of missing required parameters for an intent."""
        if intent not in REQUIRED_PARAMETERS:
            return []
        
        required = REQUIRED_PARAMETERS[intent]
        missing = []
        
        for param in required:
            if param not in filled_parameters or filled_parameters[param] is None:
                missing.append(param)
        
        return missing
    
    def validate_parameters(self, intent: str, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate that all required parameters are present."""
        missing = self.get_missing_parameters(intent, parameters)
        return len(missing) == 0, missing
    
    def is_intent_supported(self, intent: str) -> bool:
        """Check if intent is supported."""
        return intent in SUPPORTED_INTENTS
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return SUPPORTED_INTENTS.copy()
    
    def get_required_parameters_for_intent(self, intent: str) -> List[str]:
        """Get required parameters for a specific intent."""
        return REQUIRED_PARAMETERS.get(intent, []).copy() 