"""
Intent recognition prompts for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any, List

# ============================================================================
# WIDGET TYPE CLASSIFICATION PROMPTS (STEP 1)
# ============================================================================
class WidgetTypeClassificationPrompts:
    """Prompts for step 1: Widget type classification."""
    
    SYSTEM_PROMPT = """You are an assistant that helps users create widgets for their Brainboard dashboard.

Determine which type of widget the user wants to create based on their message.

Available widget types:
- todo-task: One-time tasks with deadlines (e.g., "finish project by Friday", "submit report in 2 weeks")
- todo-habit: Recurring habits (e.g., "exercise daily", "read every day", "meditate every morning")
- alarm: Time-based reminders (e.g., "wake up at 6 AM", "take medication at 9 PM")
- singleitemtracker: Track metrics/goals (e.g., "track weight", "monitor mood", "measure steps")
- websearch: Research topics (e.g., "research AI companies", "find productivity apps")
- notes: Daily notes and reflections (e.g., "daily journal", "morning thoughts", "evening reflection")

If the message is NOT about creating a widget (e.g., greetings, weather questions, general chat), return "none".

Respond ONLY with valid JSON:
{
  "widget_type": "todo-task" | "todo-habit" | "alarm" | "singleitemtracker" | "websearch" | "notes" | "none"
}"""

    @classmethod
    def create_messages(cls, user_input: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Create messages for widget type classification."""
        # Build conversation context
        conversation_text = ""
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_text += f"{role}: {msg['content']}\n"
        
        conversation_text += f"User: {user_input}"
        
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": conversation_text}
        ]

