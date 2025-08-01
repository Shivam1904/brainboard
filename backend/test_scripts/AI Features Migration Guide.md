# AI Features Migration Guide

## 🎯 **MISSION**
Migrate AI features from the old `/apps/backend` to the new clean `/backend` architecture, focusing on building the API with a shared orchestrator pattern.

## 📋 **BACKGROUND**

### **AI Features Overview**
- **Daily Plan Generation**: AI-powered widget selection for daily dashboard
- **Web Summary Generation**: Web search + AI summarization for WebSearch widgets
- **Shared Architecture**: Both AI tools (chat) and AI APIs (direct) use same core logic

### **Key Principles**
1. **Shared Orchestrator**: Tools and APIs use same `AIOrchestrator`
2. **Single AI Service**: All AI business logic in one service
3. **API Focus**: Primary goal is building functional APIs
4. **Clean Architecture**: Separation of concerns
5. **Async/await**: All operations asynchronous

## 🏗️ **SIMPLIFIED ARCHITECTURE**

### **Core Components**
```
┌─────────────────┐    ┌─────────────────┐
│   AI Tools      │    │  AI APIs        │
│  (Chat-based)   │    │ (Direct access) │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┐
                                 │                       │
                    ┌─────────────────┐                  │
                    │  AI Orchestrator│                  │
                    │  (Shared Core)  │                  │
                    └─────────────────┘                  │
                                 │                       │
                                 └───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  AI Service     │
                    │  (Single        │
                    │   Service)      │
                    └─────────────────┘
```

### **Files to Create**
```
/backend
├── models/
│   └── daily_widgets_ai_output.py              # AI output model
├── services/
│   └── ai_service.py                           # Single AI service
├── orchestrators/
│   └── ai_orchestrator.py                      # AI operations orchestrator
├── schemas/
│   └── ai.py                                   # AI request/response schemas
├── routes/
│   └── ai.py                                   # AI endpoints
└── ai_engine/tools/
    ├── daily_plan_tool.py                      # Daily plan tool
    └── web_summary_tool.py                     # Web summary tool
```

### **Files to Update**
```
/backend
├── models/__init__.py                           # Export new model
├── services/__init__.py                         # Export AI service
├── main.py                                      # Include AI router
└── generate_dummy_data.py                       # Add AI output data
```

## 📊 **DATABASE SCHEMA**

