# Widget Data Models

This directory contains TypeScript interfaces and types for the Brainboard widget system. The models are designed to work with the API response from `/api/v1/dashboard/today`.

## Overview

The widget system is built around a unified `BaseWidget` interface that contains common properties for all widgets, with specific data structures for each widget type.

## Core Types

### BaseWidget
The main interface that all widgets implement:

```typescript
interface BaseWidget {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  category?: string | null;
  importance?: WidgetImportance | null;
  frequency: WidgetFrequency;
  settings: Record<string, any>;
  data: WidgetData;
}
```

### Widget Types
- `WidgetType`: Union type of all supported widget types
- `WidgetSize`: Widget size options ('small', 'medium', 'large', 'full')
- `WidgetFrequency`: Frequency options ('daily', 'weekly', 'monthly', 'yearly', 'once')
- `WidgetImportance`: Importance scale (1-5)

## Widget-Specific Data Models

### 1. Todo Widget
```typescript
interface TodoWidgetData {
  tasks: TodoTask[];
  stats: TodoStats;
}

interface TodoTask {
  id: string;
  content: string;
  due_date: string | null;
  is_done: boolean;
  created_at: string;
}

interface TodoStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
}
```

### 2. Habit Tracker Widget
```typescript
interface HabitTrackerWidgetData {
  habits: Habit[];
  total_habits: number;
}

interface Habit {
  id: string;
  name: string;
  description?: string;
  streak: number;
  completed_today: boolean;
  created_at: string;
}
```

### 3. Web Search Widget
```typescript
interface WebSearchWidgetData {
  message?: string;
  searches: WebSearch[];
}

interface WebSearch {
  id: string;
  query: string;
  results?: WebSearchResult[];
  last_searched?: string;
}

interface WebSearchResult {
  title: string;
  url: string;
  snippet: string;
}
```

### 4. Web Summary Widget
```typescript
interface WebSummaryWidgetData {
  summaries: WebSummary[];
  total_summaries: number;
}

interface WebSummary {
  id: string;
  url: string;
  title: string;
  summary: string;
  created_at: string;
}
```

### 5. Calendar Widget
```typescript
interface CalendarWidgetData {
  events: CalendarEvent[];
  current_date: string;
  total_events: number;
}

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  description?: string;
  is_completed: boolean;
}
```

### 6. Reminder Widget
```typescript
interface ReminderWidgetData {
  reminders: Reminder[];
  total_reminders: number;
  overdue_count: number;
}

interface Reminder {
  id: string;
  title: string;
  message: string;
  due_date: string;
  is_completed: boolean;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
}
```

## API Response Structure

The main API response from `/api/v1/dashboard/today` follows this structure:

```typescript
interface TodayWidgetsResponse {
  date: string;
  widgets: BaseWidget[];
  stats: DashboardStats;
}

interface DashboardStats {
  total_widgets: number;
  daily_count: number;
  weekly_count: number;
  monthly_count: number;
}
```

## Type Guards

Type guards are provided to safely check widget types:

```typescript
import { 
  isTodoWidget, 
  isHabitTrackerWidget, 
  isWebSearchWidget,
  isWebSummaryWidget,
  isCalendarWidget,
  isReminderWidget
} from '../types';

// Usage example
const renderWidget = (widget: BaseWidget) => {
  if (isTodoWidget(widget)) {
    // widget.data is now typed as TodoWidgetData
    return <TodoWidgetComponent data={widget.data} />;
  }
  
  if (isHabitTrackerWidget(widget)) {
    // widget.data is now typed as HabitTrackerWidgetData
    return <HabitTrackerComponent data={widget.data} />;
  }
  
  // ... handle other widget types
};
```

## Usage Examples

### 1. Fetching Today's Widgets
```typescript
import { dashboardService } from '../services/api';
import { TodayWidgetsResponse } from '../types';

const fetchTodayWidgets = async (): Promise<TodayWidgetsResponse> => {
  return await dashboardService.getTodayWidgets();
};
```

