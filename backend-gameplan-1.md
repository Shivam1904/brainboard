# 🧠 Backend Gameplan - Web Summary AI Agent

## 📋 Overview
Building a modular backend for Web Summary AI Agent that supports the existing `WebSummaryWidget.tsx` frontend:

**Primary API**: 
- **Summary Generation API**: Immediate query processing + summary generation (matches current frontend)generate
**Future APIs** (for multi-widget dashboard support):
- **Widget Configuration API**: Save/retrieve persistent search terms for scheduled widgets  
- **Background Processing API**: Daily automated summary generation for saved widgets

## 🎯 Goals
- **Frontend-First Approach**: Match existing `WebSummaryWidget.tsx` expectations
- **Immediate Functionality**: Real-time query → summary generation  
- **Modular, extensible codebase**: Easy to add more widget types (reminders, counters, etc.)
- **Local development with easy AWS migration**
- **Future Enhancement**: Background AI agent processing for persistent widgets
- **Multiple widget instances support**: Different search terms per widget
- **Daily summary updates**: For saved/persistent search terms

## 🛠️ Tech Stack
- **Framework**: FastAPI (already set up)
- **AI/ML**: LangChain + OpenAI GPT
- **Web Search**: Serper.dev API
- **Local DB**: SQLite with SQLAlchemy
- **Environment**: **Conda** (see `environment.yml`)
- **Future Migration**: AWS DynamoDB, Lambda, SQS

## 🔧 Development Environment Setup

### **Environment Management**
This project uses **Conda** for environment management. Dependencies are in `apps/backend/environment.yml`.

```bash
# Create and activate conda environment
cd apps/backend
conda env create -f environment.yml
conda activate brainboard
```

## 📚 Required API Keys

### 1. OpenAI API Key
- **Get it from**: https://platform.openai.com/
- **Purpose**: GPT for content summarization

### 2. Serper.dev API Key  
- **Get it from**: https://serper.dev/
- **Purpose**: Google search results

### Environment Variables:
```bash
# Add to .env file
OPENAI_API_KEY=your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here
DATABASE_URL=sqlite:///./brainboard.db
```

## 🤔 Architecture Decisions

### **Core Design Principles:**
1. **Modular Architecture**: Easy to add new widget types
2. **Service Layer**: Single responsibility for each service
3. **Data Access Layer**: Clean database operations
4. **Factory Pattern**: Extensible widget creation
5. **Local-First**: Everything works without AWS

### **Widget Lifecycle:**
1. **Create Widget**: User enters query → widget created → first summary generated
2. **Generate Summary**: User requests new summary → AI processing → stored in DB
3. **Fetch Summary**: User loads widget → get latest summary from DB (fast)

### **Database Strategy:**
- **Widgets Table**: widget_id, user_id, widget_type, current_query, settings
- **Summaries Table**: summary_id, widget_id, query, summary_text, sources_json
- **Relationship**: One widget → Many summaries

## 🏗️ Implementation Plan

### Phase 1: Core Summary API (Match Frontend) ✅ TODO
- [ ] **1.1** Create widget creation endpoint: `POST /api/widget/web-summary/create`
- [ ] **1.2** Create summary generation endpoint: `POST /api/widget/web-summary/{widget_id}/generate`
- [ ] **1.3** Create summary fetch endpoint: `GET /api/widget/web-summary/{widget_id}/latest`
- [ ] **1.4** Set up SQLite database for widget and summary storage
- [ ] **1.5** Create response models:
  ```typescript
  // Widget creation response
  {
    widget_id: string
    user_id: string
    summary: Summary  // First summary generated
    widget_created_at: string
  }
  
  // Summary model (matches frontend)
  {
    id: string
    query: string  
    summary: string
    sources: string[]
    createdAt: string
  }
  ```
- [ ] **1.6** Update database initialization to support both SQLite and DynamoDB

### Phase 2: Enhanced AI Service ✅ TODO  
- [ ] **2.1** Integrate LangChain for better AI agent capabilities
- [ ] **2.2** Create modular web search service using Serper.dev
- [ ] **2.3** Implement smart content extraction and summarization
- [ ] **2.4** Add source tracking and citation (return clickable URLs)
- [ ] **2.5** Error handling and fallback mechanisms (graceful degradation)

