# WebSearch Widget Migration Guide

## 🎯 **MISSION**
Migrate the WebSearch widget from the old `/apps/backend` to the new clean `/backend` architecture, preserving all existing functionality while allowing small refactoring for better code quality (better names, cleaner structure, etc.).

## 📋 **BACKGROUND & CONTEXT**

### **Backend Migration Status**
- ✅ **COMPLETED**: Alarm widget migration (fully functional)
- ✅ **COMPLETED**: Daily widget system migration  
- ✅ **COMPLETED**: Widget creation API
- ✅ **COMPLETED**: Chat API
- ✅ **COMPLETED**: TODO widget migration (todo-habit, todo-task, todo-event)
- ✅ **COMPLETED**: SingleItemTracker widget migration
- 🔄 **NEXT**: WebSearch widget migration (this task)

### **WebSearch Overview**
WebSearch is an advanced widget that performs web searches on user queries and generates AI-powered summaries. It uses the Serper API for web search and OpenAI for AI summarization with comprehensive fallback mechanisms.

### **Key Principles**
1. **Preserve functionality** - Keep all existing features and behavior
2. **Preserve database fields** - Don't change existing table schemas
3. **Follow established patterns** - Use alarm widget as template
4. **Clean architecture** - Separation of concerns
5. **Async/await** - All database operations
6. **Consistent naming** - Follow existing conventions, allow small improvements
7. **API parity** - Ensure all old endpoints have equivalents
8. **Schema validation** - Ensure response schemas match service output
9. **Comprehensive testing** - Test both service methods and live API endpoints
10. **AI Integration** - Preserve all AI logic as implemented

## 🏗️ **FILE ARCHITECTURE**

### **Files to Create**
```
/backend
├── models/
│   ├── websearch_details.py                    # WebSearch details model
│   ├── websearch_item_activity.py              # WebSearch activities model
│   └── websearch_summary_ai_output.py          # AI summary output model
├── services/
│   └── websearch_service.py                    # WebSearch business logic
├── schemas/
│   └── websearch.py                            # WebSearch request/response schemas
├── routes/
│   └── websearch.py                            # WebSearch endpoints
└── main.py                                     # FastAPI app (add websearch router)
```

### **Files to Update**
```
/backend
├── models/
│   ├── __init__.py                             # Export new models
│   ├── dashboard_widget_details.py             # Add relationship
│   └── daily_widget.py                         # Add relationship
├── services/
│   ├── __init__.py                             # Export WebSearchService
│   └── widget_service.py                       # Add websearch creation logic
├── schemas/
│   └── widget.py                               # Add websearch to WidgetType enum
└── generate_dummy_data.py                      # Add dummy data generation
```

## 📊 **DATABASE SCHEMA (ACTUAL LEGACY IMPLEMENTATION)**

### **WebSearch Details Table** (`websearch_details`)
```sql
- id (String, PK, UUID)
- widget_id (String, FK to dashboard_widget_details.id)
- title (String, NOT NULL)
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

### **WebSearch Item Activity Table** (`websearch_item_activities`)
```sql
- id (String, PK, UUID)
- daily_widget_id (String, FK to daily_widgets.id)
- widget_id (String, FK to dashboard_widget_details.id)
- websearchdetails_id (String, FK to websearch_details.id)
- status (String, NOT NULL) - 'pending', 'completed', 'failed'
- reaction (Text, nullable) - User reaction to search results
- summary (Text, nullable) - AI-generated summary
- source_json (JSON, nullable) - Source data as JSON
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

