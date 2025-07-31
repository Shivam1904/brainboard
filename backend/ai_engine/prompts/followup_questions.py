"""
Follow-up question prompts for missing information.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import List

# ============================================================================
# FOLLOW-UP QUESTION PROMPTS
# ============================================================================
class FollowupQuestionPrompts:
    """Prompts for generating follow-up questions for missing information."""
    
    SYSTEM_PROMPT = """You are a helpful AI assistant that asks follow-up questions to gather missing information for alarm creation.

Your job is to generate natural, conversational questions to get the missing parameters from the user.

TONE: Friendly, helpful, and conversational. Don't be robotic.

RESPONSE FORMAT:
Return only the question text, no JSON or additional formatting.

EXAMPLES:
- "What should I call this alarm?"
- "What time should it ring?"
- "Would you like to add a description to this alarm?"
- "Should this alarm be snoozable?" """

    @classmethod
    def create_messages(cls, intent: str, missing_parameters: List[str], current_context: str = "") -> List[dict]:
        """Create messages for follow-up question generation."""
        
        context = f"""Intent: {intent}
Missing Parameters: {missing_parameters}
Current Context: {current_context}

Generate a natural follow-up question to get the missing information. Focus on the most important missing parameter first."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
    
    @classmethod
    def get_parameter_questions(cls) -> dict:
        """Get predefined questions for common parameters."""
        return {
            "title": [
                "What should I call this alarm?",
                "What's the name for this alarm?",
                "What would you like to name this alarm?"
            ],
            "alarm_times": [
                "What time should the alarm ring?",
                "When do you want this alarm to go off?",
                "What time should I set this for?"
            ],
            "description": [
                "Would you like to add a description to this alarm?",
                "Any additional notes for this alarm?",
                "Should I add any details to this alarm?"
            ],
            "is_snoozable": [
                "Should this alarm be snoozable?",
                "Do you want to be able to snooze this alarm?",
                "Can you snooze this alarm when it rings?"
            ]
        } 