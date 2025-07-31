# WebSocket Implementation Game Plan
INSTRUCTIONS FOR AI - 
to start the backend server for any reason - run the folllowing script from inside the root/backend folder:
./run_with_conda.sh server


## 🎯 **Backend WebSocket Implementation**

### 1. **Create WebSocket Router** ✅
- [x] Create `apps/backend/routers/chat.py`
- [x] Add WebSocket endpoint `/ws/chat`
- [x] Add connection management (active_connections dict)
- [x] Add error handling and disconnect logic

### 2. **Register WebSocket Router** ✅
- [x] Update `apps/backend/routers/__init__.py`
- [x] Add chat router to v1_router
- [x] Ask user to test router registration

### 3. **Create a socket manager that will recieve and send messages** ✅
- [x] Whenever websocket needs to be added, use this abstracted service

### 4. **Modify Chat Orchestrator** ✅
- [x] Add `websocket_callback` parameter to `process_message()`
- [x] Add WebSocket thinking steps in `_handle_new_conversation()`
- [x] Add WebSocket thinking steps in `_handle_continuing_conversation()`
- [x] Add WebSocket thinking steps in `_execute_tool_and_respond()`
- [x] Keep existing `session.add_message()` calls
- [x] Add WebSocket messages alongside session messages

### 5. **Add Real-time Step Updates** ✅
- [x] Session management step
- [x] Intent recognition step
- [x] Intent processing step (with fallback attempts)
- [x] Parameter extraction step
- [x] Tool execution step
- [x] Response generation step
- [x] **Actual AI Response** (final answer from orchestrator)
- [x] **Interactive Components** (if any forms/buttons needed)
- [x] **Follow-up Questions** (if more parameters needed)
- [x] Error handling step
- [x] Leave scope for more steps....

### 5. **WebSocket vs REST Strategy**
- [ ] **WebSocket for Real-time Updates:**
  - [ ] Thinking steps (intermediate progress)
  - [ ] Final AI response (actual answer)
  - [ ] Interactive components (forms, buttons, etc.)
  - [ ] Error messages (real-time error feedback)
- [ ] **REST API for:**
  - [ ] Session management (list sessions, clear sessions)
  - [ ] Health checks (connection status)
  - [ ] Fallback (when WebSocket fails)
- [ ] **Message Types via WebSocket:**
  - [ ] `thinking` - Intermediate steps
  - [ ] `response` - Final AI answer
  - [ ] `component` - Interactive forms/buttons
  - [ ] `error` - Error messages

### 6. **Connection & Session Lifecycle**
- [ ] **WebSocket Connection:**
  - [ ] **Connect**: When user opens chat widget (component mount)
      - [ ] later we will implement a better approach because the chat might remain open for long times 
      - [ ] When user send the first chat message
  - [ ] **Disconnect**: When user closes chat widget (component unmount)
  - [ ] **Reconnect**: Auto-reconnect on connection loss
      - [ ] later - When no chat has been sent for 5 minutes
  - [ ] **Keep Alive**: Maintain connection for entire chat session
- [ ] **Chat Session:**
  - [ ] **Start**: When user sends first message (orchestrator creates session)
  - [ ] **Continue**: Multiple messages in same conversation
  - [ ] **End**: When conversation is complete (is_complete: true)
  - [ ] **Timeout**: Auto-clear after inactivity period
- [ ] **Session vs Connection:**
  - [ ] **WebSocket Connection** = UI connection (long-lived)
  - [ ] **Chat Session** = Conversation context (per conversation)
  - [ ] **Multiple conversations** can happen over same WebSocket connection

### 7. **Session Management Strategy**
- [ ] **Session Independence:**
  - [ ] **WebSocket Connection** = UI Connection (long-lived, independent of chat sessions)
  - [ ] **Chat Session** = Conversation Context (short-lived, per task)
  - [ ] **They work completely independently!**
- [ ] **Session Lifecycle:**
  - [ ] Chat Session Start → Task Complete → Session Cleared → New Session Start
  - [ ] WebSocket stays connected throughout all sessions
- [ ] **Message History vs Real-time:**
  - [ ] **Real-time (Socket)**: Current conversation in progress
  - [ ] **History**: Past completed conversations (fetched from database)
- [ ] **Key Behaviors:**
  - [ ] **Session closes** ≠ **Socket closes** (Socket stays open)
  - [ ] **Active chat** → **History** when `is_complete: true`
  - [ ] **Messages stay on screen** even after session clears
  - [ ] **New session** starts immediately for next task
- [ ] **Orchestrator Logic:**
  - [ ] Keep current session management (clear session after successful task completion)
  - [ ] No changes needed to orchestrator - current logic is perfect
  - [ ] Each task gets clean context and proper intent recognition
  - [ ] No parameter pollution between different tasks