### **Daily Widgets AI Output Table** (`daily_widgets_ai_output`)
```sql
- id (String, PK, UUID)
- widget_id (String, FK to dashboard_widget_details.id)
- priority (String, NOT NULL) - 'HIGH', 'LOW'
- reasoning (Text, nullable) - AI reasoning for selection
- result_json (JSON, nullable) - Full AI response as JSON
- date (Date, NOT NULL) - Date for which plan was generated
- ai_model_used (String, nullable) - 'gpt-4', 'gpt-3.5-turbo'
- ai_prompt_used (Text, nullable) - The prompt sent to AI
- ai_response_time (String, nullable) - Time taken for AI response
- confidence_score (String, nullable) - AI confidence in decision
- generation_type (String, NOT NULL, default="ai_generated") - 'ai_generated' or 'fallback'
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

## 🔍 **REFERENCE FILES**

### **Legacy Implementation**
- `apps/backend/models/database/daily_widgets_ai_output.py` - Original model
- `apps/backend/services/daily_plan_service.py` - Original service
- `apps/backend/routers/ai.py` - Original AI endpoints

### **New Architecture Patterns**
- `backend/services/alarm_service.py` - Service patterns
- `backend/orchestrators/chat_orchestrator.py` - Orchestrator patterns
- `backend/ai_engine/tools/alarm_tool.py` - Tool patterns

## 🎯 **IMPLEMENTATION TASKS**

### **Phase 1: Models**
1. **Create `backend/models/daily_widgets_ai_output.py`**
   - Inherit from `BaseModel`
   - Include all fields from legacy model
   - Add proper relationships

### **Phase 2: AI Service**
1. **Create `backend/services/ai_service.py`**
   - **Daily Plan Generation**: AI widget selection logic
   - **Web Summary Generation**: Web search + AI summarization
   - **AI Integration**: OpenAI + Serper API calls
   - **Fallback Mechanisms**: When AI services fail
   - **Database Operations**: CRUD for AI outputs

### **Phase 3: AI Orchestrator**
1. **Create `backend/orchestrators/ai_orchestrator.py`**
   - Coordinate between tools and APIs
   - Route requests to appropriate service methods
   - Handle session management for chat
   - Provide consistent interface

### **Phase 4: Schemas & Routes**
1. **Create `backend/schemas/ai.py`**
   - Request/response schemas for AI operations
2. **Create `backend/routes/ai.py`**
   - AI endpoints for direct API access
3. **Update `backend/main.py`**
   - Include AI router

### **Phase 5: AI Engine Tools**
1. **Create `backend/ai_engine/tools/daily_plan_tool.py`**
   - Tool for chat-based daily plan generation
2. **Create `backend/ai_engine/tools/web_summary_tool.py`**
   - Tool for chat-based web summary generation

## 🔧 **KEY IMPLEMENTATION DETAILS**

### **Shared Orchestrator Pattern**
```python
# backend/orchestrators/ai_orchestrator.py
class AIOrchestrator:
    def __init__(self, db_session):
        self.db_session = db_session
        self.ai_service = AIService(db_session)
    
    async def generate_daily_plan(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """Shared method used by both tools and APIs"""
        return await self.ai_service.generate_daily_plan(user_id, target_date)
    
    async def generate_web_summaries(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """Shared method used by both tools and APIs"""
        return await self.ai_service.generate_web_summaries(user_id, target_date)
```

### **Tool Implementation**
```python
# backend/ai_engine/tools/daily_plan_tool.py
class DailyPlanTool(BaseTool):
    def __init__(self, db_session):
        super().__init__("daily_plan_tool", "Generate AI daily plans")
        self.ai_orchestrator = AIOrchestrator(db_session)
    
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return await self.ai_orchestrator.generate_daily_plan(user_id, parameters.get("target_date"))
```

### **API Implementation**
```python
# backend/routes/ai.py
@router.post("/generate_today_plan")
async def generate_today_plan(
    target_date: Optional[date] = Query(None),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    ai_orchestrator = AIOrchestrator(db)
    return await ai_orchestrator.generate_daily_plan(user_id, target_date or date.today())
```

### **Required Endpoints**
- `POST /api/v1/ai/generate_today_plan` - Generate daily plan
- `POST /api/v1/ai/generate_web_summary_list` - Generate web summaries
- `POST /api/v1/ai/generate_activity_from_plan` - Generate activities from plan

## 🧪 **TESTING REQUIREMENTS**

### **Test File**
- `backend/test_scripts/test_ai_features.py`
- Test both service methods and live API endpoints
- Test AI integration and fallback mechanisms
- Test daily plan generation and web summary generation

## 🚨 **CRITICAL REQUIREMENTS**

### **MUST:**
- ✅ **Shared Logic**: Tools and APIs use same orchestrator and service
- ✅ **API Focus**: Primary goal is building functional APIs
- ✅ **Single Service**: All AI logic in one `ai_service.py`
- ✅ **Async Operations**: All database and API calls async
- ✅ **Error Handling**: Proper error handling and fallbacks
- ✅ **Database Compatibility**: Preserve existing table structure

### **DO NOT:**
- ❌ Create separate services for different AI operations
- ❌ Skip orchestrator pattern
- ❌ Use sync operations
- ❌ Ignore error handling

## 📚 **RESOURCES**

### **Study These Files:**
1. `apps/backend/services/daily_plan_service.py` - Original AI logic
2. `apps/backend/routers/ai.py` - Original AI endpoints
3. `backend/services/alarm_service.py` - Service patterns
4. `backend/orchestrators/chat_orchestrator.py` - Orchestrator patterns

## 🎯 **SUCCESS CRITERIA**

✅ **API Functionality**: All AI endpoints working
✅ **Shared Architecture**: Tools and APIs use same core logic
✅ **Single Service**: All AI operations in one service
✅ **Database Operations**: AI outputs stored correctly
✅ **Error Handling**: Proper fallbacks and error responses
✅ **Testing**: Comprehensive test coverage
✅ **Integration**: Works with existing widget system

---

**Focus**: Building functional APIs with shared orchestrator pattern. Single AI service handles all business logic. Tools and APIs both use the same core components for consistency. 