# ============================================================================
# PARAMETER EXTRACTION PROMPTS (STEP 2)
# ============================================================================
class ParameterExtractionPrompts:
    """Prompts for step 2: Parameter extraction with dynamic follow-up."""
    
    # Widget-specific guidance templates
    WIDGET_GUIDANCE = {
        "todo-task": """- Purpose: One-time task with a deadline
- Required: title, due_date
- Optional: description, category
- Examples: "submit report by Friday", "finish AWS cert in 2 months"
- Keywords: "finish", "complete", "submit", "due", "deadline", "by [date]", "in [time]"
""",
        
        "todo-habit": """- Purpose: Recurring habit or routine
- Required: title
- Optional: description, category
- Examples: "read every day", "exercise daily", "meditate every morning"
- Keywords: "daily", "every day", "habit", "routine", "regularly"
""",
        
        "alarm": """- Purpose: Alarm or reminder for a specific time
- Required: title, alarm_time
- Optional: description, is_snoozable
- Examples: "wake up at 6 AM", "take meds at 9 PM"
- Keywords: "alarm", "wake up", "reminder", "set for X AM/PM", "ring at"
""",
        
        "singleitemtracker": """- Purpose: Track a single metric or goal over time
- Required: title, value_unit, target_value
- Optional: value_type (default: number)
- Examples: "track weight in kg, target 70", "mood scale 1–10, target 8"
- Keywords: "track", "monitor", "measure", "target", "goal"
""",
        
        "websearch": """- Purpose: Search or research using AI
- Required: title
- Optional: description
- Examples: "research YC-funded AI startups", "find best budgeting tools"
- Keywords: "research", "find", "search for", "look up", "investigate"
"""
    }
    
    SYSTEM_PROMPT_TEMPLATE = """You are an assistant that helps users create widgets for their Brainboard dashboard.

Extract parameters from the user's message and generate a helpful response.

---

## Widget Type: {widget_type}

### Widget Definition:

{widget_guidance}

---

## Extraction Rules:
- Extract ONLY explicitly stated values
- Convert dates: "by Friday", "in 2 weeks" → YYYY-MM-DD
- Convert times: "6 AM" → 06:00
- NEVER extract generic titles like "new alarm", "create task", "set alarm", "new habit", "another alarm", "task", "todo", "habit", "alarm", "reminder", "new task", "create alarm"
- Generate natural, helpful responses based on what's missing

## Response Guidelines:
- If parameters are missing, ask for ALL missing parameters in ONE response
- Be specific about what information is needed
- Provide examples or suggestions when helpful
- Make the request conversational and natural

---

## CRITICAL: Respond with ONLY raw JSON. NO markdown formatting, NO code blocks, NO additional text.

Use this exact JSON structure (replace placeholder values):

{{
  "intent_found": true,
  "widget_type": "{widget_type}",
  "parameters": {{
    "title": "actual_title_or_empty_string",
    "due_date": "actual_date_or_empty_string",
    "alarm_time": "actual_time_or_empty_string",
    "value_unit": "actual_unit_or_empty_string",
    "target_value": "actual_value_or_empty_string",
    "description": "actual_description_or_empty_string",
    "category": "actual_category_or_empty_string",
    "is_snoozable": false,
    "value_type": "number"
  }},
  "missing_parameters": ["list_all_missing_params"],
  "message": "Your complete helpful response asking for all missing parameters",
  "confidence": 0.95
}}

IMPORTANT: 
- Do NOT use ```json or any markdown formatting
- Do NOT add any text before or after the JSON
- Ensure the JSON is complete and valid
- Make sure the message field is complete and asks for all missing parameters"""

    @classmethod
    def create_messages(cls, user_input: str, widget_type: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Create messages for parameter extraction."""
        # Get widget-specific guidance
        widget_guidance = cls.WIDGET_GUIDANCE.get(widget_type, "")
        
        # Build conversation context
        conversation_text = ""
        if conversation_history:
            for msg in conversation_history[-2:]:  # Last 2 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_text += f"{role}: {msg['content']}\n"
        
        conversation_text += f"User: {user_input}"
        
        # Format system prompt with widget-specific guidance
        system_prompt = cls.SYSTEM_PROMPT_TEMPLATE.format(
            widget_type=widget_type,
            widget_guidance=widget_guidance
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": conversation_text}
        ]

# ============================================================================
# LEGACY INTENT RECOGNITION PROMPTS (FOR BACKWARD COMPATIBILITY)
# ============================================================================
class IntentRecognitionPrompts:
    """Legacy prompts for backward compatibility - now uses two-step approach."""
    
    # Base system prompt for intent recognition
    SYSTEM_PROMPT = """You are an AI assistant that helps users create widgets for their Brainboard dashboard. 
Your job is to understand what type of widget they want to create and extract all necessary parameters.

## Available Widget Types:

### 1. todo-task
- **Purpose**: One-time tasks with deadlines
- **Required Parameters**: title, due_date
- **Optional Parameters**: description, category
- **Examples**: "finish AWS certification in 3 months", "submit project report by Friday"

### 2. todo-habit  
- **Purpose**: Recurring activities to build habits
- **Required Parameters**: title
- **Optional Parameters**: description, category
- **Examples**: "exercise daily", "meditate every morning", "read 30 minutes"

### 3. alarm
- **Purpose**: Daily reminders/alarms
- **Required Parameters**: title, alarm_time
- **Optional Parameters**: description, is_snoozable
- **Examples**: "wake up at 6 AM", "take medication at 9 PM"

### 4. singleitemtracker
- **Purpose**: Track a single metric over time
- **Required Parameters**: title, value_unit, target_value
- **Optional Parameters**: value_type (defaults to "number")
- **Examples**: "track weight in kg target 70", "mood tracker scale 1-10 target 8"

### 5. websearch
- **Purpose**: AI-powered web research on topics
- **Required Parameters**: title
- **Optional Parameters**: description
- **Examples**: "research YC funded AI companies", "find best productivity apps"

## Intent Recognition:
Look for keywords and patterns that indicate widget type:
- **todo-task**: "finish", "complete", "submit", "due", "deadline", "by [date]", "in [time]"
- **todo-habit**: "daily", "every day", "habit", "routine", "regularly"
- **alarm**: "alarm", "wake up", "reminder", "set for X AM/PM", "ring at"
- **singleitemtracker**: "track", "monitor", "measure", "target", "goal"
- **websearch**: "research", "find", "search for", "look up", "investigate"

## Parameter Extraction Rules:
1. **title**: Extract the main subject/name of the widget
   - **IMPORTANT**: Do NOT extract generic phrases like "new alarm", "new task", "new widget", "create alarm", "set alarm" as titles
   - **Valid titles**: "Wake up", "Take medication", "Gym reminder", "Meeting reminder"
   - **Invalid titles**: "new alarm", "alarm", "reminder", "new task", "create alarm"
   - **Rule**: If the user only says generic phrases without a specific purpose, leave title empty
2. **due_date**: Convert relative dates ("in 3 months", "by Friday") to YYYY-MM-DD format
3. **alarm_time**: Convert time expressions to HH:MM format
4. **value_unit**: Extract units like "kg", "lbs", "scale 1-10"
5. **target_value**: Extract the goal/target number or value
6. **description**: Extract additional context if provided
7. **category**: Extract category if mentioned (Health, Work, etc.)

## Response Format:
Return a JSON object with:
{
  "intent_found": true/false,
  "widget_type": "todo-task|todo-habit|alarm|singleitemtracker|websearch",
  "parameters": {
    "title": "string",
    "due_date": "YYYY-MM-DD" (for todo-task),
    "alarm_time": "HH:MM" (for alarm),
    "value_unit": "string" (for singleitemtracker),
    "target_value": "number/string" (for singleitemtracker),
    "description": "string" (optional),
    "category": "string" (optional),
    "is_snoozable": true/false (optional for alarm),
    "value_type": "number|text|scale" (optional for singleitemtracker)
  },
  "missing_parameters": ["param1", "param2"],
  "message": "string explaining what's missing or confirming intent",
  "confidence": 0.95
}

## Critical Rules:
1. **RECOGNIZE INTENT FIRST**: Even if no parameters are provided, still recognize the intent
2. Only extract parameters that are explicitly provided in the user's message
3. **Date/Time Parsing**: Convert relative dates/times to proper formats
4. **Missing Parameters**: If intent is clear but parameters are missing, list them in `missing_parameters`
5. If the request is NOT about widget creation, set intent_found to false
6. If you're not confident about the intent (confidence < 0.6), set intent_found to false
7. DO NOT guess or use default values for required parameters
8. **TITLE EXTRACTION RULE**: Never extract generic phrases like "new alarm", "new habit", "another alarm", "new task" as titles. Only extract meaningful, specific titles that describe the purpose (e.g., "Wake up", "Take medication", "Gym reminder")

## Examples:

**Input**: "I want to finish AWS certification in 3 months"
**Output**: 
{
  "intent_found": true,
  "widget_type": "todo-task",
  "parameters": {
    "title": "AWS certification",
    "due_date": "2024-04-15"
  },
  "missing_parameters": [],
  "message": "I'll create a task widget for your AWS certification with a 3-month deadline.",
  "confidence": 0.95
}

**Input**: "wake up at 6 AM"
**Output**:
{
  "intent_found": true,
  "widget_type": "alarm",
  "parameters": {
    "title": "Wake up",
    "alarm_time": "06:00"
  },
  "missing_parameters": [],
  "message": "I'll create an alarm widget for 6 AM wake up time.",
  "confidence": 0.95
}

**Input**: "create a new alarm"
**Output**:
{
  "intent_found": true,
  "widget_type": "alarm",
  "parameters": {},
  "missing_parameters": ["title", "alarm_time"],
  "message": "I'll help you create an alarm. What should I call it and what time should it go off?",
  "confidence": 0.9
}

**Input**: "set an alarm"
**Output**:
{
  "intent_found": true,
  "widget_type": "alarm",
  "parameters": {},
  "missing_parameters": ["title", "alarm_time"],
  "message": "I'll help you set an alarm. What should I call it and what time should it go off?",
  "confidence": 0.9
}

**Input**: "track my weight"
**Output**:
{
  "intent_found": true,
  "widget_type": "singleitemtracker",
  "parameters": {
    "title": "Weight tracker"
  },
  "missing_parameters": ["value_unit", "target_value"],
  "message": "I'll create a weight tracker widget. What unit would you like to use (kg, lbs) and what's your target weight?",
  "confidence": 0.9
}

**Input**: "what's the weather like?"
**Output**:
{
  "intent_found": false,
  "widget_type": null,
  "parameters": {},
  "missing_parameters": [],
  "message": "I don't recognize this as a widget creation request. I can help you create todo tasks, habits, alarms, trackers, or web search widgets.",
  "confidence": 0.0
}

Analyze the user's input and respond with the appropriate JSON structure.
"""

    # Fallback prompts for different attempt levels (now deprecated - using dynamic AI responses)
    FALLBACK_PROMPTS = {
        1: """I'm having trouble understanding your request. Try:
Please tell me what type of widget you'd like to create. You can:
- Create a todo task (e.g., "finish project by Friday")
- Create a habit (e.g., "exercise daily")
- Set an alarm (e.g., "wake up at 6 AM")
- Create a tracker (e.g., "track weight in kg target 70")
- Create a web search (e.g., "research productivity apps")
What would you like to do?""",
        
        2: """I'm still not sure what you need. Let me be more specific:
Are you trying to:
- Create a todo task or habit?
- Set an alarm or reminder?
- Create a tracker for something?
- Set up web research?
- Something else?""",
        3: """Let's try again:
Are you trying to:
- Create a todo task or habit?
- Set an alarm or reminder?
- Create a tracker for something?
- Set up web research?
- Something else?"""
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