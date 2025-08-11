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

# Supported widget types
SUPPORTED_WIDGET_TYPES = ["todo-task", "todo-habit", "alarm", "singleitemtracker", "websearch", "notes"]

# Required parameters for each widget type
REQUIRED_PARAMETERS = {
    "todo-task": ["title", "due_date"],
    "todo-habit": ["title"],
    "alarm": ["title", "alarm_time"],
    "singleitemtracker": ["title", "value_unit", "target_value"],
    "websearch": ["title"],
    "notes": ["title"]
}

# ============================================================================
# INTENT SERVICE CLASS
# ============================================================================
class IntentService:
    """Service for intent recognition and parameter extraction."""
    
    def __init__(self):
        """Initialize the intent service."""
        self.ai_service = AIService()
    
    async def recognize_intent(self, user_message: str, fallback_attempt: int = 0, conversation_history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Recognize user intent with fallback mechanism."""
        try:
            # Try AI-based intent recognition with conversation history
            intent_response = await self.ai_service.recognize_intent(user_message, fallback_attempt, conversation_history)
            
            if not intent_response:
                logger.warning("AI intent recognition failed, using fallback")
                return self._create_fallback_response(fallback_attempt)
            
            # Validate widget type
            widget_type = intent_response.get("widget_type")
            if widget_type and widget_type not in SUPPORTED_WIDGET_TYPES:
                logger.warning(f"Unsupported widget type: {widget_type}")
                intent_response["intent_found"] = False
                intent_response["confidence"] = 0.0
            
            return intent_response
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return self._create_fallback_response(fallback_attempt)
    
    def _create_fallback_response(self, fallback_attempt: int) -> Dict[str, Any]:
        """Create a fallback response when AI recognition fails."""
        return {
            "intent_found": False,
            "widget_type": None,
            "parameters": {},
            "missing_parameters": [],
            "message": "AI recognition failed, using fallback",
            "confidence": 0.0,
            "fallback_attempt": fallback_attempt
        }
    
    async def extract_parameters(
        self, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> Optional[ParameterExtractionResponse]:
        """Extract parameters from follow-up message."""
        try:
            # Extract widget type from intent (e.g., "create_todo-task" -> "todo-task")
            widget_type = current_intent.replace("create_", "") if current_intent.startswith("create_") else None
            
            if not widget_type or widget_type not in SUPPORTED_WIDGET_TYPES:
                logger.warning(f"Unsupported widget type for parameter extraction: {widget_type}")
                return None
            
            return await self.ai_service.extract_parameters(
                user_message, current_intent, existing_parameters, missing_parameters
            )
            
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            return None
    
    def get_missing_parameters(self, intent: str, filled_parameters: Dict[str, Any]) -> List[str]:
        """Get list of missing required parameters for an intent."""
        # Extract widget type from intent
        widget_type = intent.replace("create_", "") if intent.startswith("create_") else None
        
        if not widget_type or widget_type not in REQUIRED_PARAMETERS:
            return []
        
        required = REQUIRED_PARAMETERS[widget_type]
        missing = []
        
        for param in required:
            value = filled_parameters.get(param)
            # Check if parameter is missing, None, empty string, or empty list
            if (param not in filled_parameters or 
                value is None or 
                value == "" or 
                (isinstance(value, list) and len(value) == 0)):
                missing.append(param)
        
        return missing
    
    def validate_parameters(self, intent: str, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate that all required parameters are present."""
        missing = self.get_missing_parameters(intent, parameters)
        return len(missing) == 0, missing
    
    def is_widget_type_supported(self, widget_type: str) -> bool:
        """Check if widget type is supported."""
        return widget_type in SUPPORTED_WIDGET_TYPES
    
    def get_supported_widget_types(self) -> List[str]:
        """Get list of supported widget types."""
        return SUPPORTED_WIDGET_TYPES.copy()
    
    def get_required_parameters_for_widget_type(self, widget_type: str) -> List[str]:
        """Get required parameters for a specific widget type."""
        return REQUIRED_PARAMETERS.get(widget_type, []).copy() 