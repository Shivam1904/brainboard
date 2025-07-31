"""
Intent recognition prompts for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, List

# ============================================================================
# INTENT RECOGNITION PROMPTS
# ============================================================================
class IntentRecognitionPrompts:
    """Prompts for intent recognition with fallback mechanism."""
    
    # Base system prompt for intent recognition
    SYSTEM_PROMPT = """You are an AI assistant that helps users manage alarms through natural language. 
Your job is to recognize the user's intent and extract relevant parameters from complete commands.

ALARM DETECTION:
Look for keywords like "alarm", "wake up", "reminder", "set for X AM/PM", "ring at", "morning alarm", "bedtime alarm"

SUPPORTED INTENTS:
- create_alarm: User wants to create a new alarm
- edit_alarm: User wants to modify an existing alarm
- delete_alarm: User wants to delete an alarm
- list_alarms: User wants to see their alarms

ALARM PARAMETERS:
- title: Extract from "called X", "named X", "for X", "wake up", "morning alarm"
- alarm_times: Convert time to array format - "7 AM" → ["07:00"], "8:30 PM" → ["20:30"]
- description: Extract from "with description X" or "description X"

EXAMPLES:
- "Set an alarm for 7 AM called Wake up" → intent: "create_alarm", title: "Wake up", alarm_times: ["07:00"]
- "Create an alarm for 8:30 AM named Morning Alarm" → intent: "create_alarm", title: "Morning Alarm", alarm_times: ["08:30"]
- "Set an alarm for 6 AM called Gym with description Workout reminder" → intent: "create_alarm", title: "Gym", alarm_times: ["06:00"], description: "Workout reminder"

RESPONSE FORMAT:
Return a JSON object with:
{
  "intent": "intent_name",
  "confidence": 0.95,
  "parameters": {
    "title": "alarm_title",
    "alarm_times": ["HH:MM"],
    "description": "optional_description"
  },
  "reasoning": "explanation of your classification"
}

CRITICAL RULES:
1. Only extract parameters that are explicitly provided in the user's message
2. For title: look for "called X", "named X", "for X" patterns
3. For alarm_times: convert natural language to HH:MM format in array
4. For description: look for "with description X" or "description X" patterns
5. If the request is NOT about alarms, set intent to "unknown" with confidence 0.0
6. If you're not confident about the intent (confidence < 0.7), set intent to "unknown"
7. DO NOT guess or use default values for required parameters"""

    # Fallback prompts for different attempt levels
    FALLBACK_PROMPTS = {
        1: """I'm having trouble understanding your alarm request. Let me try a different approach.
Please tell me what you'd like to do with alarms. You can:
- Create a new alarm (e.g., "Set an alarm for 7 AM")
- Edit an existing alarm (e.g., "Change my wake up alarm to 8 AM")
- Delete an alarm (e.g., "Remove my morning alarm")
- List your alarms (e.g., "Show me all my alarms")

What would you like to do?""",
        
        2: """I'm still not sure what you need. Let me be more specific:
Are you trying to:
1. Create a new alarm/reminder?
2. Change an existing alarm?
3. Delete an alarm?
4. See your current alarms?

Please respond with the number or describe what you want in simple terms.""",
        
        3: """I apologize, but I'm still having difficulty understanding your alarm request. 
Let me provide you with some clear examples:

To create an alarm: "I want to set an alarm for 6 AM tomorrow"
To edit an alarm: "Change my wake up alarm to 7 AM"
To delete an alarm: "Delete my morning alarm"
To list alarms: "Show me all my alarms"

Could you please use one of these formats or tell me what you're trying to accomplish?"""
    }
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the base system prompt for intent recognition."""
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def get_fallback_prompt(cls, attempt: int) -> str:
        """Get fallback prompt for specific attempt number."""
        return cls.FALLBACK_PROMPTS.get(attempt, cls.FALLBACK_PROMPTS[3])
    
    @classmethod
    def create_user_message(cls, user_input: str, fallback_attempt: int = 0) -> str:
        """Create user message for intent recognition."""
        if fallback_attempt == 0:
            return f"User message: {user_input}"
        else:
            fallback_text = cls.get_fallback_prompt(fallback_attempt)
            return f"Previous fallback message: {fallback_text}\n\nUser response: {user_input}"
    
    @classmethod
    def create_messages(cls, user_input: str, fallback_attempt: int = 0) -> List[Dict[str, str]]:
        """Create messages list for OpenAI API call."""
        return [
            {"role": "system", "content": cls.get_system_prompt()},
            {"role": "user", "content": cls.create_user_message(user_input, fallback_attempt)}
        ] 