# Backend Refactoring Plan - Consolidated JSON Approach

- inside folder brainboard/backend/

## Goal
Consolidate all details and activity tables into just 2 main tables with JSON columns:
- `dashboard_widget_details` (consolidated details in JSON)
- `daily_widgets` (consolidated activities in JSON)

## Final Architecture Decision: JSON Columns ✅

### Why JSON Columns:
- **MongoDB Ready**: Perfect document structure
- **Schema Flexibility**: Easy to add new widget types
- **Storage Efficiency**: No null fields
- **Query Flexibility**: Rich MongoDB aggregation support
- **Type Flexibility**: Different structures per widget type

## New Table Structure

### 1. Enhanced dashboard_widget_details
```sql
CREATE TABLE dashboard_widget_details (
    -- Base fields
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    widget_type VARCHAR NOT NULL, -- 'alarm', 'todo', 'single_item_tracker', 'websearch'
    frequency VARCHAR NOT NULL,
    frequency_details JSON, -- Contains all frequency specific configuration

    importance FLOAT,
    title VARCHAR NOT NULL,
    description VARCHAR,
    category VARCHAR,
    is_permanent BOOLEAN DEFAULT FALSE, -- Always false (handpicked true cases)
    
    -- Consolidated details fields (JSON)
    widget_config JSON NOT NULL, -- Contains all widget-specific configuration
    
    -- Audit fields
    created_at TIMESTAMP,
    created_by VARCHAR,
    updated_at TIMESTAMP,
    updated_by VARCHAR,
    delete_flag BOOLEAN DEFAULT FALSE
);
```

### 2. Enhanced daily_widgets
```sql
CREATE TABLE daily_widgets (
    -- Base fields
    id VARCHAR PRIMARY KEY,
    widget_id VARCHAR, -- foreign key 
    priority VARCHAR NOT NULL,
    reasoning TEXT,
    date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Consolidated activity fields (JSON)
    activity_data JSON NOT NULL, -- Contains all activity-specific data
    
    -- Audit fields
    created_at TIMESTAMP,
    created_by VARCHAR,
    updated_at TIMESTAMP,
    updated_by VARCHAR,
    delete_flag BOOLEAN DEFAULT FALSE
);
```

## Complete Implementation Plan

### Phase 1: Database Migration ⚙️
- [ ] No need for migration. will start with a fresh database.

### Phase 2: Model Updates 🏗️

#### 2.1 Update dashboard_widget_details.py
- [ ] Remove all relationship imports
- [ ] Add `widget_config` JSON field
- [ ] Add helper methods:
  - `get_alarm_config()` → returns alarm-specific config
  - `get_todo_config()` → returns todo-specific config
  - `get_tracker_config()` → returns tracker-specific config
  - `get_websearch_config()` → returns websearch-specific config
  - `update_widget_config()` → updates specific widget config
- [ ] Remove all relationship definitions

#### 2.2 Update daily_widget.py
- [ ] Remove all relationship imports
- [ ] Add `activity_data` JSON field
- [ ] Add helper methods:
  - `get_alarm_activity()` → returns alarm activity data
  - `get_todo_activity()` → returns todo activity data
  - `get_tracker_activity()` → returns tracker activity data
  - `get_websearch_activity()` → returns websearch activity data
  - `update_activity_data()` → updates specific activity data
- [ ] Remove all relationship definitions

#### 2.3 Update models/__init__.py
- [ ] Remove imports for old detail/activity models
- [ ] Keep only: `DashboardWidgetDetails`, `DailyWidget`, `DailyWidgetsAIOutput`, `WebSearchSummaryAIOutput`

### Phase 3: Service Layer Consolidation 🔧

#### 3.1 Create DashboardWidgetService
- [ ] Create `services/dashboard_widget_service.py`
- [ ] Implement CRUD operations:
  - `create_widget(user_id, widget_type, config_data)`
  - `get_widget(widget_id)`
  - `get_user_widgets(user_id)`
  - `update_widget(widget_id, update_data)`
  - `delete_widget(widget_id)`
  - `get_widgets_by_type(user_id, widget_type)`