### Phase 3: Widget Configuration API (Future Enhancement) ✅ TODO
- [ ] **3.1** Create widget management endpoints:
  - `GET /api/widget/web-summary/{widget_id}` - Get complete widget info + latest summary
  - `PUT /api/widget/web-summary/{widget_id}/settings` - Update widget settings/query
  - `DELETE /api/widget/web-summary/{widget_id}` - Delete widget and all summaries
- [ ] **3.2** Add validation for settings (query, frequency, limits)
- [ ] **3.3** Support widget persistence and user ownership

### Phase 4: Advanced Summary Features ✅ TODO
- [ ] **4.1** Add widget-specific summary history endpoints:
  - `GET /api/widget/web-summary/{widget_id}/history` - Get all summaries for widget
  - `GET /api/widget/web-summary/{widget_id}/latest` - Get latest summary for widget
  - `DELETE /api/widget/web-summary/{widget_id}/summary/{summary_id}` - Delete specific summary
- [ ] **4.2** Implement summary caching (avoid regenerating same queries)
- [ ] **4.3** Add summary sharing capabilities (public widget links)

### Phase 5: Testing & Documentation ✅ TODO
- [ ] **5.1** Unit tests for all services
- [ ] **5.2** Integration tests for API endpoints  
- [ ] **5.3** API documentation with OpenAPI/Swagger
- [ ] **5.4** Error handling documentation

## 📁 Modular Architecture & File Structure

### **🎯 Design Principles:**
- **Single Responsibility**: Each class/service has one job
- **Dependency Injection**: Easy to mock and test
- **Factory Pattern**: Easy to extend with new widget types
- **Data Access Pattern**: Clean database operations

```
apps/backend/
├── core/
│   ├── database.py          # Database connection & session management
│   ├── config.py           # Configuration management (Pydantic Settings)
│   └── exceptions.py       # Custom exception classes
├── models/
│   ├── database_models.py  # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic request/response models
├── data/                  # 🆕 Data Access Layer
│   ├── base_data.py       # Abstract base data access
│   ├── widget_data.py     # Widget CRUD operations
│   └── summary_data.py    # Summary CRUD operations
├── services/              # 🆕 Business Logic Layer
│   ├── base_service.py    # Abstract base service
│   ├── web_search_service.py # Web search (Serper.dev)
│   ├── ai_summarization_service.py # AI summarization (OpenAI)
│   ├── widget_service.py  # Widget business logic
│   └── summary_service.py # Summary orchestration service
├── factories/             # 🆕 Factory Pattern
│   ├── widget_factory.py  # Create different widget types
│   └── service_factory.py # Create appropriate services
├── routers/
│   ├── widget_web_summary.py # Web Summary widget API
│   └── health.py          # Health check endpoints
└── utils/                 # 🆕 Utility functions
    ├── logger.py          # Logging setup
    ├── validators.py      # Custom validators
    └── helpers.py         # Helper functions
```

### **🔧 Modular Code Organization:**

#### **1. Base Classes (Abstract Interfaces)**
```python
# services/base_service.py
from abc import ABC, abstractmethod

class BaseService(ABC):
    """Abstract base class for all services"""
    
    @abstractmethod
    async def validate_input(self, data: dict) -> bool:
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> dict:
        pass

# data/base_data.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseDataAccess(ABC, Generic[T]):
    """Abstract base data access with common CRUD operations"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
```

#### **2. Service Layer (Single Responsibility)**
```python
# services/web_search_service.py
class WebSearchService(BaseService):
    """Handles only web search functionality"""
    
    async def search(self, query: str) -> List[SearchResult]:
        # Only web search logic here
        pass

# services/ai_summarization_service.py  
class AISummarizationService(BaseService):
    """Handles only AI summarization"""
    
    async def summarize(self, content: str, query: str) -> str:
        # Only AI summarization logic here
        pass

# services/summary_service.py
class SummaryService(BaseService):
    """Orchestrates web search + AI summarization"""
    
    def __init__(self, web_search: WebSearchService, ai_service: AISummarizationService):
        self.web_search = web_search
        self.ai_service = ai_service
    
    async def generate_summary(self, query: str) -> Summary:
        # Orchestrates: search → extract → summarize
        search_results = await self.web_search.search(query)
        content = self._extract_content(search_results)
        summary_text = await self.ai_service.summarize(content, query)
        return Summary(query=query, summary=summary_text, sources=...)
```

