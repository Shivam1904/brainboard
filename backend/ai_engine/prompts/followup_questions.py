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
- For missing title: "What should I call this alarm?"
- For missing time: "What time should the alarm ring?"
- For missing both: "What should I call this alarm and what time should it ring?"
- For missing time when title exists: "What time should the 'Wake up' alarm ring?"
- For missing title when time exists: "What should I call the 7 AM alarm?"

PRIORITY: Ask for the most critical missing parameter first. If both title and alarm_times are missing, ask for both."""

    @classmethod
    def create_messages(cls, intent: str, missing_parameters: List[str], current_context: str = "") -> List[dict]:
        """Create messages for follow-up question generation."""
        
        context = f"""Intent: {intent}
Missing Parameters: {missing_parameters}
Current Context: {current_context}

Generate a natural follow-up question to get the missing information. 

For ALARMS:
- If title and alarm_times are missing, ask for both
- If only title is missing, ask "What should I call this alarm?"
- If only alarm_times is missing, ask "What time should the alarm ring?"

Use the existing context to make the question more specific."""

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
                "When should the alarm go off?",
                "What time should I set the alarm for?"
            ],
            "description": [
                "Would you like to add a description to this alarm?",
                "Any additional notes for this alarm?",
                "Should I add any details to this alarm?"
            ]
        } 