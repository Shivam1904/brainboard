# Dashboard API Architecture

## Overview

The Brainboard system now uses a two-tier API architecture:

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
}
```

### Features
- **Dynamic Layout**: Server determines which widgets to show and where
- **Widget Configuration**: Each widget gets specific config parameters
- **Priority System**: Widgets can be prioritized for positioning
- **Enable/Disable**: Widgets can be conditionally shown
- **Date-based**: Different configurations for different days

## 2. Widget Level APIs

Each widget type has its own API endpoints for fetching specific data:

### Everyday Web Search Widget
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

## Implementation Status

### ✅ Completed
- Dashboard API configuration (`src/config/api.ts`)
- TypeScript types (`src/types/dashboard.ts`)
- Dummy data for development (`src/data/dashboardDummyData.ts`)
- Dashboard loading logic with error handling
- Widget configuration passing
- Everyday Web Search widget with config support

### 🔄 In Progress
- Backend API implementation
- Real API integration (currently using dummy data)

### 📋 Planned
- All other widget implementations
- Real-time updates
- Widget data caching
- Offline support

## Benefits

1. **Centralized Control**: Server controls what widgets appear each day
2. **Flexible Layout**: Dynamic positioning based on user needs
3. **Widget Independence**: Each widget manages its own data
4. **Configuration**: Widgets can be configured per user/day
5. **Scalability**: Easy to add new widgets and configurations
6. **Performance**: Widgets load their data independently

## Usage Example

```typescript
// Dashboard fetches configuration
const dashboardConfig = await fetch('/api/dashboard/today?date=2024-01-15');

// Creates widgets with layout and config
const widgets = dashboardConfig.widgets.map(config => ({
  id: config.id,
  type: config.type,
  layout: config.layout,
  config: config.config
}));

// Each widget fetches its own data
widgets.forEach(widget => {
  switch(widget.type) {
    case 'everydayWebSearch':
      // Widget calls its own API
      const searchData = await fetch('/api/web-search/scheduled');
      break;
    case 'everydayTaskList':
      // Widget calls its own API
      const taskData = await fetch('/api/tasks/today');
      break;
  }
});
```

## Next Steps

1. Implement backend API endpoints
2. Add real API integration (uncomment imports)
3. Implement remaining widgets
4. Add real-time updates
5. Add user preferences and customization 