### 8. **Chat History & Database Management**
- [ ] **Nomenclature:**
  - [ ] **Backend Session** = `session_id` (orchestrator session) (backend session created per request. closes when intent closes or abandoned)
  - [ ] **User Intent** = `user_intent_id` (user experience session) (per 'user intent' request fulfilled or closed by user)
  - [ ] **User Chat** = `user_chat_id` (chat window/experience) (per chat window, persists across reconnections)
  - [ ] **Socket Connection** = `socket_connection_id` (WebSocket connection) (per connection, changes on reconnect)
- [ ] **Database Tables:**
  - [ ] **chat_history** table (NEW)
    - [ ] `id` (primary key)
    - [ ] `user_id` (user identifier)
    - [ ] `user_chat_id` (chat window/experience ID)
    - [ ] `socket_connection_id` (WebSocket connection ID)
    - [ ] `session_id` (backend orchestrator session)
    - [ ] `user_intent_id` (user experience session)
    - [ ] `message_type` (user/ai/thinking)
    - [ ] `content` (message content)
    - [ ] `timestamp` (message timestamp)
    - [ ] `is_complete` (session completion status)
    - [ ] `abandoned` (session abandonment status)
- [ ] **Session States:**
  - [ ] **Completed**: Task finished successfully (`is_complete: true`)
  - [ ] **Abandoned**: User left without completing (`abandoned: true`)
  - [ ] **Active**: Currently in progress
- [ ] **UI Session Display:**
  - [ ] Show current session indicator to user
  - [ ] Display when session completes and new one starts
  - [ ] Show abandoned session status
- [ ] **ID Lifecycle & Behavior:**
  - [ ] **user_chat_id**: 
    - [ ] Created when user opens new chat window
    - [ ] Persists until user closes chat window completely
    - [ ] Same ID across reconnections
    - [ ] Only changes when user creates new chat window
  - [ ] **socket_connection_id**:
    - [ ] Created on each WebSocket connection
    - [ ] Changes on every reconnect
    - [ ] Same user_chat_id can have multiple socket_connection_ids
  - [ ] **user_intent_id**:
    - [ ] Created per user intent/request
    - [ ] Completed when task finished or abandoned
    - [ ] Multiple intents per user_chat_id
  - [ ] **session_id**:
    - [ ] Backend orchestrator session
    - [ ] Short-lived per intent processing
- [ ] **Session Recovery Logic:**
  - [ ] **Completed Intent**: Start new intent in same chat window
  - [ ] **Abandoned Intent**: Resume from last abandoned intent
    - [ ] If backend session still exists → use it
    - [ ] If backend session expired → fetch from history and show as current
  - [ ] **Chat Window Recovery**:
    - [ ] On reconnect → Use existing user_chat_id
    - [ ] Show all history for this chat window
    - [ ] Resume from last state (completed/abandoned)
- [ ] **Message Logging:**
  - [ ] Log every message (user/ai/thinking) with all IDs
  - [ ] Include thinking steps in history
  - [ ] Track session state changes
- [ ] **Future Context Manager:**
  - [ ] Reserve space for context-aware sessions
  - [ ] Will read previous session context from DB
  - [ ] Use context in new backend sessions

- [ ] **Example Flow:**
  ```
  User opens chat widget → user_chat_id: "chat_123"
    ↓
  WebSocket connects → socket_connection_id: "socket_abc"
    ↓
  User sends "Create alarm" → user_intent_id: "intent_456", session_id: "session_789"
    ↓
  Connection drops, user reconnects → socket_connection_id: "socket_def" (new)
    ↓
  Same user_chat_id: "chat_123" (persists)
    ↓
  User continues → user_intent_id: "intent_456" (same intent)
    ↓
  Task completes → intent completed, new intent starts
    ↓
  User sends "Create another alarm" → user_intent_id: "intent_789" (new intent)
    ↓
  Same user_chat_id: "chat_123" (still same chat window)
  ```

## 🎨 **Frontend UI Cleanup & Connection**

### 1. **Update Socket Service** ✅
- [x] Update WebSocket URL to point to backend: `/api/v1/chat/ws/chat`
- [x] Ask user to test connection to real backend

### 2. **Clean Up AiChatWidget** ✅
- [x] Simplify message handling and remove complex fallback logic
- [x] Streamline real-time thinking steps display
- [x] Keep simple fallback for when backend is down
- [x] Update message handling to use real backend responses
- [x] Test real-time thinking steps from backend socket

### 3. **Component System Integration**
- [ ] there will be space for in-chat components. if we get a type of ai response as 'form' then only show the placeholder form 

## 📋 **Files to Modify**

### Backend Files:
- `apps/backend/routers/chat.py` (NEW)
- `apps/backend/routers/__init__.py`
- `backend/orchestrators/chat_orchestrator.py`

### Frontend Files:
- `src/services/socket.ts`
- `src/components/widgets/AiChatWidget.tsx`
- `src/services/aiResponseGenerator.ts` (fallback system)

## 🎯 **Success Criteria**
- [x] WebSocket connects to backend ✅
- [x] Real-time thinking steps display ✅
- [x] Chat responses work ✅
- [x] Fallback system works when backend is down ✅
- [x] Session management works ✅
- [x] Error handling works ✅ 