#### **3. Factory Pattern (Easy Extension)**
```python
# factories/widget_factory.py
class WidgetFactory:
    """Creates different types of widgets"""
    
    @staticmethod
    def create_widget(widget_type: str, **kwargs) -> Widget:
        if widget_type == "web-summary":
            return WebSummaryWidget(**kwargs)
        elif widget_type == "reminders":
            return RemindersWidget(**kwargs)
        elif widget_type == "counter":
            return CounterWidget(**kwargs)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")

# factories/service_factory.py
class ServiceFactory:
    """Creates appropriate services for widget types"""
    
    @staticmethod
    def create_summary_service() -> SummaryService:
        web_search = WebSearchService()
        ai_service = AISummarizationService()
        return SummaryService(web_search, ai_service)
```

#### **4. Data Access Pattern (Clean Database Layer)**
```python
# data/widget_data.py
class WidgetDataAccess(BaseDataAccess[Widget]):
    """Handles widget database operations"""
    
    async def create(self, widget: Widget) -> Widget:
        # Database-specific widget creation
        pass
    
    async def get_by_user_id(self, user_id: str) -> List[Widget]:
        # Get all widgets for a user
        pass

# data/summary_data.py  
class SummaryDataAccess(BaseDataAccess[Summary]):
    """Handles summary database operations"""
    
    async def get_latest_by_widget_id(self, widget_id: str) -> Optional[Summary]:
        # Get latest summary for widget
        pass
    
    async def get_history_by_widget_id(self, widget_id: str, limit: int) -> List[Summary]:
        # Get summary history for widget
        pass
```

### **� Benefits of This Architecture:**

#### **1. Easy Extension:**
```python
# Adding a new widget type is simple:
# 1. Create new widget class
class CounterWidget(Widget):
    count: int = 0

# 2. Add to factory
# widget_factory.py - just add new case

# 3. Create service if needed
class CounterService(BaseService):
    async def increment(self, widget_id: str) -> int:
        pass

# 4. Add router
# routers/widget_counter.py
```

#### **2. Easy Testing:**
```python
# Mock any service for testing
async def test_summary_generation():
    # Mock web search service
    mock_web_search = Mock(spec=WebSearchService)
    mock_web_search.search.return_value = [mock_results]
    
    # Mock AI service  
    mock_ai = Mock(spec=AISummarizationService)
    mock_ai.summarize.return_value = "Mock summary"
    
    # Test with mocked dependencies
    service = SummaryService(mock_web_search, mock_ai)
    result = await service.generate_summary("test query")
    
    assert result.summary == "Mock summary"
```

#### **3. Clean Configuration:**
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    serper_api_key: str
    
    # Database
    database_url: str = "sqlite:///./brainboard.db"
    
    # AI Configuration
    default_ai_model: str = "gpt-3.5-turbo"
    max_search_results: int = 5
    max_summary_tokens: int = 400
    
    # Widget Configuration
    default_user_id: str = "default_user"
    widget_max_summaries_history: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### **4. Dependency Injection in FastAPI:**
```python
# main.py
def get_summary_service() -> SummaryService:
    return ServiceFactory.create_summary_service()

def get_widget_repository() -> WidgetRepository:
    return WidgetRepository()

# routers/widget_web_summary.py
@router.post("/create")
async def create_widget(
    request: CreateWidgetRequest,
    summary_service: SummaryService = Depends(get_summary_service),
    widget_repo: WidgetRepository = Depends(get_widget_repository)
):
    # Clean, testable, mockable dependencies
    pass
```

### **🎯 Implementation Priority:**
1. **Core Infrastructure**: Config, Database, Base classes
2. **Repository Layer**: Data access for widgets and summaries  
3. **Service Layer**: Web search, AI, orchestration services
4. **API Layer**: FastAPI routers with dependency injection
5. **Testing**: Unit tests for each service independently