### **WebSearch Summary AI Output Table** (`websearch_summary_ai_output`)
```sql
- id (String, PK, UUID)
- widget_id (String, FK to dashboard_widget_details.id)
- query (String, NOT NULL) - The search query
- result_json (JSON, nullable) - Full AI response as JSON
- ai_model_used (String, nullable) - 'gpt-4', 'gpt-3.5-turbo', 'fallback'
- ai_prompt_used (Text, nullable) - The prompt sent to AI
- ai_response_time (String, nullable) - Time taken for AI response
- search_results_count (String, nullable) - Number of search results processed
- summary_length (String, nullable) - Length of generated summary
- sources_used (JSON, nullable) - List of sources used for summary
- generation_type (String, NOT NULL, default="ai_generated") - 'ai_generated' or 'fallback'
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

## 🔍 **REFERENCE FILES (Study These)**

### **Models (Study These Patterns)**
- `backend/models/alarm_details.py` - How to structure detail models
- `backend/models/alarm_item_activity.py` - How to structure activity models
- `backend/models/todo_details.py` - Multiple type handling example
- `backend/models/base.py` - Base model to inherit from

### **Services (Study These Patterns)**
- `backend/services/alarm_service.py` - Complete service implementation
- `backend/services/todo_service.py` - Service with type handling
- `backend/services/widget_service.py` - Widget creation logic

### **Schemas (Study These Patterns)**
- `backend/schemas/alarm.py` - Request/response schemas
- `backend/schemas/todo.py` - Validation patterns
- `backend/schemas/widget.py` - Widget schemas with enums

### **Routes (Study These Patterns)**
- `backend/routes/alarm.py` - Complete route implementation
- `backend/routes/todo.py` - Route patterns
- `backend/routes/widgets.py` - Widget management routes

### **Old Implementation (Reference)**
- `apps/backend/models/database/websearch_details.py` - Original model
- `apps/backend/models/database/websearch_item_activity.py` - Original activity model
- `apps/backend/models/database/websearch_summary_ai_output.py` - Original AI output model
- `apps/backend/services/websearch_service.py` - Original service implementation
- `apps/backend/routers/websearch.py` - Original API endpoints
- `apps/backend/routers/ai.py` - AI integration and web search logic

## 🎯 **IMPLEMENTATION TASKS**

### **Phase 1: Analysis & Planning**
1. **Study the old WebSearch implementation**
   - ✅ Examine old models in `apps/backend/models/database/`
   - ✅ Identify all fields and relationships
   - ✅ Note business logic: search execution, AI summary generation
   - ✅ Understand AI integration patterns

2. **Plan the migration**
   - ✅ Map old fields to new structure
   - ✅ Identify required API endpoints
   - ✅ Plan search engine handling
   - ✅ Consider AI integration requirements

### **Phase 2: Models**
1. **Create `backend/models/websearch_details.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_details.py pattern

2. **Create `backend/models/websearch_item_activity.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_item_activity.py pattern

3. **Create `backend/models/websearch_summary_ai_output.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Handle JSON fields properly

4. **Update `backend/models/__init__.py`**
   - Export new models

5. **Update relationship models**
   - Add relationships to `DashboardWidgetDetails`
   - Add relationships to `DailyWidget`

### **Phase 3: Schemas**
1. **Create `backend/schemas/websearch.py`**
   - Request schemas (UpdateActivityRequest, UpdateWebSearchDetailsRequest, etc.)
   - Response schemas (WebSearchDetailsResponse, WebSearchActivityResponse, etc.)
   - Follow alarm.py pattern exactly
   - **CRITICAL**: Ensure response schema field names match service output exactly

2. **Update `backend/schemas/widget.py`**
   - Add `WEBSEARCH = "websearch"` to `WidgetType` enum
   - Update `CreateWidgetRequest` to include websearch-specific fields
   - Add validation for websearch fields

### **Phase 4: Services**
1. **Create `backend/services/websearch_service.py`**
   - Implement all WebSearch business logic
   - Follow alarm_service.py patterns
   - Include methods for CRUD operations
   - Include search execution methods
   - Handle AI summary generation
   - **CRITICAL**: Preserve all business logic from legacy implementation
   - **CRITICAL**: Include delete flag filtering in all queries

2. **Update `backend/services/__init__.py`**
   - Export WebSearchService

3. **Update `backend/services/widget_service.py`**
   - Add WebSearch widget creation logic
   - Follow alarm pattern
   - Handle websearch-specific field mapping

