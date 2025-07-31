# TODO Widget Migration Guide

## 🎯 **MISSION**
Migrate the TODO widget from the old `/apps/backend` to the new clean `/backend` architecture, following the established patterns and maintaining database field compatibility.

## 📋 **BACKGROUND & CONTEXT**

### **Backend Migration Status**
- ✅ **COMPLETED**: Alarm widget migration (fully functional)
- ✅ **COMPLETED**: Daily widget system migration  
- ✅ **COMPLETED**: Widget creation API
- ✅ **COMPLETED**: Chat API
- 🔄 **NEXT**: TODO widget migration (this task)

### **Architecture Overview**
We migrated from a complex `/apps/backend` to a clean, modular `/backend` structure:
- **Old**: `/apps/backend` (complex, hard to maintain)
- **New**: `/backend` (clean, modular, scalable)

### **Key Principles**
1. **Preserve database fields** - Don't change existing table schemas
2. **Follow established patterns** - Use alarm widget as template
3. **Clean architecture** - Separation of concerns
4. **Async/await** - All database operations
5. **Consistent naming** - Follow existing conventions

## 🏗️ **FILE ARCHITECTURE (CRITICAL)**

### **Current Structure (Follow This Exactly)**
```
/backend
├── models/                     # SQLAlchemy models
│   ├── base.py                # Base model (inherits from)
│   ├── dashboard_widget_details.py  # Parent widget table
│   ├── alarm_details.py       # Alarm-specific details
│   ├── alarm_item_activity.py # Alarm activities
│   └── [NEW] todo_details.py  # TODO-specific details
│   └── [NEW] todo_item_activity.py # TODO activities
├── services/                   # Business logic
│   ├── alarm_service.py       # Alarm business logic (template)
│   ├── widget_service.py      # Widget creation logic
│   └── [NEW] todo_service.py  # TODO business logic
├── schemas/                    # Pydantic schemas
│   ├── alarm.py               # Alarm request/response schemas
│   ├── widget.py              # Widget schemas
│   └── [NEW] todo.py          # TODO request/response schemas
├── routes/                     # HTTP endpoints
│   ├── alarm.py               # Alarm endpoints (template)
│   ├── widgets.py             # Widget endpoints
│   └── [NEW] todo.py          # TODO endpoints
└── main.py                     # FastAPI app (add todo router)
```

## 📊 **DATABASE SCHEMA (Preserve Exactly)**

### **TODO Details Table** (`todo_details`)
```sql
- id (String, PK, UUID)
- widget_id (String, FK to dashboard_widget_details.id)
- title (String, NOT NULL)
- todo_type (String, NOT NULL) - 'task' or 'habit'
- description (Text, nullable)
- due_date (Date, nullable)
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

### **TODO Item Activity Table** (`todo_item_activities`)
```sql
- id (String, PK, UUID)
- daily_widget_id (String, FK to daily_widgets.id)
- widget_id (String, FK to dashboard_widget_details.id)
- tododetails_id (String, FK to todo_details.id)
- status (String, NOT NULL) - 'in progress', 'completed', 'pending'
- progress (Integer, nullable) - Progress percentage
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
- `backend/models/base.py` - Base model to inherit from

### **Services (Study These Patterns)**
- `backend/services/alarm_service.py` - Complete service implementation
- `backend/services/widget_service.py` - Widget creation logic

### **Schemas (Study These Patterns)**
- `backend/schemas/alarm.py` - Request/response schemas
- `backend/schemas/widget.py` - Widget schemas

### **Routes (Study These Patterns)**
- `backend/routes/alarm.py` - Complete route implementation
- `backend/routes/widgets.py` - Widget routes

### **Old Implementation (Reference)**
- `apps/backend/models/database/todo_details.py` - Original TODO model
- `apps/backend/models/database/todo_item_activity.py` - Original TODO activity model

## 🎯 **IMPLEMENTATION TASKS**

### **Phase 1: Models**
1. **Create `backend/models/todo_details.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_details.py pattern

2. **Create `backend/models/todo_item_activity.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_item_activity.py pattern

3. **Update `backend/models/__init__.py`**
   - Export new models

### **Phase 2: Schemas**
1. **Create `backend/schemas/todo.py`**
   - Request schemas (CreateTodoRequest, UpdateTodoRequest, etc.)
   - Response schemas (TodoDetailsResponse, TodoActivityResponse, etc.)
   - Follow alarm.py pattern exactly