- [ ] Add widget-specific methods:
  - `create_alarm_widget(user_id, alarm_config)`
  - `create_todo_widget(user_id, todo_config)`
  - `create_tracker_widget(user_id, tracker_config)`
  - `create_websearch_widget(user_id, websearch_config)`

#### 3.2 Enhance DailyWidgetService
- [ ] Update `services/daily_widget_service.py`
- [ ] Add activity-specific methods:
  - `create_alarm_activity(daily_widget_id, activity_data)`
  - `create_todo_activity(daily_widget_id, activity_data)`
  - `create_tracker_activity(daily_widget_id, activity_data)`
  - `create_websearch_activity(daily_widget_id, activity_data)`
  - `update_activity(daily_widget_id, activity_data)`
  - `get_activity_data(daily_widget_id)`

#### 3.3 Update ServiceFactory
- [ ] Update `services/service_factory.py`
- [ ] Remove old service properties
- [ ] Add new service properties:
  - `dashboard_widget_service`
  - `daily_widget_service`

#### 3.4 Delete Old Services
- [ ] Delete `alarm_service.py`
- [ ] Delete `todo_service.py`
- [ ] Delete `single_item_tracker_service.py`
- [ ] Delete `websearch_service.py`
- [ ] Delete `widget_service.py`

### Phase 4: Route Layer Simplification 🌐

#### 4.1 Create DashboardWidgets Routes
- [ ] Create `routes/dashboard_widgets.py`
- [ ] Implement endpoints:
  - `POST /dashboard-widgets` → Create widget
  - `GET /dashboard-widgets` → Get all user widgets
  - `GET /dashboard-widgets/{widget_id}` → Get specific widget
  - `PUT /dashboard-widgets/{widget_id}` → Update widget
  - `DELETE /dashboard-widgets/{widget_id}` → Update widget active flag = 0
  - `GET /dashboard-widgets/type/{widget_type}` → Get widgets by type
- [ ] Add widget-specific endpoints:
  - `POST /dashboard-widgets/alarm` → Create alarm widget
  - `POST /dashboard-widgets/todo` → Create todo widget
  - `POST /dashboard-widgets/tracker` → Create tracker widget
  - `POST /dashboard-widgets/websearch` → Create websearch widget

#### 4.2 Enhance DailyWidgets Routes
- [ ] Update `routes/daily_widgets.py`
- [ ] Add activity endpoints:
  - `POST /daily-widgets/{daily_widget_id}/activity` → Create activity
  - `PUT /daily-widgets/{daily_widget_id}/activity` → Update activity
  - `GET /daily-widgets/{daily_widget_id}/activity` → Get activity data
- [ ] Add widget-specific activity endpoints:
  - `POST /daily-widgets/{daily_widget_id}/alarm-activity`
  - `POST /daily-widgets/{daily_widget_id}/todo-activity`
  - `POST /daily-widgets/{daily_widget_id}/tracker-activity`
  - `POST /daily-widgets/{daily_widget_id}/websearch-activity`

#### 4.3 Delete Old Routes
- [ ] Delete `routes/alarm.py`
- [ ] Delete `routes/todo.py`
- [ ] Delete `routes/single_item_tracker.py`
- [ ] Delete `routes/websearch.py`
- [ ] Delete `routes/widgets.py`

#### 4.4 Update Route Registration
- [ ] Update `main.py` to register new routes
- [ ] Remove old route registrations

### Phase 5: Schema Updates 📋

#### 5.1 Create DashboardWidget Schemas
- [ ] Create `schemas/dashboard_widget.py`
- [ ] Define schemas:
  - `DashboardWidgetCreate`
  - `DashboardWidgetUpdate`
  - `DashboardWidgetResponse`
  - `AlarmWidgetCreate`
  - `TodoWidgetCreate`
  - `TrackerWidgetCreate`
  - `WebSearchWidgetCreate`

#### 5.2 Update DailyWidget Schemas
- [ ] Update `schemas/daily_widget.py`
- [ ] Add activity schemas:
  - `ActivityData`
  - `AlarmActivityData`
  - `TodoActivityData`
  - `TrackerActivityData`
  - `WebSearchActivityData`

