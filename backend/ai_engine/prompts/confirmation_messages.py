"""
Confirmation message prompts for success/failure responses.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, List

# ============================================================================
# CONFIRMATION MESSAGE PROMPTS
# ============================================================================
class ConfirmationMessagePrompts:
    """Prompts for generating confirmation messages."""
    
    SYSTEM_PROMPT = """You are a helpful AI assistant that provides confirmation messages for alarm operations.

Your job is to generate natural, friendly confirmation messages when operations succeed or fail.

TONE: Friendly, helpful, and conversational. Be encouraging and clear.

RESPONSE FORMAT:
Return only the confirmation message text, no JSON or additional formatting.

EXAMPLES:
- "Perfect! I've created your 'Wake up' alarm for 7:00 AM."
- "Great! Your alarm has been updated successfully."
- "I've deleted your morning alarm as requested."
- "Here are your current alarms: [list]"
- "I'm sorry, but I couldn't create the alarm. Please try again." """

    @classmethod
    def create_success_messages(cls, intent: str, result: Dict[str, Any]) -> List[dict]:
        """Create messages for success confirmation."""
        
        context = f"""Intent: {intent}
Result: {result}

Generate a friendly success confirmation message."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
    
    @classmethod
    def create_error_messages(cls, intent: str, error: str) -> List[dict]:
        """Create messages for error confirmation."""
        
        context = f"""Intent: {intent}
Error: {error}

Generate a friendly error message that explains what went wrong."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
    
    @classmethod
    def get_predefined_messages(cls) -> Dict[str, str]:
        """Get predefined confirmation messages."""
        return {
            "create_alarm_success": "Perfect! I've created your alarm successfully.",
            "edit_alarm_success": "Great! Your alarm has been updated successfully.",
            "delete_alarm_success": "I've deleted your alarm as requested.",
            "list_alarms_success": "Here are your current alarms:",
            "generic_error": "I'm sorry, but something went wrong. Please try again.",
            "validation_error": "I couldn't process your request. Please check the information and try again."
        } 