### **Phase 5: Routes**
1. **Create `backend/routes/websearch.py`**
   - Implement all WebSearch endpoints
   - Follow alarm.py patterns exactly
   - Include proper error handling
   - Use dependency injection
   - **CRITICAL**: Ensure response_model matches service output structure

2. **Update `backend/main.py`**
   - Include websearch router

### **Phase 6: Integration**
1. **Update `backend/generate_dummy_data.py`**
   - Add WebSearch dummy data generation
   - Create proper relationships
   - Include realistic search data and AI summaries

2. **Test all endpoints**
   - Create comprehensive test script
   - Test all CRUD operations
   - Test search functionality
   - **CRITICAL**: Test both service methods and live API endpoints

## 🔧 **KEY IMPLEMENTATION DETAILS**

### **Web Search Integration**
WebSearch uses Serper API for Google search:

1. **Search API Integration**:
```python
async def perform_web_search(query: str) -> Dict[str, Any]:
    """Perform web search using Serper API"""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise ValueError("SERPER_API_KEY not found")
    
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": 5}
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()
```

2. **Search Result Parsing**:
```python
def parse_search_results(search_response: Dict[str, Any]) -> List[Dict[str, str]]:
    """Parse and format Serper API search results"""
    results = []
    organic_results = search_response.get("organic", [])
    
    for result in organic_results[:5]:
        formatted_result = {
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", ""),
            "combined_text": f"Title: {result.get('title', '')}\nURL: {result.get('link', '')}\nSnippet: {result.get('snippet', '')}"
        }
        results.append(formatted_result)
    
    return results
```

### **AI Integration**
WebSearch includes sophisticated AI analysis using OpenAI:

1. **AI Summary Generation**:
```python
async def generate_summary_with_openai(prompt: str) -> Dict[str, Any]:
    """Generate summary using OpenAI"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that provides accurate, concise summaries of web search results."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return {
        "summary": response.choices[0].message.content.strip(),
        "response_time": f"{response_time:.2f}s",
        "confidence_score": "0.85",
        "model_used": "gpt-3.5-turbo"
    }
```

2. **Prompt Creation**:
```python
def create_summarization_prompt(query: str, search_results: List[Dict[str, str]]) -> str:
    """Create a prompt for OpenAI summarization"""
    combined_content = "\n\n---\n\n".join([result["combined_text"] for result in search_results])
    
    prompt = f"""
You are a helpful AI assistant that provides concise, factual summaries of web search results.

ORIGINAL QUERY: {query}

SEARCH RESULTS:
{combined_content}

Please provide a comprehensive summary that:
1. Directly addresses the original query
2. Highlights the most relevant and recent information
3. Includes key facts and insights
4. Is concise but thorough (2-3 paragraphs maximum)
5. Maintains factual accuracy
6. Cites sources when appropriate

SUMMARY:
"""
    return prompt
```

3. **Fallback Handling**:
```python
def create_fallback_summary(search_results: List[Dict[str, str]]) -> str:
    """Create a fallback summary from raw search results"""
    if not search_results:
        return "No relevant information found."
    
    summary_parts = []
    for i, result in enumerate(search_results[:3], 1):
        summary_parts.append(f"{i}. {result['title']}\n   {result['snippet'][:200]}...")
    
    return "\n\n".join(summary_parts)
```

### **Required Endpoints**
- `GET /api/v1/websearch/getSummaryAndActivity/{widget_id}` - Get websearch summary and activity
- `POST /api/v1/websearch/updateActivity/{activity_id}` - Update websearch activity
- `GET /api/v1/websearch/getWebsearchDetails/{widget_id}` - Get websearch details
- `POST /api/v1/websearch/updateDetails/{websearch_details_id}` - Update websearch details
- `GET /api/v1/websearch/getaisummary/{widget_id}` - Get AI summary for specific widget
- `POST /api/v1/ai/generate_web_summary_list` - Generate AI summaries for all websearch widgets

### **Widget Creation Fields**
When creating a WebSearch widget, the form should include:
- **Fixed fields**: Widget Type, Title, Frequency, Importance, Category
- **WebSearch-specific fields**: 
  - `title` (used as search query)