### � **Core Widget APIs (Priority Implementation)**

#### 1. Create Widget
```python
POST /api/widget/web-summary/create
# Request Body:
{
  "query": "newly funded YC companies"
}

# Response:
{
  "widget_id": "uuid-here",
  "user_id": "user-uuid",
  "summary": {
    "id": "summary-uuid-here",
    "query": "newly funded YC companies", 
    "summary": "Here's a comprehensive summary...",
    "sources": ["https://url1.com", "https://url2.com"],
    "createdAt": "2025-01-27T10:00:00Z"
  },
  "widget_created_at": "2025-01-27T10:00:00Z"
}
```

#### 2. Generate New Summary
```python
POST /api/widget/web-summary/{widget_id}/generate
# Request Body:
{
  "query": "newly funded YC companies 2025"
}

# Response:
{
  "id": "new-summary-uuid",
  "query": "newly funded YC companies 2025", 
  "summary": "Here's the latest summary...",
  "sources": ["https://url1.com", "https://url2.com"],
  "createdAt": "2025-01-27T11:00:00Z"
}
```

#### 3. Fetch Latest Summary
```python
GET /api/widget/web-summary/{widget_id}/latest
# Response:
{
  "id": "existing-summary-uuid",
  "query": "newly funded YC companies 2025",
  "summary": "Previously generated summary...",
  "sources": ["https://url1.com", "https://url2.com"],
  "createdAt": "2025-01-27T10:00:00Z"
}
```

### 📋 **Widget Management APIs (Future Enhancement)**

#### 4. Get Widget Info
```python
GET /api/widget/web-summary/{widget_id}
# Response:
{
  "widget_id": "uuid-here",
  "user_id": "user-uuid",
  "current_query": "newly funded YC companies",
  "settings": {
    "update_frequency": "manual",
    "max_results": 5
  },
  "latest_summary": { /* Summary object */ },
  "created_at": "2025-01-27T09:00:00Z",
  "last_updated": "2025-01-27T10:00:00Z"
}
```

#### 5. Update Widget Settings
```python
PUT /api/widget/web-summary/{widget_id}/settings
# Request Body:
{
  "query": "newly funded YC companies 2025",
  "update_frequency": "daily",
  "max_results": 10
}
```

#### 6. Delete Widget
```python
DELETE /api/widget/web-summary/{widget_id}
# Deletes widget and all its summaries
```

### � **Summary History APIs (Future Enhancement)**

#### 7. Get Summary History
```python
GET /api/widget/web-summary/{widget_id}/history?limit=10&offset=0
# Response:
{
  "widget_id": "uuid-here",
  "summaries": [
    {
      "id": "summary-uuid-1",
      "query": "newly funded YC companies 2025",
      "summary": "Recent summary...",
      "sources": ["https://url1.com"],
      "createdAt": "2025-01-27T10:00:00Z"
    }
  ],
  "total": 25,
  "has_more": true
}
```

#### 8. Delete Specific Summary
```python
DELETE /api/widget/web-summary/{widget_id}/summary/{summary_id}
# Deletes specific summary from widget history
```

### 📋 **Error Responses**
```python
# Standard Error Format:
{
  "detail": "Failed to generate summary. Please try again.",
  "error_code": "SUMMARIZATION_FAILED"
}
```

## 🔄 Implementation Strategy

### 🎯 Phase 1 Focus: Get Frontend Working
1. **Immediate Goal**: Make `WebSummaryWidget.tsx` functional with widget lifecycle
2. **Two Core APIs**: 
   - `POST /api/widget/web-summary/{widget_id}/generate` - Generate NEW summary (AI processing)
   - `GET /api/widget/web-summary/{widget_id}/latest` - Fetch EXISTING summary (from DB)
3. **Data Flow**: 
   - **Generate**: Query → Web Search → AI Summary → Save to DB → Return Summary
   - **Fetch**: Widget ID → Query DB → Return Cached Summary
4. **Frontend Integration**: Widget can generate new summaries or display cached ones

