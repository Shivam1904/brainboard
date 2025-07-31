# SingleItemTracker Widget Migration Guide

## 🎯 **MISSION**
Migrate the SingleItemTracker widget from the old `/apps/backend` to the new clean `/backend` architecture, following established patterns and maintaining database field compatibility.

## 📋 **BACKGROUND & CONTEXT**

### **Backend Migration Status**
- ✅ **COMPLETED**: Alarm widget migration (fully functional)
- ✅ **COMPLETED**: Daily widget system migration  
- ✅ **COMPLETED**: Widget creation API
- ✅ **COMPLETED**: Chat API
- ✅ **COMPLETED**: TODO widget migration (todo-habit, todo-task, todo-event)
- 🔄 **NEXT**: SingleItemTracker widget migration (this task)

### **SingleItemTracker Overview**
SingleItemTracker is used for tracking single values over time (e.g., weight, steps, pages read, etc.). It's a simple but powerful widget for habit tracking and goal monitoring.

### **Key Principles**
1. **Preserve database fields** - Don't change existing table schemas
2. **Follow established patterns** - Use alarm widget as template
3. **Clean architecture** - Separation of concerns
4. **Async/await** - All database operations
5. **Consistent naming** - Follow existing conventions
6. **API parity** - Ensure all old endpoints have equivalents

## 🏗️ **FILE ARCHITECTURE**

### **Files to Create**
```
/backend
├── models/
│   ├── single_item_tracker_details.py      # SingleItemTracker details model
│   └── single_item_tracker_item_activity.py # SingleItemTracker activities model
├── services/
│   └── single_item_tracker_service.py      # SingleItemTracker business logic
├── schemas/
│   └── single_item_tracker.py              # SingleItemTracker request/response schemas
├── routes/
│   └── single_item_tracker.py              # SingleItemTracker endpoints
└── main.py                                 # FastAPI app (add single_item_tracker router)
```

### **Files to Update**
```
/backend
├── models/
│   ├── __init__.py                         # Export new models
│   ├── dashboard_widget_details.py         # Add relationship
│   └── daily_widget.py                     # Add relationship
├── services/
│   ├── __init__.py                         # Export SingleItemTrackerService
│   └── widget_service.py                   # Add single_item_tracker creation logic
├── schemas/
│   └── widget.py                           # Add singleitemtracker to WidgetType enum
└── generate_dummy_data.py                  # Add dummy data generation
```

## 📊 **DATABASE SCHEMA (Preserve Exactly)**

### **SingleItemTracker Details Table** (`single_item_tracker_details`)
```sql
- id (String, PK, UUID)
- widget_id (String, FK to dashboard_widget_details.id)
- title (String, NOT NULL)
- value_type (String, NOT NULL) - 'number', 'text', 'decimal'
- value_unit (String, nullable) - 'kg', 'pages', 'steps'
- target_value (String, nullable) - Target value as string
- created_at (DateTime)
- created_by (String)
- updated_at (DateTime)
- updated_by (String)
- delete_flag (Boolean, default=False)
```

### **SingleItemTracker Item Activity Table** (`single_item_tracker_item_activities`)
```sql
- id (String, PK, UUID)
- daily_widget_id (String, FK to daily_widgets.id)
- widget_id (String, FK to dashboard_widget_details.id)
- singleitemtrackerdetails_id (String, FK to single_item_tracker_details.id)
- value (String, nullable) - Current value
- time_added (DateTime, nullable) - When value was added
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
- `apps/backend/models/database/single_item_tracker_details.py` - Original model
- `apps/backend/models/database/single_item_tracker_item_activity.py` - Original activity model

## 🎯 **IMPLEMENTATION TASKS**

### **Phase 1: Analysis & Planning**
1. **Study the old SingleItemTracker implementation**
   - ✅ Examined old models in `apps/backend/models/database/`
   - ✅ Identified all fields and relationships
   - ✅ Noted business logic: value tracking with units and targets
   - ✅ Single widget type (no multiple types like TODO)

2. **Plan the migration**
   - ✅ Map old fields to new structure
   - ✅ Identify required API endpoints
   - ✅ Plan value type handling (number, text, decimal)
   - ✅ Consider validation requirements

### **Phase 2: Models**
1. **Create `backend/models/single_item_tracker_details.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_details.py pattern

