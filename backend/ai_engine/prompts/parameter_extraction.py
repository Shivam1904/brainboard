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

ALARM PARAMETERS:
- title: The name/title of the alarm (required) - DO NOT use default titles like "alarm" or "Alarm"
- alarm_times: Array of times in HH:MM format (required)
- description: Optional description of the alarm
- is_snoozable: Boolean, defaults to true

IMPORTANT: If title is not provided, DO NOT create the alarm. Ask the user for the title instead.

RESPONSE FORMAT:
Return a JSON object with:
{
  "updated_parameters": {
    "title": "alarm_title",
    "alarm_times": ["HH:MM"],
    "description": "optional_description",
    "is_snoozable": true
  },
  "missing_parameters": ["param1", "param2"],
  "confidence": 0.95,
  "reasoning": "explanation of parameter extraction"
}

CRITICAL RULES:
1. Only include parameters that are actually provided or updated in the user's message
2. If title is not explicitly provided, DO NOT include it in updated_parameters
3. If alarm_times is not explicitly provided, DO NOT include it in updated_parameters
4. DO NOT guess or use default values
5. Only extract what the user actually said"""

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
If the user provides a time like "7 AM", extract it as alarm_times: ["07:00"].
If the user provides a name like "Wake up", extract it as title: "Wake up".
Only extract parameters that are actually provided in the message."""

        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ] 