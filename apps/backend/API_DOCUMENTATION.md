# Brainboard API Documentation v2.0.0

## Overview
Brainboard is an AI-powered dashboard backend that provides RESTful APIs for managing various widget types including todos, alarms, single item trackers, and web searches. The API is built with FastAPI and follows REST conventions.

**Base URL**: `http://localhost:8000`  
**API Version**: `/api/v1`  
**Documentation**: `/docs` (Swagger UI)

## Authentication
Currently, the API uses a default user system for development. All endpoints automatically use the default user (`default@brainboard.com`).

## CORS Configuration
The API allows requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (React dev server)

---

## 1. Health Check Endpoints

### 1.1 Basic Health Check
**GET** `/api/v1/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "brainboard-api",
  "version": "2.0.0"
}
```

### 1.2 Detailed Health Check
**GET** `/api/v1/health/detailed`

Get detailed health status including external services.

**Response:**
```json
{
  "status": "healthy",
  "service": "brainboard-api",
  "version": "2.0.0",
  "services": {
    "database": "healthy",
    "ai_services": "not_implemented_yet"
  }
}
```

---

## 2. Dashboard Management Endpoints

### 2.1 Get Today's Widget List
**GET** `/api/v1/dashboard/getTodayWidgetList`

Get AI-generated daily widget selections for a specific date.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "date": "2024-01-15",
  "widgets": [
    {
      "daily_widget_id": "uuid",
      "widget_ids": ["widget1", "widget2"],
      "widget_type": "todo",
      "priority": "HIGH",
      "reasoning": "AI reasoning for widget selection",
      "date": "2024-01-15",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_widgets": 1,
  "ai_generated": true,
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### 2.2 Get All Widget List
**GET** `/api/v1/dashboard/getAllWidgetList`

Get all dashboard widget configurations for the user.

**Response:**
```json
{
  "widgets": [
    {
      "id": "widget-uuid",
      "widget_type": "todo",
      "frequency": "daily",
      "importance": 0.8,
      "title": "Daily Tasks",
      "category": "productivity",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_widgets": 1
}
```

### 2.3 Add New Widget
**POST** `/api/v1/dashboard/widget/addnew`

Create a new dashboard widget.

**Request Body:**
```json
{
  "widget_type": "todo",
  "frequency": "daily",
  "importance": 0.8,
  "title": "Daily Tasks",
  "category": "productivity"
}
```

**Widget Types:**
- `todo`: Task and habit management
- `alarm`: Time-based reminders
- `singleitemtracker`: Single value tracking
- `websearch`: Web search and AI summaries

**Frequency Options:**
- `daily`: Daily widgets
- `weekly`: Weekly widgets
- `monthly`: Monthly widgets

**Response:**
```json
{
  "message": "Widget created successfully",
  "widget_id": "widget-uuid",
  "widget_type": "todo",
  "title": "Daily Tasks"
}
```

### 2.4 Get Todo List by Type
**GET** `/api/v1/dashboard/getTodoList/{todo_type}`

Get all todo details filtered by type (habit/task).

**Path Parameters:**
- `todo_type`: Either "habit" or "task"

**Response:**
```json
{
  "todo_type": "task",
  "todos": [
    {
      "id": "todo-uuid",
      "title": "Complete project",
      "todo_type": "task",
      "description": "Finish the project documentation",
      "due_date": "2024-01-20",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_todos": 1
}
```

---

## 3. Todo Widget Endpoints

### 3.1 Get Today's Todo List
**GET** `/api/v1/widgets/todo/getTodayTodoList/{todo_type}`

Get today's todo activities filtered by type.

**Path Parameters:**
- `todo_type`: Either "habit" or "task"

**Response:**
```json
{
  "todo_type": "task",
  "todos": [
    {
      "activity_id": "activity-uuid",
      "widget_id": "widget-uuid",
      "daily_widget_id": "daily-widget-uuid",
      "todo_details_id": "todo-details-uuid",
      "title": "Complete project",
      "todo_type": "task",
      "description": "Finish the project documentation",
      "due_date": "2024-01-20",
      "status": "pending",
      "progress": 0.5,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_todos": 1
}
```

### 3.2 Update Todo Activity
**POST** `/api/v1/widgets/todo/updateActivity/{activity_id}`

Update todo activity status and progress.

**Path Parameters:**
- `activity_id`: Activity UUID

**Request Body:**
```json
{
  "status": "completed",
  "progress": 1.0,
  "updated_by": "user-id"
}
```

**Status Options:**
- `pending`: Not started
- `in_progress`: In progress
- `completed`: Completed
- `cancelled`: Cancelled

**Response:**
```json
{
  "activity_id": "activity-uuid",
  "status": "completed",
  "progress": 1.0,
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 3.3 Get Todo Item Details and Activity
**GET** `/api/v1/widgets/todo/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}`

Get todo item details and activity for a specific widget.

**Path Parameters:**
- `daily_widget_id`: Daily widget UUID
- `widget_id`: Widget UUID

**Response:**
```json
{
  "todo_details": {
    "id": "todo-details-uuid",
    "title": "Complete project",
    "todo_type": "task",
    "description": "Finish the project documentation",
    "due_date": "2024-01-20"
  },
  "activity": {
    "id": "activity-uuid",
    "status": "pending",
    "progress": 0.5,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

### 3.4 Get Todo Details
**GET** `/api/v1/widgets/todo/getTodoDetails/{widget_id}`

Get todo details for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "id": "todo-details-uuid",
  "title": "Complete project",
  "todo_type": "task",
  "description": "Finish the project documentation",
  "due_date": "2024-01-20",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 3.5 Update Todo Details
**POST** `/api/v1/widgets/todo/updateDetails/{todo_details_id}`

Update todo details.

**Path Parameters:**
- `todo_details_id`: Todo details UUID

**Request Body:**
```json
{
  "title": "Updated project title",
  "description": "Updated description",
  "due_date": "2024-01-25",
  "todo_type": "task"
}
```

**Response:**
```json
{
  "id": "todo-details-uuid",
  "title": "Updated project title",
  "description": "Updated description",
  "due_date": "2024-01-25",
  "todo_type": "task",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

## 4. Alarm Widget Endpoints

### 4.1 Get Alarm Details and Activity
**GET** `/api/v1/widgets/alarm/getAlarmDetailsAndActivity/{widget_id}`

Get alarm details and activity for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "alarm_details": {
    "id": "alarm-details-uuid",
    "title": "Morning Alarm",
    "alarm_times": ["09:00", "09:15"],
    "enabled": true
  },
  "activity": {
    "id": "activity-uuid",
    "status": "snoozed",
    "snooze_count": 2,
    "last_triggered": "2024-01-15T09:00:00Z"
  }
}
```

### 4.2 Update Alarm Activity
**POST** `/api/v1/widgets/alarm/updateActivity/{activity_id}`

Update alarm activity (start/snooze).

**Path Parameters:**
- `activity_id`: Activity UUID

**Request Body:**
```json
{
  "status": "started",
  "snooze_count": 0,
  "updated_by": "user-id"
}
```

**Status Options:**
- `pending`: Not triggered
- `triggered`: Alarm triggered
- `started`: User started alarm
- `snoozed`: User snoozed alarm
- `dismissed`: User dismissed alarm

**Response:**
```json
{
  "activity_id": "activity-uuid",
  "status": "started",
  "snooze_count": 0,
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 4.3 Get Alarm Details
**GET** `/api/v1/widgets/alarm/getAlarmDetails/{widget_id}`

Get alarm details for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "id": "alarm-details-uuid",
  "title": "Morning Alarm",
  "alarm_times": ["09:00", "09:15"],
  "enabled": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 4.4 Update Alarm Details
**POST** `/api/v1/widgets/alarm/updateDetails/{alarm_details_id}`

Update alarm details.

**Path Parameters:**
- `alarm_details_id`: Alarm details UUID

**Request Body:**
```json
{
  "title": "Updated Alarm Title",
  "alarm_times": ["08:30", "09:00"],
  "enabled": true
}
```

**Response:**
```json
{
  "id": "alarm-details-uuid",
  "title": "Updated Alarm Title",
  "alarm_times": ["08:30", "09:00"],
  "enabled": true,
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

## 5. Single Item Tracker Widget Endpoints

### 5.1 Get Tracker Details and Activity
**GET** `/api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}`

Get tracker details and activity for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "tracker_details": {
    "id": "tracker-details-uuid",
    "title": "Water Intake",
    "value_type": "number",
    "unit": "glasses",
    "target_value": 8
  },
  "activity": {
    "id": "activity-uuid",
    "current_value": 5,
    "last_updated": "2024-01-15T10:00:00Z"
  }
}
```

### 5.2 Update Tracker Activity
**POST** `/api/v1/widgets/single-item-tracker/updateActivity/{activity_id}`

Update tracker activity value and time.

**Path Parameters:**
- `activity_id`: Activity UUID

**Request Body:**
```json
{
  "current_value": 6,
  "updated_by": "user-id"
}
```

**Response:**
```json
{
  "activity_id": "activity-uuid",
  "current_value": 6,
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 5.3 Get Tracker Details
**GET** `/api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}`

Get tracker details for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "id": "tracker-details-uuid",
  "title": "Water Intake",
  "value_type": "number",
  "unit": "glasses",
  "target_value": 8,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 5.4 Update Tracker Details
**POST** `/api/v1/widgets/single-item-tracker/updateDetails/{tracker_details_id}`

Update tracker details.

**Path Parameters:**
- `tracker_details_id`: Tracker details UUID

**Request Body:**
```json
{
  "title": "Updated Tracker Title",
  "target_value": 10,
  "unit": "cups"
}
```

**Response:**
```json
{
  "id": "tracker-details-uuid",
  "title": "Updated Tracker Title",
  "target_value": 10,
  "unit": "cups",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

## 6. WebSearch Widget Endpoints

### 6.1 Get Summary and Activity
**GET** `/api/v1/widgets/websearch/getSummaryAndActivity/{widget_id}`

Get websearch summary and activity for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "websearch_details": {
    "id": "websearch-details-uuid",
    "title": "AI Research",
    "search_query": "latest AI developments"
  },
  "activity": {
    "id": "activity-uuid",
    "status": "completed",
    "reaction": "positive",
    "summary": "AI summary of search results",
    "sources": ["url1", "url2"]
  }
}
```

### 6.2 Update WebSearch Activity
**POST** `/api/v1/widgets/websearch/updateActivity/{activity_id}`

Update websearch activity (status, reaction, summary, sources).

**Path Parameters:**
- `activity_id`: Activity UUID

**Request Body:**
```json
{
  "status": "completed",
  "reaction": "positive",
  "summary": "Updated AI summary",
  "sources": ["url1", "url2", "url3"],
  "updated_by": "user-id"
}
```

**Status Options:**
- `pending`: Not started
- `searching`: Searching in progress
- `summarizing`: AI summarization in progress
- `completed`: Completed
- `failed`: Failed

**Reaction Options:**
- `positive`: User liked the results
- `negative`: User didn't like the results
- `neutral`: User had neutral reaction

**Response:**
```json
{
  "activity_id": "activity-uuid",
  "status": "completed",
  "reaction": "positive",
  "summary": "Updated AI summary",
  "sources": ["url1", "url2", "url3"],
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 6.3 Get WebSearch Details
**GET** `/api/v1/widgets/websearch/getWebsearchDetails/{widget_id}`

Get websearch details for a specific widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "id": "websearch-details-uuid",
  "title": "AI Research",
  "search_query": "latest AI developments",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 6.4 Update WebSearch Details
**POST** `/api/v1/widgets/websearch/updateDetails/{websearch_details_id}`

Update websearch details.

**Path Parameters:**
- `websearch_details_id`: WebSearch details UUID

**Request Body:**
```json
{
  "title": "Updated Research Title",
  "search_query": "updated search query"
}
```

**Response:**
```json
{
  "id": "websearch-details-uuid",
  "title": "Updated Research Title",
  "search_query": "updated search query",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 6.5 Get AI Summary
**GET** `/api/v1/widgets/websearch/getaisummary/{widget_id}`

Get AI-generated summary for a specific websearch widget.

**Path Parameters:**
- `widget_id`: Widget UUID

**Response:**
```json
{
  "summary": "AI-generated summary of search results",
  "sources": ["url1", "url2"],
  "generated_at": "2024-01-15T10:00:00Z",
  "confidence_score": 0.85
}
```

---

## 7. AI Endpoints

### 7.1 Generate Today's Plan
**POST** `/api/v1/ai/generate_today_plan`

Generate AI-powered daily plan with widget selections.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "date": "2024-01-15",
  "generated_widgets": [
    {
      "widget_ids": ["widget1", "widget2"],
      "widget_type": "todo",
      "priority": "HIGH",
      "reasoning": "AI reasoning for selection"
    }
  ],
  "total_widgets": 1,
  "ai_generated": true,
  "generated_at": "2024-01-15T10:00:00Z"
}
```

### 7.2 Generate Web Summary List
**POST** `/api/v1/ai/generate_web_summary_list`

Generate AI-powered web summaries for websearch widgets.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "date": "2024-01-15",
  "summaries": [
    {
      "widget_id": "widget-uuid",
      "summary": "AI-generated summary",
      "sources": ["url1", "url2"],
      "confidence_score": 0.85
    }
  ],
  "total_summaries": 1,
  "generated_at": "2024-01-15T10:00:00Z"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Service temporarily unavailable"
}
```

---

## Data Types

### Widget Types
- `todo`: Task and habit management
- `alarm`: Time-based reminders  
- `singleitemtracker`: Single value tracking
- `websearch`: Web search and AI summaries

### Frequency Types
- `daily`: Daily widgets
- `weekly`: Weekly widgets
- `monthly`: Monthly widgets

### Priority Types
- `HIGH`: High priority
- `LOW`: Low priority

### Todo Status Types
- `pending`: Not started
- `in_progress`: In progress
- `completed`: Completed
- `cancelled`: Cancelled

### Alarm Status Types
- `pending`: Not triggered
- `triggered`: Alarm triggered
- `started`: User started alarm
- `snoozed`: User snoozed alarm
- `dismissed`: User dismissed alarm

### WebSearch Status Types
- `pending`: Not started
- `searching`: Searching in progress
- `summarizing`: AI summarization in progress
- `completed`: Completed
- `failed`: Failed

### Reaction Types
- `positive`: User liked the results
- `negative`: User didn't like the results
- `neutral`: User had neutral reaction

---

## Usage Examples

### Frontend Integration Example

```javascript
// Get today's widgets
const response = await fetch('http://localhost:8000/api/v1/dashboard/getTodayWidgetList');
const todayWidgets = await response.json();

// Update todo activity
const updateResponse = await fetch(`http://localhost:8000/api/v1/widgets/todo/updateActivity/${activityId}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: 'completed',
    progress: 1.0
  })
});

// Create new widget
const createResponse = await fetch('http://localhost:8000/api/v1/dashboard/widget/addnew', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    widget_type: 'todo',
    frequency: 'daily',
    importance: 0.8,
    title: 'Daily Tasks',
    category: 'productivity'
  })
});
```

---

## Notes for Frontend AI

1. **Default User**: All endpoints automatically use the default user system
2. **CORS**: Configured for localhost development servers
3. **Error Handling**: Always check response status and handle errors gracefully
4. **Real-time Updates**: Consider implementing polling or WebSocket for real-time updates
5. **Data Validation**: Validate all request data before sending to API
6. **Loading States**: Implement loading states for async operations
7. **Caching**: Consider caching frequently accessed data like widget lists
8. **AI Integration**: Use AI endpoints for intelligent widget suggestions and summaries 