### **Phase 3: Services**
1. **Create `backend/services/todo_service.py`**
   - Implement all TODO business logic
   - Follow alarm_service.py patterns
   - Include methods for CRUD operations
   - Include activity tracking methods

2. **Update `backend/services/__init__.py`**
   - Export TodoService

### **Phase 4: Routes**
1. **Create `backend/routes/todo.py`**
   - Implement all TODO endpoints
   - Follow alarm.py patterns exactly
   - Include proper error handling
   - Use dependency injection

2. **Update `backend/main.py`**
   - Include todo router

### **Phase 5: Integration**
1. **Update `backend/services/widget_service.py`**
   - Add TODO widget creation logic
   - Follow alarm pattern

2. **Update `backend/generate_dummy_data.py`**
   - Add TODO dummy data generation

## 🔧 **KEY IMPLEMENTATION DETAILS**

### **Naming Conventions**
- **Models**: `TodoDetails`, `TodoItemActivity`
- **Services**: `TodoService`
- **Schemas**: `TodoDetailsResponse`, `TodoActivityResponse`
- **Routes**: `/api/v1/todo/...`

### **Required Endpoints**
- `GET /api/v1/todo/getTodoDetails/{widget_id}` - Get TODO details
- `GET /api/v1/todo/getTodoDetailsAndActivity/{widget_id}` - Get details + activities
- `POST /api/v1/todo/updateStatus/{activity_id}` - Update TODO status
- `POST /api/v1/todo/updateProgress/{activity_id}` - Update progress
- `POST /api/v1/todo/updateDetails/{todo_details_id}` - Update TODO details
- `GET /api/v1/todo/user/{user_id}` - Get user's TODOs

### **Error Handling**
- Use `utils.errors.raise_not_found()` for 404s
- Use `utils.errors.raise_database_error()` for DB errors
- Follow alarm.py error handling patterns

### **Database Operations**
- All async/await
- Use SQLAlchemy select/update/insert
- Proper transaction handling
- Follow alarm_service.py patterns

## 🧪 **TESTING REQUIREMENTS**

### **Test Files to Create**
1. **`backend/test_scripts/test_todo_api.py`**
   - Test all TODO endpoints
   - Follow test_alarm_api.py patterns

2. **Update `backend/test_scripts/run_tests.py`**
   - Include TODO test suite

### **Test Coverage**
- TODO creation via widget service
- TODO details retrieval
- TODO activity tracking
- Status updates
- Progress updates
- Error handling

## 🚨 **CRITICAL REQUIREMENTS**

### **DO NOT:**
- ❌ Change existing database field names
- ❌ Remove any fields from old models
- ❌ Use different naming conventions
- ❌ Skip error handling
- ❌ Use sync database operations

### **MUST:**
- ✅ Follow alarm widget patterns exactly
- ✅ Use async/await everywhere
- ✅ Include proper error handling
- ✅ Add comprehensive tests
- ✅ Update all necessary files
- ✅ Maintain database compatibility

## 📚 **RESOURCES**

### **Study These Files First:**
1. `backend/models/alarm_details.py` - Model structure
2. `backend/services/alarm_service.py` - Service patterns
3. `backend/schemas/alarm.py` - Schema patterns
4. `backend/routes/alarm.py` - Route patterns
5. `apps/backend/models/database/todo_details.py` - Original TODO model
6. `apps/backend/models/database/todo_item_activity.py` - Original TODO activity

### **Key Patterns to Follow:**
- **Model inheritance**: `from .base import BaseModel`
- **Service initialization**: `def __init__(self, db: AsyncSession)`
- **Schema validation**: Use Pydantic `Field` with constraints
- **Route dependencies**: Use `Depends(get_db_session_dependency)`
- **Error handling**: Use utility functions from `utils.errors`

## 🎯 **SUCCESS CRITERIA**

✅ All TODO endpoints working
✅ Database operations successful
✅ Error handling implemented
✅ Tests passing
✅ Follows established patterns
✅ No breaking changes to existing functionality
✅ Swagger docs generated correctly

---

**Remember**: The alarm widget is your template. Follow its patterns exactly, just replace "alarm" with "todo" and adapt the specific fields and logic for TODO functionality. 