### **Error Handling**
- Use `utils.errors.raise_not_found()` for 404s
- Use `utils.errors.raise_database_error()` for DB errors
- Follow alarm.py error handling patterns
- Handle search API failures gracefully
- Handle AI service failures gracefully

### **Database Operations**
- All async/await
- Use SQLAlchemy select/update/insert
- Proper transaction handling
- Follow alarm_service.py patterns
- **CRITICAL**: Always include delete_flag filtering
- Handle JSON fields properly

## 🧪 **TESTING REQUIREMENTS**

### **Test Files to Create**
1. **`backend/test_scripts/test_websearch_api.py`**
   - Test all WebSearch endpoints
   - Follow test_alarm_api.py patterns
   - Test search functionality
   - Test AI summary generation
   - **CRITICAL**: Test both service methods and API endpoints
   - **CRITICAL**: Test with fresh dummy data for each run

2. **Update `backend/test_scripts/run_tests.py`**
   - Include WebSearch test suite

### **Test Coverage**
- WebSearch creation via widget service
- WebSearch details retrieval
- Search execution and result handling
- AI summary generation and analysis
- Error handling
- All CRUD operations
- **CRITICAL**: Live API endpoint testing

### **Test Scenarios**
1. **Research Query**: title="AI trends 2024"
2. **News Search**: title="latest technology news"
3. **Academic Search**: title="machine learning papers"
4. **Simple Query**: title="weather today"

## 🚨 **CRITICAL REQUIREMENTS**

### **DO NOT:**
- ❌ **ADD NEW FEATURES** - This is a migration, not an enhancement
- ❌ Change existing database field names
- ❌ Remove any fields from old models
- ❌ Skip error handling
- ❌ Use sync database operations
- ❌ Remove business logic from legacy implementation
- ❌ Ignore schema field name mismatches
- ❌ Skip delete flag filtering
- ❌ Skip AI integration patterns
- ❌ Change core API behavior
- ❌ Add new endpoints not in legacy

### **MUST:**
- ✅ **PRESERVE ALL FUNCTIONALITY** - Keep everything that exists in legacy
- ✅ Follow alarm widget patterns
- ✅ Use async/await everywhere
- ✅ Include proper error handling
- ✅ Add comprehensive tests
- ✅ Update all necessary files
- ✅ Maintain database compatibility
- ✅ Ensure API parity with old backend
- ✅ **CRITICAL**: Preserve all business logic from legacy
- ✅ **CRITICAL**: Test both service methods and live API
- ✅ **CRITICAL**: Handle AI integration properly
- ✅ **CRITICAL**: Allow small refactoring for better code quality

## 📚 **RESOURCES**

### **Study These Files First:**
1. `backend/models/alarm_details.py` - Model structure
2. `backend/services/alarm_service.py` - Service patterns
3. `backend/schemas/alarm.py` - Schema patterns
4. `backend/routes/alarm.py` - Route patterns
5. `apps/backend/models/database/websearch_details.py` - Original model
6. `apps/backend/models/database/websearch_item_activity.py` - Original activity model
7. `apps/backend/models/database/websearch_summary_ai_output.py` - Original AI output model
8. `apps/backend/services/websearch_service.py` - Original service implementation
9. `apps/backend/routers/websearch.py` - Original API endpoints
10. `apps/backend/routers/ai.py` - AI integration and web search logic

### **Key Patterns to Follow:**
- **Model inheritance**: `from .base import BaseModel`
- **Service initialization**: `def __init__(self, db: AsyncSession)`
- **Schema validation**: Use Pydantic `Field` with constraints
- **Route dependencies**: Use `Depends(get_db_session_dependency)`
- **Error handling**: Use utility functions from `utils.errors`
- **AI integration**: Handle AI service calls properly

## 🎯 **SUCCESS CRITERIA**

