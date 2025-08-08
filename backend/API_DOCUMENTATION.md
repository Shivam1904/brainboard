# Brainboard Backend API Documentation

## Overview
The Brainboard Backend API provides a consolidated interface for managing dashboard widgets and daily activities. The API uses a simplified JSON-based schema that consolidates multiple widget types into two main tables.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently using default user ID `user_001` for development. No authentication required.

## API Endpoints

### Health & Status

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Brainboard Backend is running"
}
```

#### GET /
Get API information.

**Response:**
```json
{
  "message": "Brainboard Backend API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### Dashboard Widgets (`/api/v1/dashboard-widgets/`)

#### POST /newwidget
Create a new widget.

**Request Body:**
```json
{
  "widget_type": "alarm",
  "title": "Morning Alarm",
  "frequency": "daily",
  "importance": 0.8,
  "category": "Health",
  "description": "Wake up early",
  "is_permanent": false,
  "widget_config": {
      "alarm_times": ["07:00", "07:15"],
      "is_snoozable": true
  }
}
```

**Response:**
```json
{
  "id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82",
  "user_id": "user_001",
  "widget_type": "alarm",
  "title": "Morning Alarm",
  "frequency": "daily",
  "importance": 0.8,
  "category": "Health",
  "description": "Wake up early",
  "is_permanent": false,
  "widget_config": {
      "alarm_times": ["07:00", "07:15"],
      "is_snoozable": true
  },
  "created_at": "2025-08-07T17:45:30.123456",
  "updated_at": "2025-08-07T17:45:30.123456",
  "delete_flag": false
}
```

#### GET /allwidgets
Get all widgets for the default user.

**Response:**
```json
[
  {
    "id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82",
    "user_id": "user_001",
    "widget_type": "alarm",
    "title": "Morning Alarm",
    "frequency": "daily",
    "importance": 0.8,
    "category": "Health",
    "widget_config": {
        "alarm_times": ["07:00", "07:15"],
        "is_snoozable": true
    },
    "created_at": "2025-08-07T17:45:30.123456",
    "updated_at": "2025-08-07T17:45:30.123456",
    "delete_flag": false
  }
]
```

#### GET /{widget_id}
Get a specific widget by ID.

**Response:**
```json
{
  "id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82",
  "user_id": "user_001",
  "widget_type": "alarm",
  "title": "Morning Alarm",
  "frequency": "daily",
  "importance": 0.8,
  "category": "Health",
  "widget_config": {
      "alarm_times": ["07:00", "07:15"],
      "is_snoozable": true
  },
  "created_at": "2025-08-07T17:45:30.123456",
  "updated_at": "2025-08-07T17:45:30.123456",
  "delete_flag": false
}
```

#### PUT /{widget_id}/update
Update a widget.

**Request Body:**
```json
{
  "title": "Updated Alarm",
  "importance": 0.9,
  "widget_config": {
      "alarm_times": ["06:30", "07:00"],
      "is_snoozable": false
  }
}
```

#### DELETE /{widget_id}/delete
Soft delete a widget.

**Response:**
```json
{
  "message": "Widget deleted successfully"
}
```

#### GET /alloftype/{widget_type}
Get all widgets of a specific type.

**Response:**
```json
[
  {
    "id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82",
    "user_id": "user_001",
    "widget_type": "alarm",
    "title": "Morning Alarm",
    "frequency": "daily",
    "importance": 0.8,
    "category": "Health",
    "widget_config": {
        "alarm_times": ["07:00", "07:15"],
        "is_snoozable": true
    },
    "created_at": "2025-08-07T17:45:30.123456",
    "updated_at": "2025-08-07T17:45:30.123456",
    "delete_flag": false
  }
]
```

### Dashboard (`/api/v1/dashboard/`)

#### GET /getTodayWidgetList
Get today's widget list.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
[
  {
    "id": "daily-widget-id",
    "widget_id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82",
    "priority": "HIGH",
    "reasoning": "Manually added Morning Alarm to today's dashboard",
    "date": "2025-08-07",
    "is_active": true,
    "activity_data": {
        "started_at": null,
        "snoozed_at": null,
        "snooze_until": null,
        "snooze_count": 0
    }
  }
]
```

#### POST /widget/addtotoday/{widget_id}
Add a widget to today's dashboard.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "success": true,
  "message": "Widget added to today's dashboard successfully",
  "daily_widget_id": "daily-widget-id",
  "widget_id": "ac5ffca6-37a7-4ee8-8f5c-f56edf38db82"
}
```

#### POST /widget/removefromtoday/{daily_widget_id}
Remove a widget from today's dashboard.

**Query Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "success": true,
  "message": "DailyWidget is_active updated successfully",
  "daily_widget_id": "daily-widget-id",
  "is_active": false
}
```

#### PUT /daily-widgets/{daily_widget_id}/updateactivity
Update activity data for a daily widget.

**Request Body:**
```json
{
    "started_at": "2025-08-07T07:00:00Z",
    "snoozed_at": "2025-08-07T07:05:00Z",
    "snooze_count": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Activity data updated successfully",
  "activity_data": {
      "started_at": "2025-08-07T07:00:00Z",
      "snoozed_at": "2025-08-07T07:05:00Z",
      "snooze_count": 1
  }
}
```

#### GET /daily-widgets/{daily_widget_id}/getactivity
Get activity data for a daily widget.

**Response:**
```json
{
    "started_at": "2025-08-07T07:00:00Z",
    "snoozed_at": "2025-08-07T07:05:00Z",
    "snooze_count": 1
}
```

## Widget Types

### Alarm Widget
**Widget Type:** `alarm`

**Configuration:**
```json
{
    "alarm_times": ["07:00", "07:15"],
    "target_value": null,
    "is_snoozable": true
}
```

**Activity Data:**
```json
{
    "started_at": "2025-08-07T07:00:00Z",
    "snoozed_at": "2025-08-07T07:05:00Z",
    "snooze_until": "2025-08-07T07:10:00Z",
    "snooze_count": 1
}
```

### Todo Widget
**Widget Type:** `todo`

**Configuration:**
```json
{
    "todo_type": "todo-habit",
    "due_date": "2025-08-07",
    "milestone_list": []
}
```

**Activity Data:**
```json
{
    "status": "in_progress",
    "progress": 50,
    "started_at": "2025-08-07T09:00:00Z"
}
```

### Single Item Tracker Widget
**Widget Type:** `single_item_tracker`

**Configuration:**
```json
{
    "value_type": "number",
    "value_unit": "steps",
    "target_value": "10000"
}
```

**Activity Data:**
```json
{
    "value": "7500",
    "time_added": "2025-08-07T18:00:00Z",
    "notes": "Good progress today"
}
```

### Web Search Widget
**Widget Type:** `websearch`

**Configuration:**
```json
{
    "search_query_detailed": "latest AI developments"
}
```

**Activity Data:**
```json
{
    "status": "completed",
    "reaction": "Very interesting findings",
    "summary": "AI is advancing rapidly in 2024",
    "source_json": {...},
    "completed_at": "2025-08-07T10:00:00Z"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Widget not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create widget: Database connection error"
}
```

## Database Schema

### dashboard_widget_details
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR | Primary key |
| user_id | VARCHAR | User identifier |
| widget_type | VARCHAR | Type of widget |
| frequency | VARCHAR | Frequency (daily, weekly, monthly) |
| frequency_details | JSON | Frequency-specific details |
| importance | FLOAT | Importance score (0.0-1.0) |
| title | VARCHAR | Widget title |
| description | TEXT | Widget description |
| category | VARCHAR | Widget category |
| is_permanent | BOOLEAN | Whether widget is permanent |
| widget_config | JSON | Widget-specific configuration |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| delete_flag | BOOLEAN | Soft delete flag |

### daily_widgets
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR | Primary key |
| widget_id | VARCHAR | Reference to dashboard_widget_details |
| priority | VARCHAR | Priority level |
| reasoning | TEXT | Reason for inclusion |
| date | DATE | Date of the daily widget |
| is_active | BOOLEAN | Whether widget is active |
| activity_data | JSON | Activity state data |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| delete_flag | BOOLEAN | Soft delete flag |

## Development Notes

### Default User
- All operations use `user_001` as the default user
- No authentication required for development
- Easy to extend for multi-user support

### Transaction Management
- Services handle business logic only
- Routes manage transactions (commit/rollback)
- Consistent error handling across all endpoints

### JSON Flexibility
- Widget configurations stored as JSON
- Activity data stored as JSON
- MongoDB-ready document structure
- Easy to add new widget types

## Testing

Run the test script to verify API functionality:
```bash
cd backend
python test_new_api.py
```

Expected output:
```
✅ Health check: 200
✅ Root endpoint: 200
✅ Create widget: 200
✅ Get specific widget: 200
✅ Get all widgets: 200
✅ Get widgets by type: 200
✅ Dashboard endpoints: 200
``` 