### 2. Rendering Widgets with Type Safety
```typescript
import { BaseWidget, isTodoWidget, isHabitTrackerWidget } from '../types';

const WidgetRenderer: React.FC<{ widget: BaseWidget }> = ({ widget }) => {
  if (isTodoWidget(widget)) {
    return (
      <div>
        <h3>{widget.title}</h3>
        <p>Tasks: {widget.data.stats.total_tasks}</p>
        <p>Completed: {widget.data.stats.completed_tasks}</p>
        {widget.data.tasks.map(task => (
          <div key={task.id}>
            <input type="checkbox" checked={task.is_done} />
            <span>{task.content}</span>
          </div>
        ))}
      </div>
    );
  }
  
  if (isHabitTrackerWidget(widget)) {
    return (
      <div>
        <h3>{widget.title}</h3>
        <p>Total Habits: {widget.data.total_habits}</p>
        {widget.data.habits.map(habit => (
          <div key={habit.id}>
            <span>{habit.name}</span>
            <span>Streak: {habit.streak}</span>
          </div>
        ))}
      </div>
    );
  }
  
  return <div>Unknown widget type: {widget.type}</div>;
};
```

### 3. Working with Widget Settings
```typescript
import { TodoWidgetSettings, HabitTrackerWidgetSettings } from '../types';

const getTodoSettings = (widget: BaseWidget): TodoWidgetSettings => {
  return widget.settings as TodoWidgetSettings;
};

const getHabitSettings = (widget: BaseWidget): HabitTrackerWidgetSettings => {
  return widget.settings as HabitTrackerWidgetSettings;
};
```

## Widget Settings

Each widget type has specific settings that can be configured:

### Todo Widget Settings
- `max_tasks`: Maximum number of tasks to display
- `show_completed`: Whether to show completed tasks
- `sort_by`: Sort order ('created_at', 'due_date', 'priority')

### Habit Tracker Settings
- `streak_goal`: Target streak length
- `reminder_time`: Time for daily reminders
- `show_streaks`: Whether to display streak information

### Web Search Settings
- `max_results`: Maximum search results to display
- `search_engines`: Array of search engines to use
- `auto_search`: Whether to automatically perform searches

## Best Practices

1. **Always use type guards** when working with widget data to ensure type safety
2. **Handle null/undefined values** for optional properties like `category` and `importance`
3. **Use the provided interfaces** instead of creating your own to maintain consistency
4. **Import from the index file** for convenience: `import { BaseWidget, TodoWidgetData } from '../types'`
5. **Validate API responses** before using the data in your components

## Migration from Old Types

If you're migrating from the old widget types:

1. Replace `DashboardWidget` with `BaseWidget`
2. Use the new widget-specific data interfaces instead of generic `any` types
3. Implement type guards for safe widget rendering
4. Update your API service calls to use the new `dashboardService`

## Example API Response

Here's an example of what the API returns:

```json
{
  "date": "2025-07-28",
  "widgets": [
    {
      "id": "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
      "type": "todo",
      "title": "Test Todo Widget",
      "size": "medium",
      "category": "testing",
      "importance": 5,
      "frequency": "daily",
      "settings": {},
      "data": {
        "tasks": [
          {
            "id": "230a0dd7-4532-42bd-8f30-7c0c7aac67cd",
            "content": "Monthly task - Budget review",
            "due_date": null,
            "is_done": false,
            "created_at": "2025-07-28T08:07:09.285093"
          }
        ],
        "stats": {
          "total_tasks": 3,
          "completed_tasks": 1,
          "pending_tasks": 2,
          "completion_rate": 33.33333333333333
        }
      }
    }
  ],
  "stats": {
    "total_widgets": 8,
    "daily_count": 8,
    "weekly_count": 0,
    "monthly_count": 0
  }
}
``` 