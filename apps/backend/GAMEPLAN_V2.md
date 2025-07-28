# 🧠 Brainboard Backend Gameplan V2
## AI-Powered Dynamic Dashboard System

This document outlines the implementation plan for the new AI-generated daily dashboard system.

---

## 🎯 Core Concept

**Old System**: Fixed widget layout with static widgets
**New System**: AI generates daily dashboard based on user preferences, frequency settings, and widget configurations

### Key Flow:
1. User configures widgets with frequency preferences
2. AI analyzes user's widget configurations daily
3. AI generates today's dashboard layout
4. Frontend renders the AI-selected widgets with their data

---

## 📊 Database Schema Changes

### Current Tables (to keep):
- `widgets` - Will be renamed/refactored to `dashboard_widgets`
- `summaries` - Will be enhanced for web search data

### New Database Schema:

**Updated Models (SQLAlchemy):**

```python
# KEEP and ENHANCE existing models:

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# RENAME/ENHANCE existing Widget model:
class DashboardWidget(Base):  # Previously Widget
    __tablename__ = "dashboard_widgets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    widget_type = Column(String, nullable=False)  # 'todo', 'websearch', 'alarm', etc.
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    category = Column(String, nullable=True)
    importance = Column(Integer, nullable=True)  # 1-5 scale
    settings = Column(JSON, nullable=True)  # Widget-specific settings
    is_active = Column(Boolean, default=True)
    last_shown_date = Column(Date, nullable=True)  # Track when last shown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# NEW widget-specific tables:
class TodoTask(Base):
    __tablename__ = "todo_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"))
    content = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WebSearchQuery(Base):
    __tablename__ = "websearch_queries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"))
    search_term = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alarm(Base):
    __tablename__ = "alarms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"))
    next_trigger_time = Column(DateTime, nullable=True)
    is_snoozed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Habit(Base):
    __tablename__ = "habits"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"))
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String, ForeignKey("habits.id"))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # 'completed', 'missed', 'partial'
    created_at = Column(DateTime, default=datetime.utcnow)

# ENHANCE existing Summary model for web search data:
class Summary(Base):  # Keep existing, enhance for web search
    __tablename__ = "summaries"
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"))  # Updated FK
    query = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)
    search_results_json = Column(JSON, nullable=True)  # NEW: Store full search results
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Migration Strategy:
1. **Phase 1**: Add new tables while keeping existing ones
2. **Phase 2**: Migrate existing `widgets` data to `dashboard_widgets`
3. **Phase 3**: Update foreign keys and relationships
4. **Phase 4**: Drop old tables

---

## 🛠️ API Endpoints Implementation Plan

### Phase 1: Core Dashboard API

#### 1. Main Dashboard Endpoint
```
GET /api/v1/dashboard/today
```
**Purpose**: Returns AI-generated daily dashboard with all widget data
**Response**: Complete dashboard configuration + data for today

#### 2. Widget Management HQ
```
GET /api/v1/widget/getAll
POST /api/v1/dashboard/widget/add
POST /api/v1/dashboard/widget/update
```

### Phase 2: Widget-Specific APIs

#### ToDo Widget
```
GET /api/v1/widgets/todo/tasks
POST /api/v1/widgets/todo/tasks
GET /api/v1/widgets/todo/tasks/today
POST /api/v1/widgets/todo/tasks/:taskId/updateStatus
```

#### WebSearch Widget
```
POST /api/v1/widgets/websearch/queries/add
GET /api/v1/widgets/websearch/queries
POST /api/v1/widgets/websearch/queries/update
```

#### Alarm Widget
```
GET /api/v1/widgets/alarm
POST /api/v1/widgets/alarm/add
POST /api/v1/widgets/alarm/updateStatus
```

#### Calendar Widget
```
GET /api/v1/widgets/calendar/events?start=startDate&end=endDate
```

#### Habit Tracker Widget
```
GET /api/v1/widgets/habittracker
POST /api/v1/widgets/habittracker/add
GET /api/v1/widgets/habittracker/history?habitId=xxx
POST /api/v1/widgets/habittracker/updateStatus
```

---

## 🤖 AI Dashboard Generation Logic

### Simple Initial Algorithm:
1. **Get User's Active Widgets**: Fetch all `dashboard_widgets` where `is_active = true`
2. **Apply Frequency Filter**: 
   - Daily: Include if last shown != today
   - Weekly: Include if last shown < 7 days ago
   - Monthly: Include if last shown < 30 days ago
3. **Random Selection**: For now, randomly select widgets that meet frequency criteria
4. **Future Enhancement**: Consider importance, user activity patterns, bandwidth

### AI Service Structure:
```python
class DashboardAIService:
    def generate_daily_dashboard(self, user_id: int, date: str) -> List[WidgetInstance]:
        # Simple random selection based on frequency
        pass
    
    def should_include_widget(self, widget: DashboardWidget, date: str) -> bool:
        # Frequency-based logic
        pass
