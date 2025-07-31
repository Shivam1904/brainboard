# AI Chat Implementation Plan

## Overview
Build an AI-powered chat interface that allows users to create and manage alarms through natural language conversation using OpenAI LLM with intent recognition and multi-turn conversation support.

## Technical Specifications
- **LLM Provider**: OpenAI
- **Scope**: Alarm widgets only (expandable to other widgets later)
- **Memory**: Session-based conversation memory (30-minute timeout)
- **Fallback**: Maximum 3 attempts for missing information
- **Response Format**: JSON API responses
- **Architecture**: Uses existing AlarmService, adds orchestration layer

## Implementation Requirements

### 1. File Structure to Create

```
backend/
├── routes/
│   └── chat.py                     # NEW: AI Chat endpoint
├── orchestrators/                  # NEW: Orchestration layer
│   ├── __init__.py
│   └── chat_orchestrator.py        # Main conversation coordinator
├── services/
│   ├── ai_service.py               # NEW: OpenAI LLM integration
│   ├── intent_service.py           # NEW: Intent recognition logic
│   └── session_service.py          # NEW: Session memory management
├── ai_engine/                      # NEW: AI-specific code
│   ├── __init__.py
│   ├── prompts/
│   │   ├── intent_recognition.py   # Intent recognition prompts
│   │   ├── parameter_extraction.py # Parameter extraction prompts
│   │   ├── followup_questions.py   # Missing info prompts
│   │   └── confirmation_messages.py # Success/failure responses
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py            # Abstract tool interface
│   │   ├── alarm_tool.py           # Alarm creation/editing tool
│   │   └── tool_registry.py        # Tool management
│   └── models/
│       ├── session_memory.py       # Session data structures
│       ├── intent_models.py        # Intent response models
│       └── llm_client.py           # OpenAI client wrapper
├── schemas/
│   └── chat.py                     # NEW: Chat request/response schemas
```

### 2. Core Components to Implement

#### A. Chat Endpoint (`routes/chat.py`)
- **Endpoint**: `POST /api/v1/chat/message`
- **Function**: Accept user messages and return AI responses
- **Integration**: Use chat_orchestrator for processing
- **Error Handling**: Graceful fallbacks for AI service failures

#### B. Chat Orchestrator (`orchestrators/chat_orchestrator.py`)
- **Purpose**: Coordinate the entire conversation flow
- **Responsibilities**:
  - Load/create session memory
  - Determine if new intent recognition needed or parameter update
  - Execute tools when parameters are complete
  - Generate appropriate responses (success confirmation or follow-up questions)
  - Manage session lifecycle

#### C. Session Service (`services/session_service.py`)
- **Storage**: In-memory with 30-minute expiration
- **Data Structure**: Store current intent, filled parameters, pending parameters, conversation history
- **Methods**: get_or_create, save, clear, cleanup_expired

#### D. Intent Service (`services/intent_service.py`)
- **Purpose**: Use OpenAI to recognize user intents and extract parameters
- **Methods**:
  - `recognize_intent()`: Analyze new messages for intent
  - `extract_parameters()`: Update parameters from follow-up messages
- **Supported Intents**: create_alarm, edit_alarm, delete_alarm, list_alarms

#### E. AI Service (`services/ai_service.py`)
- **Purpose**: Handle all OpenAI API interactions
- **Methods**:
  - `generate_followup_question()`: Create natural language prompts for missing info
  - `generate_confirmation()`: Create success/failure messages
  - `call_openai()`: Generic OpenAI API wrapper with error handling

#### F. Tool System (`ai_engine/tools/`)
- **Base Tool**: Abstract interface with validate_parameters() and execute() methods
- **Alarm Tool**: Implement alarm creation using existing AlarmService
- **Tool Registry**: Manage and execute tools by intent name
- **Validation**: Check for required vs optional parameters

#### G. LLM Client (`ai_engine/models/llm_client.py`)
- **Purpose**: OpenAI API client with configuration
- **Features**: Token management, error handling, retry logic
- **Configuration**: Model selection, temperature, max tokens

### 3. Data Models and Schemas