✅ **FUNCTIONALITY PRESERVED** - All existing features work as expected
✅ All WebSearch endpoints working with same behavior
✅ Database operations successful with same data structure
✅ Error handling implemented properly
✅ Tests passing with compatible data
✅ Follows established patterns
✅ No breaking changes to existing functionality
✅ Swagger docs generated correctly
✅ API parity with old backend achieved
✅ AI integration functional with same logic
✅ Dummy data generation complete
✅ **CRITICAL**: All business logic preserved
✅ **CRITICAL**: Live API testing successful
✅ **CRITICAL**: No new features added
✅ **CRITICAL**: Code quality improved where appropriate

## 🔄 **SPECIFIC CONSIDERATIONS FOR WEBSEARCH**

1. **Serper API Integration**: Use Serper API for Google search with proper error handling
2. **AI Summary Generation**: Generate comprehensive summaries using OpenAI GPT-3.5-turbo
3. **Fallback Mechanisms**: Provide fallback summaries when AI services fail
4. **Source Tracking**: Track which sources were used for AI analysis
5. **Result Storage**: Store both raw search results and AI-processed summaries
6. **Query Management**: Use widget title as search query
7. **Performance**: Optimize for search API response times
8. **Error Resilience**: Handle search API failures and AI service outages

## 📋 **API ENDPOINTS TO IMPLEMENT**

### **Required Endpoints (from legacy implementation)**
- `GET /api/v1/websearch/getSummaryAndActivity/{widget_id}`
- `POST /api/v1/websearch/updateActivity/{activity_id}`
- `GET /api/v1/websearch/getWebsearchDetails/{widget_id}`
- `POST /api/v1/websearch/updateDetails/{websearch_details_id}`
- `GET /api/v1/websearch/getaisummary/{widget_id}`

### **AI Generation Endpoint**
- `POST /api/v1/ai/generate_web_summary_list` - Generate AI summaries for all websearch widgets

## 🤖 **AI INTEGRATION CONSIDERATIONS**

### **AI Service Integration**
1. **Summary Generation**: Use OpenAI GPT-3.5-turbo to create comprehensive summaries
2. **Prompt Engineering**: Create structured prompts for consistent AI responses
3. **Fallback Handling**: Provide fallback summaries when AI services fail
4. **Response Time Tracking**: Track AI response times for performance monitoring
5. **Source Attribution**: Track which sources contributed to AI analysis

### **AI Output Structure**
```python
{
    "summary": "Comprehensive summary of search results...",
    "sources": [
        {"title": "Source Title", "url": "https://source.com"}
    ],
    "search_successful": True,
    "results_count": 5,
    "confidence_score": "0.85"
}
```

### **Error Handling for AI Services**
- Handle OpenAI API timeouts
- Handle OpenAI API rate limits
- Handle OpenAI API authentication failures
- Provide fallback responses when AI is unavailable
- Log AI service errors for debugging

## 🚨 **LESSONS LEARNED & IMPROVEMENTS**

### **Critical Issues Encountered:**
1. **Schema Field Mismatches**: Response schema field names must exactly match service output
2. **Business Logic Preservation**: Don't remove complex logic like search execution and AI integration
3. **Delete Flag Filtering**: Always include `delete_flag == False` in queries
4. **AI Service Integration**: Handle AI service failures gracefully
5. **JSON Field Handling**: Properly handle JSON fields in database operations
6. **API vs Service Testing**: Test both service methods and live API endpoints

### **Best Practices Added:**
1. **Schema Validation**: Ensure response_model matches service output structure
2. **Comprehensive Testing**: Test both unit tests and live API calls
3. **Business Logic Preservation**: Keep all original functionality
4. **Error Handling**: Proper error handling for all edge cases
5. **AI Integration**: Robust AI service integration with fallbacks
6. **Documentation**: Clear documentation of all changes

---

**Remember**: This is a **MIGRATION** that preserves functionality while allowing small improvements. The alarm widget is your primary template. Follow its patterns, replace "alarm" with "websearch" and adapt the specific fields and logic for WebSearch functionality. **CRITICAL**: Preserve all business logic from legacy, ensure schema compatibility, handle AI integration properly, and maintain all existing functionality while improving code quality where appropriate! 