2. **Create `backend/models/single_item_tracker_item_activity.py`**
   - Inherit from `BaseModel`
   - Include all fields from old model
   - Add proper relationships
   - Follow alarm_item_activity.py pattern

3. **Update `backend/models/__init__.py`**
   - Export new models

4. **Update relationship models**
   - Add relationships to `DashboardWidgetDetails`
   - Add relationships to `DailyWidget`

### **Phase 3: Schemas**
1. **Create `backend/schemas/single_item_tracker.py`**
   - Request schemas (CreateTrackerRequest, UpdateTrackerRequest, etc.)
   - Response schemas (TrackerDetailsResponse, TrackerActivityResponse, etc.)
   - Follow alarm.py pattern exactly
   - Add proper validation for value_type, value_unit

2. **Update `backend/schemas/widget.py`**
   - Add `SINGLEITEMTRACKER = "singleitemtracker"` to `WidgetType` enum
   - Update `CreateWidgetRequest` to include tracker-specific fields
   - Add validation for tracker fields

### **Phase 4: Services**
1. **Create `backend/services/single_item_tracker_service.py`**
   - Implement all SingleItemTracker business logic
   - Follow alarm_service.py patterns
   - Include methods for CRUD operations
   - Include activity tracking methods
   - Handle value type validation

2. **Update `backend/services/__init__.py`**
   - Export SingleItemTrackerService

3. **Update `backend/services/widget_service.py`**
   - Add SingleItemTracker widget creation logic
   - Follow alarm pattern
   - Handle tracker-specific field mapping

### **Phase 5: Routes**
1. **Create `backend/routes/single_item_tracker.py`**
   - Implement all SingleItemTracker endpoints
   - Follow alarm.py patterns exactly
   - Include proper error handling
   - Use dependency injection

2. **Update `backend/main.py`**
   - Include single_item_tracker router

### **Phase 6: Integration**
1. **Update `backend/generate_dummy_data.py`**
   - Add SingleItemTracker dummy data generation
   - Create proper relationships
   - Include realistic tracker data

2. **Test all endpoints**
   - Create comprehensive test script
   - Test all CRUD operations
   - Test value tracking functionality

## 🔧 **KEY IMPLEMENTATION DETAILS**

### **Value Type Handling**
SingleItemTracker supports different value types:

1. **Value Type Validation**:
```python
class ValueType(str, Enum):
    NUMBER = "number"
    TEXT = "text"
    DECIMAL = "decimal"
```

2. **Value Unit Examples**:
```python
# Common units for different trackers
UNITS = {
    "weight": ["kg", "lbs", "g"],
    "steps": ["steps", "km", "miles"],
    "reading": ["pages", "books", "minutes"],
    "exercise": ["minutes", "sets", "reps"]
}
```

3. **Value Validation**:
```python
# Validate value based on type
def validate_value(value: str, value_type: str) -> bool:
    if value_type == "number":
        return value.isdigit()
    elif value_type == "decimal":
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif value_type == "text":
        return len(value) > 0
    return False
```

### **Required Endpoints**
- `GET /api/v1/single-item-tracker/getTrackerDetails/{widget_id}` - Get tracker details
- `GET /api/v1/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}` - Get details + activities
- `POST /api/v1/single-item-tracker/updateActivity/{activity_id}` - Update tracker activity
- `POST /api/v1/single-item-tracker/updateDetails/{tracker_details_id}` - Update tracker details
- `GET /api/v1/single-item-tracker/user/{user_id}` - Get user's trackers

### **Widget Creation Fields**
When creating a SingleItemTracker widget, the form should include:
- **Fixed fields**: Widget Type, Title, Frequency, Importance, Category
- **Tracker-specific fields**: 
  - `value_type` (number/text/decimal)
  - `value_unit` (kg, pages, steps, etc.)
  - `target_value` (optional target)

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
1. **`backend/test_scripts/test_single_item_tracker_api.py`**
   - Test all SingleItemTracker endpoints
   - Follow test_alarm_api.py patterns
   - Test value tracking functionality

