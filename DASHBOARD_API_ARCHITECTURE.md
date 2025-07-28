# Dashboard API Architecture

## Overview

The Brainboard system uses a two-tier API architecture:

1. **Dashboard Level API**: Fetches today's widget configuration and layout
2. **Widget Level APIs**: Each widget fetches its own specific data

## Architecture Flow

```
Dashboard Loads
    ↓
Fetch Today's Widget Configuration
    ↓
Create Widgets with Layout & Config
    ↓
Each Widget Fetches Its Own Data
    ↓
Display Complete Dashboard
```

## 1. Dashboard Level API

### Endpoint
- `GET /api/dashboard/today?date=YYYY-MM-DD`

### Response Structure
```typescript
interface TodayWidgetsResponse {
  date: string; // ISO date string
  widgets: DashboardWidgetConfig[];
  layout?: {
    gridCols: number;
    gridRows: number;
  };
}

interface DashboardWidgetConfig {
  id: string;
  type: string; // widget type
  layout: {
    x: number;
    y: number;
    w: number;
    h: number;
    minW?: number;
    minH?: number;
    maxW?: number;
    maxH?: number;
  };
  config?: Record<string, any>; // Widget-specific configuration
  priority?: number;
  enabled?: boolean;
  scheduledItem?: ScheduledItem; // Reference to the original scheduled item
}

interface ScheduledItem {
  id: string;
  title: string;
  type: string; // 'userTask', 'userHabit', 'itemTracker', 'webSearch', etc.
  frequency: string; // 'daily', 'weekly-2', 'onGym', 'alternate', 'hourly', etc.
  category?: string; // 'health', 'self-imp', 'finance', 'awareness', etc.
  importance?: 'High' | 'Medium' | 'Low';
  alarm?: string; // '[7am]', '[every 2 hr]', '[list of times]', etc.
  searchQuery?: string; // For webSearch type
  config?: Record<string, any>;
}
```

### Features
- **Dynamic Layout**: Server determines which widgets to show and where
- **Widget Configuration**: Each widget gets specific config parameters
- **Priority System**: Widgets can be prioritized for positioning
- **Enable/Disable**: Widgets can be conditionally shown
- **Date-based**: Different configurations for different days
- **Scheduled Items**: Each widget references its original scheduled item

## 2. Widget Level APIs

Each widget type has its own API endpoints for fetching specific data:

### Web Search Widget
- `GET /api/web-search/scheduled` - Get scheduled searches for today
- `GET /api/web-search/result` - Get search result for specific search

### Task List Widget
- `GET /api/tasks/today` - Get today's tasks
- `POST /api/tasks/mission` - Add new mission
- `PUT /api/tasks/update` - Update task status

### Calendar Widget
- `GET /api/calendar/monthly` - Get monthly calendar data

### Reminders Widget
- `GET /api/reminders` - Get today's reminders
- `POST /api/reminders/create` - Create new reminder

### All Schedules Widget
- `GET /api/schedules` - Get all scheduled items
- `POST /api/schedules` - Create new schedule
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule

## 3. Widget Schedule Management

### Supported Widget Types
- `userTask` - Tasks with importance levels
- `userHabit` - Habits with alarms and importance
- `itemTracker` - Metric tracking
- `webSearch` - Web search queries
- `alarm` - Time-based alarms
- `calendar` - Calendar widgets
- `weatherWig` - Weather information
- `statsWidget` - Statistics display
- `newsWidget` - News feeds

### Schedule Properties
- **Title** - Widget name
- **Type** - Widget type
- **Frequency** - Schedule frequency (daily, weekly-2, hourly, etc.)
- **Category** - Organization category (health, finance, etc.)
- **Importance** - Priority level (High, Medium, Low)
- **Alarm** - Time specifications
- **Search Query** - For web search widgets

## Implementation Status

### ✅ Completed
- Dashboard API configuration (`src/config/api.ts`)
- TypeScript types (`src/types/dashboard.ts`)
- Dummy data for development (`src/data/dashboardDummyData.ts`)
- Dashboard loading logic with error handling
- Widget configuration passing
- Web Search widget with config support
- All Schedules widget with CRUD functionality
- Dynamic widget creation from scheduled items
- Type-specific forms and validation

### 🔄 In Progress
- Backend API implementation
- Real API integration (currently using dummy data)

### 📋 Planned
- All other widget implementations
- Real-time updates
- Widget data caching
- Offline support
- User preferences and customization

## Benefits

1. **Centralized Control**: Server controls what widgets appear each day
2. **Flexible Layout**: Dynamic positioning based on user needs
3. **Widget Independence**: Each widget manages its own data
4. **Configuration**: Widgets can be configured per user/day
5. **Scalability**: Easy to add new widgets and configurations
6. **Performance**: Widgets load their data independently
7. **Schedule Management**: Complete CRUD operations for all schedules
8. **Type Safety**: Full TypeScript support with proper interfaces

## Usage Example

```typescript
// Dashboard fetches configuration
const dashboardConfig = await fetch('/api/dashboard/today?date=2024-01-15');

// Creates widgets with layout and config
const widgets = dashboardConfig.widgets.map(config => ({
  id: config.id,
  type: config.type,
  layout: config.layout,
  config: config.config,
  scheduledItem: config.scheduledItem
}));

// Each widget fetches its own data
widgets.forEach(widget => {
  switch(widget.type) {
    case 'webSearch':
      // Widget calls its own API with search query
      const searchData = await fetch(`/api/web-search/result?query=${widget.scheduledItem.searchQuery}`);
      break;
    case 'userTask':
      // Widget calls its own API
      const taskData = await fetch('/api/tasks/today');
      break;
  }
});
```

## All Schedules Widget Features

### CRUD Operations
- **Create**: Add new schedules with type-specific forms
- **Read**: View all scheduled items with details
- **Update**: Edit existing schedules with dynamic forms
- **Delete**: Remove schedules with confirmation

### Form Features
- **Dynamic Forms**: Fields appear/disappear based on widget type
- **Validation**: Required field validation
- **Type-Specific Fields**: Different fields for different widget types
- **Category Management**: Color-coded categories for organization

### UI Features
- **Large Widget**: 16x12 size for comprehensive management
- **Modal Interfaces**: Clean form interfaces for editing
- **Responsive Design**: Scrollable content with proper spacing
- **Loading States**: Professional loading indicators
- **Error Handling**: Graceful error states with retry options

## Next Steps

1. Implement backend API endpoints
2. Add real API integration (uncomment imports)
3. Implement remaining widgets
4. Add real-time updates
5. Add user preferences and customization
6. Implement widget data caching
7. Add offline support
8. Create analytics dashboard 