### 🏗️ Development Flow
1. **Phase 1**: Core summary generation (immediate frontend compatibility)
2. **Phase 2**: Enhanced AI capabilities (better summaries)  
3. **Phase 3**: Widget persistence (save favorite search terms)
4. **Phase 4**: Summary history and management
5. **Phase 5**: Background automation (daily updates)

### 🔄 Frontend Integration Points
Current `WebSummaryWidget.tsx` expects:
- **Endpoint**: Needs to replace the TODO with actual API call
- **Request**: `{ query: string }`
- **Response**: `{ id, query, summary, sources[], createdAt }`
- **Error Handling**: Graceful error messages for API failures

## 🚀 Migration Path to AWS
- **SQLite → DynamoDB**: Update database adapters
- **Local Tasks → SQS + Lambda**: Background processing
- **Local Storage → S3**: File storage if needed
- **APScheduler → EventBridge**: Scheduled tasks

## 📝 Development Notes
- **Modular Design**: Each service is independent and testable
- **Error Handling**: Graceful degradation when APIs are unavailable
- **Local First**: Everything works locally without AWS
- **Type Safety**: Full Pydantic models and type hints
- **Logging**: Comprehensive logging for debugging
- **Rate Limiting**: Built-in API rate limiting

## 🎯 Success Criteria

### 🚀 Phase 1 Success (Immediate):
- [ ] `WebSummaryWidget.tsx` can make real API calls (no more mock data)
- [ ] User enters query → gets real AI-powered summary with sources
- [ ] Error handling works when APIs are down
- [ ] Summary data persists in local SQLite database

### 🏆 Overall Success (Complete):
- [ ] User can create multiple web summary widgets on dashboard
- [ ] Each widget can have different search terms
- [ ] Frontend can retrieve latest summaries and history
- [ ] System gracefully handles API failures with fallbacks
- [ ] Code is modular and AWS-migration ready
- [ ] Other widget types (reminders, counters) can be easily added

## 🔄 Next Steps
1. **Get API Keys**: OpenAI + Serper.dev (required for Phase 1)
2. **Start with Phase 1**: Core summary generation endpoint  
3. **Test Frontend Integration**: Update `WebSummaryWidget.tsx` to use real API
4. **Implement incrementally**: One phase at a time
5. **Prepare for scaling**: Design with AWS migration in mind

### 📝 Phase 1 Implementation Order:
1. **Database Setup**: SQLite + widget and summary models
2. **AI Services**: Web search + summarization  
3. **Core API Endpoints**: 
   - `POST /api/widget/web-summary/create` (widget creation + first summary)
   - `POST /api/widget/web-summary/{widget_id}/generate` (NEW summary generation)
   - `GET /api/widget/web-summary/{widget_id}/latest` (FETCH existing summary)
4. **Frontend Update**: Replace mock data with real API calls
5. **Testing**: Verify end-to-end widget lifecycle

### 🎯 Widget Lifecycle Flow:
1. **Frontend**: User clicks "Add Widget" → selects "Web Summary Widget"
2. **Frontend**: User enters initial query → calls `/create` endpoint
3. **Backend**: Creates widget UUID + generates first summary → returns both
4. **Frontend**: Widget displays with widget_id stored for future operations
5. **Frontend**: User enters new query → calls `/generate` with widget_id (AI processing)
6. **Frontend**: Widget refresh → calls `/latest` to get cached summary (fast DB lookup)

### 🔄 API Usage Patterns:
- **Generate New Summary**: Use `/generate` when user wants fresh AI analysis
- **Display Existing Summary**: Use `/latest` for fast loading of cached content
- **Performance**: `/latest` is fast (DB only), `/generate` is slower (AI processing)

### 🎯 Widget Naming Convention:
- **Current Widget**: `web-summary` (AI-powered web search + summarization)
- **Future Widgets**: `reminders`, `counter`, `notes`, `calendar`, etc.
- **URL Pattern**: `/api/widget/{widget-name}/{action}`

---
*This updated gameplan focuses on getting the existing `WebSummaryWidget.tsx` working with a real backend, then expanding to support multiple widgets and advanced features.*