#### 5.3 Delete Old Schemas
- [ ] Delete `schemas/alarm.py`
- [ ] Delete `schemas/todo.py`
- [ ] Delete `schemas/single_item_tracker.py`
- [ ] Delete `schemas/websearch.py`
- [ ] Delete `schemas/widget.py`

### Phase 6: AI Integration Updates 🤖
- [ ] Will do later

### Phase 7: Testing & Validation ✅
- [ ] NO DB MIGRATION
- [ ] NO TESTING. Allow the user to test

### Phase 8: Deployment 🚀
- [ ] NO DEPLOYMENT. Allow the user to deploy

### 9. Cleanup
- [ ] Remove old migration files
- [ ] Update documentation
- [ ] Clean up any temporary files
- [ ] Archive old code if needed

## File Structure After Refactoring

```
backend/
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── dashboard_widget_details.py (enhanced with JSON)
│   ├── daily_widget.py (enhanced with JSON)
│   ├── daily_widgets_ai_output.py (preserved)
│   └── websearch_summary_ai_output.py (preserved)
├── services/
│   ├── __init__.py
│   ├── dashboard_widget_service.py (new consolidated service)
│   ├── daily_widget_service.py (enhanced)
│   ├── ai_service.py (preserved)
│   ├── intent_service.py (preserved)
│   ├── session_service.py (preserved)
│   └── service_factory.py (updated)
├── routes/
│   ├── __init__.py
│   ├── dashboard_widget_routes.py (new consolidated routes)
│   ├── daily_widget_routes.py (enhanced)
│   ├── ai.py (preserved)
│   ├── chat.py (preserved)
│   └── dashboard.py (updated)  -- take care of addtotoday and removefromtoday functions.
├── schemas/
│   ├── __init__.py
│   ├── dashboard_widget.py (new)
│   ├── daily_widget.py (enhanced)
│   ├── ai.py (preserved)
│   └── chat.py (preserved)
```

## JSON Structure Examples

### widget_config Examples:
```json
// Alarm widget
{
  "alarm_times": ["07:00", "07:15"],
  "target_value": null,
  "is_snoozable": true
}

// Todo widget  
{
  "todo_type": "todo-habit",
  "due_date": null
}

// Single Item Tracker
{
  "value_type": "number",
  "value_unit": "glasses",
  "target_value": "8"
}

// WebSearch widget
{
  "search_query": "tech news",
  "frequency": "daily"
}
```

### activity_data Examples:
```json
// Alarm activity
{
  "started_at": "2024-01-15T07:00:00Z",
  "snoozed_at": "2024-01-15T07:05:00Z", 
  "snooze_until": "2024-01-15T07:10:00Z",
  "snooze_count": 1
}

// Todo activity
{
  "status": "in_progress",
  "progress": 50,
  "started_at": "2024-01-15T09:00:00Z"
}

// Single Item Tracker activity
{
  "value": "6",
  "time_added": "2024-01-15T14:30:00Z",
  "notes": "After lunch"
}

// WebSearch activity
{
  "status": "completed",
  "reaction": "useful",
  "summary": "AI generated summary...",
  "source_json": {...},
  "completed_at": "2024-01-15T10:00:00Z"
}
```

## Benefits After Refactoring

1. **Ultra Clean Architecture**: Only 2 main tables instead of 10+
2. **Simplified Services**: 2 main services instead of 6+
3. **Unified Routes**: 2 main route files instead of 6+
4. **MongoDB Ready**: Perfect document structure for migration
5. **Schema Flexibility**: Easy to add new widget types
6. **Storage Efficiency**: No null fields
7. **Query Flexibility**: Rich MongoDB aggregation support
8. **Type Flexibility**: Different structures per widget type
9. **Easier Maintenance**: Less code to maintain and debug
10. **Better Performance**: Fewer joins, simpler queries

This refactoring will result in a much cleaner, simpler, and MongoDB-optimized backend architecture.