```

---

## 📁 File Structure Implementation Plan

**CURRENT STRUCTURE** (what we have):
```
apps/backend/
├── main.py ✅ (update to include new routers)
├── core/
│   ├── database.py ✅ (update init_db)
│   └── config.py ✅ (add new settings)
├── models/
│   ├── database_models.py ✅ (ADD new models)
│   └── schemas.py ✅ (ADD new schemas)
├── routers/
│   ├── widget_web_summary.py ✅ (KEEP, refactor)
│   └── health.py ✅ (KEEP)
├── services/
│   ├── widget_service.py ✅ (ENHANCE)
│   ├── ai_service.py ✅ (ENHANCE for dashboard AI)
│   ├── web_search_service.py ✅ (KEEP)
│   └── summary_service.py ✅ (KEEP)
└── factories/
    └── service_factory.py ✅ (ENHANCE)
```

**NEW STRUCTURE** (what we'll add):
```
apps/backend/
├── main.py (UPDATE - add new routers)
├── core/
│   ├── database.py (UPDATE - add new models to init_db)
│   ├── config.py (UPDATE - add dashboard settings)
│   └── ai_dashboard.py (NEW - AI generation logic)
├── models/
│   ├── database_models.py (UPDATE - add all new models)
│   └── schemas.py (UPDATE - add all new schemas)
├── routers/
│   ├── dashboard.py (NEW - main dashboard endpoints)
│   ├── widget_web_summary.py (REFACTOR - adapt to new system)
│   ├── health.py (KEEP)
│   └── widgets/ (NEW directory)
│       ├── __init__.py
│       ├── todo.py (NEW)
│       ├── websearch.py (NEW - extracted from widget_web_summary)
│       ├── alarm.py (NEW)
│       ├── calendar.py (NEW)
│       └── habittracker.py (NEW)
├── services/
│   ├── dashboard_ai_service.py (NEW - AI logic)
│   ├── widget_service.py (ENHANCE - adapt to new models)
│   ├── ai_service.py (ENHANCE - dashboard generation)
│   ├── web_search_service.py (KEEP)
│   ├── summary_service.py (KEEP)
│   └── widget_services/ (NEW directory)
│       ├── __init__.py
│       ├── todo_service.py (NEW)
│       ├── websearch_service.py (NEW - extracted from widget_service)
│       ├── alarm_service.py (NEW)
│       ├── calendar_service.py (NEW)
│       └── habittracker_service.py (NEW)
└── factories/
    └── service_factory.py (ENHANCE - add new services)
