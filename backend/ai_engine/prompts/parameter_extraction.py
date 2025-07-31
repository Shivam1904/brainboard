"""
Parameter extraction prompts for follow-up messages.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, List

# ============================================================================
# PARAMETER EXTRACTION PROMPTS
# ============================================================================
class ParameterExtractionPrompts:
    """Prompts for extracting parameters from follow-up messages."""
    
    SYSTEM_PROMPT = """You are an AI assistant that extracts parameters from user messages to complete alarm creation.

Your job is to extract missing parameters from the user's follow-up message and update the existing parameters.

ALARM PARAMETER PATTERNS:
- title: Look for "Call it X", "Name it X", "Title it X", or standalone names like "Wake up", "Morning Alarm"
- alarm_times: Convert time expressions to HH:MM format in array:
  * "7 AM" → ["07:00"]
  * "8:30 PM" → ["20:30"] 
  * "15:30" → ["15:30"]
  * "10 PM" → ["22:00"]
  * "6 AM" → ["06:00"]
- description: Look for "with description X" or "description X"

RESPONSE FORMAT:
Return a JSON object with:
{
  "updated_parameters": {
    "title": "alarm_title",
    "alarm_times": ["HH:MM"],
    "description": "optional_description"
  },
  "missing_parameters": ["param1", "param2"],
  "confidence": 0.95,
  "reasoning": "explanation of parameter extraction"
}

CRITICAL RULES:
1. Only include parameters that are actually provided or updated in the user's message
2. DO NOT guess or use default values
3. Only extract what the user actually said
4. Convert natural language time to HH:MM format in array
5. Look for explicit naming patterns or standalone values"""

    @classmethod
    def create_messages(
        cls, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> List[Dict[str, str]]:
        """Create messages for parameter extraction."""
        
        context = f"""Current Intent: {current_intent}
Existing Parameters: {existing_parameters}
Missing Parameters: {missing_parameters}
User Message: {user_message}

Extract any new or updated parameters from the user's message.

EXAMPLES:
- User says "7 AM" → extract alarm_times: ["07:00"]
- User says "8:30 PM" → extract alarm_times: ["20:30"]
- User says "15:30" → extract alarm_times: ["15:30"]
- User says "Call it Wake up" → extract title: "Wake up"
- User says "Name it Morning Alarm" → extract title: "Morning Alarm"
- User says "Wake up" → extract title: "Wake up" (if context suggests it's a title)
- User says "with description Workout reminder" → extract description: "Workout reminder"

Only extract parameters that are actually provided in the message."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ] 