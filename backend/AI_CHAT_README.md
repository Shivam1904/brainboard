# AI Chat Functionality

## Overview

This implementation provides an AI-powered chat interface that allows users to create and manage alarms through natural language conversation. The system uses OpenAI's LLM for intent recognition and parameter extraction, with a robust fallback mechanism and session-based conversation memory.

## Features

### 🎯 Core Functionality
- **Natural Language Processing**: Understand user intents through OpenAI LLM
- **Multi-turn Conversations**: Session-based memory with 30-minute timeout
- **Parameter Extraction**: Extract alarm parameters from natural language
- **Fallback Mechanism**: Multiple attempts for intent recognition with graceful degradation
- **Tool Integration**: Seamless integration with existing AlarmService

### 🔄 Conversation Flow
1. **Intent Recognition**: Analyze user message for intent (create_alarm, edit_alarm, delete_alarm, list_alarms)
2. **Parameter Extraction**: Extract relevant parameters (title, alarm_times, description, etc.)
3. **Validation**: Check for required parameters
4. **Follow-up Questions**: Ask for missing information if needed
5. **Tool Execution**: Execute alarm operations using existing services
6. **Confirmation**: Provide natural language confirmation

### 🛡️ Fallback Mechanism
- **Multiple Attempts**: Up to 3 attempts for intent recognition
- **Progressive Guidance**: Each attempt provides more specific instructions
- **Graceful Degradation**: Falls back to manual form if AI fails
- **Error Handling**: Comprehensive error handling and user feedback

## Architecture

### Directory Structure
```
backend/
├── ai_engine/                    # AI-specific code
│   ├── models/                   # Data models
│   │   ├── llm_client.py        # OpenAI client wrapper
│   │   ├── session_memory.py    # Session data structures
│   │   └── intent_models.py     # Intent response models
│   ├── prompts/                  # Prompt templates
│   │   ├── intent_recognition.py # Intent recognition prompts
│   │   ├── parameter_extraction.py # Parameter extraction prompts
│   │   ├── followup_questions.py # Missing info prompts
│   │   └── confirmation_messages.py # Success/failure responses
│   └── tools/                    # Tool system
│       ├── base_tool.py         # Abstract tool interface
│       ├── alarm_tool.py        # Alarm creation/editing tool
│       └── tool_registry.py     # Tool management
├── orchestrators/                # Orchestration layer
│   └── chat_orchestrator.py     # Main conversation coordinator
├── services/                     # Business logic services
│   ├── ai_service.py            # OpenAI LLM interactions
│   ├── intent_service.py        # Intent recognition logic
│   └── session_service.py       # Session memory management
├── schemas/                      # API schemas
│   └── chat.py                  # Chat request/response schemas
└── routes/                       # API endpoints
    └── chat.py                  # Chat endpoint
```

### Key Components

#### 1. Chat Orchestrator (`orchestrators/chat_orchestrator.py`)
- **Purpose**: Coordinates the entire conversation flow
- **Responsibilities**:
  - Load/create session memory
  - Determine if new intent recognition needed or parameter update
  - Execute tools when parameters are complete
  - Generate appropriate responses
  - Manage session lifecycle

#### 2. AI Service (`services/ai_service.py`)
- **Purpose**: Handle all OpenAI API interactions
- **Features**:
  - Intent recognition with fallback
  - Parameter extraction from follow-up messages
  - Follow-up question generation
  - Confirmation message generation

#### 3. Session Service (`services/session_service.py`)
- **Purpose**: Manage conversation session memory
- **Features**:
  - In-memory storage with 30-minute expiration
  - Session creation, retrieval, and cleanup
  - Parameter tracking and updates

#### 4. Tool System (`ai_engine/tools/`)
- **Purpose**: Execute business logic operations
- **Features**:
  - Abstract tool interface
  - Alarm tool for CRUD operations
  - Tool registry for management
  - Parameter validation

## API Endpoints

### POST `/api/v1/chat/message`
Process a chat message and return AI response.

**Request:**
```json
{
    "message": "Set an alarm for 7 AM",
    "session_id": null,
    "user_id": "user_001"
}
```

**Response:**
```json
{
    "message": "What should I call this alarm?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_complete": false,
    "intent": "create_alarm",
    "missing_parameters": ["title"]
}
```

### GET `/api/v1/chat/sessions`
List all active chat sessions.

### GET `/api/v1/chat/sessions/{session_id}`
Get information about a specific session.