```

---

## 🚀 Implementation Priority (REVISED)

### Sprint 1: Foundation & Database Migration (Week 1)
1. **Database Migration**:
   - ✅ Add new models to `models/database_models.py`
   - ✅ Update `core/database.py` to include new models
   - ✅ Create migration script for existing data
   - ✅ Add User model and default user creation

2. **Core Dashboard Service**:
   - ✅ Create `core/ai_dashboard.py` with simple frequency-based logic
   - ✅ Create `services/dashboard_ai_service.py`
   - ✅ Update `factories/service_factory.py`

3. **Main Dashboard API**:
   - ✅ Create `routers/dashboard.py` with `/api/v1/dashboard/today` endpoint
   - ✅ Add dashboard schemas to `models/schemas.py`
   - ✅ Update `main.py` to include dashboard router

### Sprint 2: Widget System Refactor (Week 2)
1. **Existing Widget Migration**:
   - ✅ Refactor `routers/widget_web_summary.py` to use new system
   - ✅ Create `routers/widgets/websearch.py` (extracted from web_summary)
   - ✅ Create `services/widget_services/websearch_service.py`
   - ✅ Update existing web search to work with dashboard widgets

2. **Todo Widget Implementation**:
   - ✅ Create `routers/widgets/todo.py`
   - ✅ Create `services/widget_services/todo_service.py`
   - ✅ Add TodoTask model and schemas

3. **Alarm Widget Implementation**:
   - ✅ Create `routers/widgets/alarm.py`
   - ✅ Create `services/widget_services/alarm_service.py`
   - ✅ Add Alarm model and schemas

### Sprint 3: Advanced Widgets (Week 3)
1. **Calendar Widget**:
   - ✅ Create `routers/widgets/calendar.py`
   - ✅ Create `services/widget_services/calendar_service.py`
   - ✅ Calendar events integration

2. **Habit Tracker Widget**:
   - ✅ Create `routers/widgets/habittracker.py`
   - ✅ Create `services/widget_services/habittracker_service.py`
   - ✅ Add Habit and HabitLog models

3. **Widget Management**:
   - ✅ Complete widget CRUD operations
   - ✅ Widget configuration management

### Sprint 4: Enhancement & Testing (Week 4)
1. **AI Enhancement**:
   - ✅ Improve dashboard generation logic
   - ✅ Add importance-based selection
   - ✅ Performance optimization

2. **Integration & Testing**:
   - ✅ End-to-end testing with frontend
   - ✅ Error handling and validation
   - ✅ Documentation updates

---

## 🔄 Data Flow Example

### User Journey:
1. **Setup**: User creates widgets via HQ interface (`POST /api/v1/dashboard/widget/add`)
2. **Daily Generation**: AI runs daily to generate dashboard (`DashboardAIService.generate_daily_dashboard()`)
3. **Frontend Request**: Frontend calls `GET /api/v1/dashboard/today`
4. **Response**: Backend returns complete dashboard with all widget data
5. **Interaction**: User interacts with widgets (complete tasks, snooze alarms, etc.)

### Sample Response from `/api/v1/dashboard/today`:
```json
{
  "date": "2025-07-28",
  "widgets": [
    {
      "id": "widget_123",
      "type": "todo",
      "title": "Daily Tasks",
      "size": "medium",
      "data": {
        "tasks": [...],
        "progress": {...}
      }
    },
    {
      "id": "widget_456", 
      "type": "websearch",
      "title": "AI News Search",
      "size": "medium",
      "data": {
        "search_term": "AI developments",
        "results": [...],
        "charts": [...]
      }
    }
  ]
}
```

---

## 🎯 Success Metrics

1. **API Response Time**: < 500ms for `/api/v1/dashboard/today`
2. **Widget Variety**: AI should select different widget combinations daily
3. **Data Completeness**: All widgets return complete data in single API call
4. **Frequency Compliance**: Widgets appear according to their frequency settings
5. **User Engagement**: Track which widgets users interact with most

---

## 🔮 Future Enhancements

1. **Smart AI Logic**: Use user behavior patterns for widget selection
2. **Layout Optimization**: AI suggests optimal widget arrangements  
3. **Performance Caching**: Cache daily dashboard generation
4. **Real-time Updates**: WebSocket integration for live widget updates
5. **Widget Templates**: Pre-configured widget sets for different user types

---

*This gameplan provides a clear roadmap for transitioning from static widgets to an AI-powered dynamic dashboard system that adapts to user preferences and schedules.*