2. **Update `backend/test_scripts/run_tests.py`**
   - Include SingleItemTracker test suite

### **Test Coverage**
- Tracker creation via widget service
- Tracker details retrieval
- Tracker activity tracking
- Value updates and validation
- Error handling
- All CRUD operations

### **Test Scenarios**
1. **Weight Tracker**: value_type="number", value_unit="kg", target_value="70"
2. **Steps Tracker**: value_type="number", value_unit="steps", target_value="10000"
3. **Reading Tracker**: value_type="number", value_unit="pages", target_value="30"
4. **Text Tracker**: value_type="text", value_unit=None, target_value=None

## 🚨 **CRITICAL REQUIREMENTS**

### **DO NOT:**
- ❌ Change existing database field names
- ❌ Remove any fields from old models
- ❌ Use different naming conventions
- ❌ Skip error handling
- ❌ Use sync database operations
- ❌ Forget value type validation

### **MUST:**
- ✅ Follow alarm widget patterns exactly
- ✅ Use async/await everywhere
- ✅ Include proper error handling
- ✅ Add comprehensive tests
- ✅ Update all necessary files
- ✅ Maintain database compatibility
- ✅ Validate value types and units
- ✅ Ensure API parity with old backend

## 📚 **RESOURCES**

### **Study These Files First:**
1. `backend/models/alarm_details.py` - Model structure
2. `backend/services/alarm_service.py` - Service patterns
3. `backend/schemas/alarm.py` - Schema patterns
4. `backend/routes/alarm.py` - Route patterns
5. `apps/backend/models/database/single_item_tracker_details.py` - Original model
6. `apps/backend/models/database/single_item_tracker_item_activity.py` - Original activity model

### **Key Patterns to Follow:**
- **Model inheritance**: `from .base import BaseModel`
- **Service initialization**: `def __init__(self, db: AsyncSession)`
- **Schema validation**: Use Pydantic `Field` with constraints
- **Route dependencies**: Use `Depends(get_db_session_dependency)`
- **Error handling**: Use utility functions from `utils.errors`
- **Value validation**: Implement proper type checking

## 🎯 **SUCCESS CRITERIA**

✅ All SingleItemTracker endpoints working
✅ Database operations successful
✅ Error handling implemented
✅ Tests passing
✅ Follows established patterns
✅ No breaking changes to existing functionality
✅ Swagger docs generated correctly
✅ API parity with old backend achieved
✅ Value type validation working
✅ Dummy data generation complete

## 🔄 **SPECIFIC CONSIDERATIONS FOR SINGLEITEMTRACKER**

1. **Value Type Handling**: Support number, text, and decimal types with proper validation
2. **Unit Management**: Handle various units (kg, steps, pages, etc.) flexibly
3. **Target Values**: Support optional target values for goal tracking
4. **Time Tracking**: Track when values are added with `time_added` field
5. **Data Validation**: Ensure values match their declared types
6. **User Experience**: Make it easy to add new values and track progress

## 📋 **API ENDPOINTS TO IMPLEMENT**

### **Required Endpoints (from aa.txt)**
- `GET /api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}`
- `POST /api/v1/widgets/single-item-tracker/updateDetails/{singleitemtrackerdetails_id}`
- `GET /api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}`
- `POST /api/v1/widgets/single-item-tracker/updateActivity/{SingleItemTrackerItemActivity_id}`

### **Additional Endpoints (for completeness)**
- `GET /api/v1/single-item-tracker/user/{user_id}` - Get user's trackers
- `POST /api/v1/single-item-tracker/addValue/{activity_id}` - Add new value

---

**Remember**: The alarm widget is your primary template. Follow its patterns exactly, just replace "alarm" with "single_item_tracker" and adapt the specific fields and logic for SingleItemTracker functionality. 