### DELETE `/api/v1/chat/sessions/{session_id}`
Clear a specific session.

### POST `/api/v1/chat/cleanup`
Clean up expired sessions.

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional (with defaults)
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=150
OPENAI_RETRY_ATTEMPTS=3
SESSION_TIMEOUT_MINUTES=30
```

### OpenAI Settings
- **Model**: gpt-3.5-turbo (cost-efficient)
- **Temperature**: 0.7 (creative responses)
- **Max Tokens**: 150 (concise replies)
- **Retry Attempts**: 3 (for reliability)

## Usage Examples

### Example 1: Complete Information
```
User: "Set an alarm for 7 AM called Wake up"
AI: "Perfect! I've created your 'Wake up' alarm for 7:00 AM."
```

### Example 2: Incomplete Information
```
User: "Set an alarm for 7 AM"
AI: "What should I call this alarm?"
User: "Wake up"
AI: "Perfect! I've created your 'Wake up' alarm for 7:00 AM."
```

### Example 3: Very Incomplete Information
```
User: "Set an alarm"
AI: "What time should the alarm ring?"
User: "7 AM"
AI: "What should I call this alarm?"
User: "Wake up"
AI: "Perfect! I've created your 'Wake up' alarm for 7:00 AM."
```

### Example 4: Fallback Scenario
```
User: "blah blah blah"
AI: "I'm having trouble understanding your request. Let me try a different approach..."
User: "I want to create an alarm"
AI: "What time should the alarm ring?"
```

## Testing

### Run Architecture Test
```bash
python test_chat.py
```

### Test API Endpoints
```bash
# Start the server
python main.py

# Test chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Set an alarm for 7 AM",
    "user_id": "user_001"
  }'
```

## Error Handling

### Session Management
- Auto-expire sessions after 30 minutes
- Handle corrupted session data gracefully
- Provide session reset capability

### LLM Failures
- Retry logic for transient API failures
- Fallback to simple responses if AI unavailable
- Log all AI interactions for debugging

### Tool Execution Failures
- Clear error messages for validation failures
- Graceful handling of service errors
- User-friendly error explanations

### Conversation Limits
- Maximum 3 attempts for missing information
- Clear escalation path to manual form
- User ability to cancel conversation

## Integration Points

### Existing Services
- **AlarmService**: Used for alarm CRUD operations
- **Database Models**: Uses existing AlarmDetails and DashboardWidgetDetails
- **Validation**: Leverages existing error handling patterns

### Dependencies
- **OpenAI Python Library**: For LLM API calls
- **UUID Generation**: For session IDs
- **DateTime Handling**: For session expiration

## Future Enhancements

### Planned Features
- **Multi-widget Support**: Extend to other widget types (todos, reminders, etc.)
- **Voice Integration**: Add voice input/output capabilities
- **Advanced Context**: Better conversation context understanding
- **User Preferences**: Learn from user behavior and preferences
- **Analytics**: Track conversation success rates and user satisfaction

### Extensibility
- **New Intents**: Easy addition of new conversation intents
- **New Tools**: Simple tool registration system
- **Custom Prompts**: Configurable prompt templates
- **Multiple LLM Providers**: Support for other LLM providers

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   - Set `OPENAI_API_KEY` environment variable
   - Verify API key is valid and has sufficient credits

2. **Session Expiration**
   - Sessions auto-expire after 30 minutes
   - Use session management endpoints to debug

3. **Intent Recognition Failures**
   - Check OpenAI API status
   - Review conversation logs
   - Verify prompt templates

4. **Tool Execution Errors**
   - Check database connectivity
   - Verify AlarmService integration
   - Review parameter validation

### Debugging

1. **Enable Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Session State**
   ```bash
   curl "http://localhost:8000/api/v1/chat/sessions"
   ```

3. **Review Conversation History**
   ```bash
   curl "http://localhost:8000/api/v1/chat/sessions/{session_id}"
   ```

## Contributing

### Development Guidelines
- Follow existing code patterns and structure
- Add comprehensive error handling
- Include unit tests for new features
- Update documentation for API changes
- Use type hints and docstrings

### Testing Strategy
- Unit tests for individual components
- Integration tests for conversation flows
- API tests for endpoint functionality
- Load tests for session management

This implementation provides a robust, scalable foundation for AI-powered conversation management with comprehensive error handling, fallback mechanisms, and extensible architecture. 