#### Session Memory Structure
```python
{
  "session_id": "uuid",
  "user_id": "user_001",
  "current_intent": "create_alarm",
  "filled_params": {
    "title": "Wake up",
    "alarm_times": ["07:00"],
    "description": null
  },
  "pending_params": ["description"],
  "original_message": "Set an alarm for 7 AM",
  "conversation_history": [...],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Chat API Schemas
- **ChatRequest**: message, session_id (optional), user_id
- **ChatResponse**: message, is_complete, session_id, intent, created_resource
- **SessionInfo**: session details for debugging

### 4. Conversation Flow Logic

#### New Conversation Flow:
1. Receive user message
2. Use intent_service to recognize intent and extract initial parameters
3. Store in session memory
4. Attempt tool execution
5. If successful: generate confirmation and clear session
6. If missing params: generate follow-up question and save session

#### Continuing Conversation Flow:
1. Receive user message with existing session_id
2. Load session memory
3. Use intent_service to extract additional parameters from message
4. Update session memory
5. Retry tool execution
6. Handle success/failure as above

#### Tool Execution Process:
1. Validate required parameters are present
2. If missing: return failure with missing field list
3. If complete: execute using existing AlarmService
4. Return success/failure result

### 5. Prompt Templates

#### Intent Recognition Prompt
- Input: User message
- Output: Intent, confidence, extracted parameters, reasoning
- Support: create_alarm, edit_alarm, delete_alarm, list_alarms

#### Parameter Extraction Prompt
- Input: User message, current intent, existing parameters
- Output: Updated parameters
- Purpose: Handle follow-up responses that provide missing information

#### Follow-up Question Prompt
- Input: Intent, missing parameters, current context
- Output: Natural language question
- Examples: "What should I call this alarm?" or "What time should it ring?"

#### Confirmation Message Prompt
- Input: Successful tool execution result
- Output: Natural language confirmation
- Examples: "Perfect! I've created your 'Wake up' alarm for 7:00 AM."

### 6. Integration Points

#### Reuse Existing Services
- **AlarmService**: Use existing methods for alarm CRUD operations
- **Database Models**: Use existing AlarmDetails and DashboardWidgetDetails
- **Validation**: Leverage existing error handling patterns

#### New Dependencies
- **OpenAI Python Library**: For LLM API calls
- **UUID Generation**: For session IDs
- **DateTime Handling**: For session expiration

### 7. Error Handling Strategy

#### Session Management
- Auto-expire sessions after 30 minutes
- Handle corrupted session data gracefully
- Provide session reset capability

#### LLM Failures
- Retry logic for transient API failures
- Fallback to simple responses if AI unavailable
- Log all AI interactions for debugging

#### Tool Execution Failures
- Clear error messages for validation failures
- Graceful handling of service errors
- User-friendly error explanations

#### Conversation Limits
- Maximum 3 attempts for missing information
- Clear escalation path to manual form
- User ability to cancel conversation

### 8. Testing Requirements

#### Unit Tests
- Intent recognition accuracy
- Parameter extraction logic
- Tool validation and execution
- Session memory operations

#### Integration Tests
- Full conversation flows
- Error handling scenarios
- Session expiration handling
- OpenAI API integration

#### End-to-End Tests
- Complete alarm creation via chat
- Multi-turn conversations
- Edge cases and error conditions

### 9. Configuration

#### Environment Variables
- `OPENAI_API_KEY`: OpenAI API authentication
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)
- `SESSION_TIMEOUT_MINUTES`: Session expiration (default: 30)
- `MAX_CONVERSATION_ATTEMPTS`: Fallback limit (default: 3)

#### OpenAI Settings
- Temperature: 0.7 for creative responses
- Max tokens: 150 for concise replies
- Model: gpt-3.5-turbo for cost efficiency

### 10. Success Criteria

#### Functional Requirements
- User can create alarms through natural language
- System properly handles missing information with follow-up questions
- Session memory works across multiple message exchanges
- Integration with existing alarm service is seamless
- Error handling provides clear user feedback

#### Example Success Flow
```
User: "Set an alarm"
System: "What should I call this alarm and what time should it ring?"
User: "Wake up at 7 AM"
System: "Perfect! I've created your 'Wake up' alarm for 7:00 AM."
```

#### Technical Requirements
- Response time under 3 seconds
- Proper error handling for all failure modes
- Clean separation between AI logic and business logic
- Extensible architecture for future widget types
- Comprehensive logging for debugging

## Implementation Notes

### Architecture Principles
- **Separation of Concerns**: Keep AI logic separate from business logic
- **Reusability**: Leverage existing services without modification
- **Extensibility**: Design for easy addition of other widget types
- **Testability**: Each component should be independently testable

### Code Organization
- Use existing patterns for imports, constants, and code structure
- Follow the established file header format with sections
- Implement proper error handling using existing utils/errors.py
- Use Pydantic models for all data validation

### Dependencies
- Add OpenAI to conda_environment.yml
- Use existing FastAPI patterns for route definition
- Leverage existing database session management
- Follow established async/await patterns

This plan provides the foundation for implementing AI chat functionality that integrates seamlessly with the existing backend architecture while providing a natural language interface for alarm management. 