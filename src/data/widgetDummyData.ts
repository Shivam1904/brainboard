// Dummy Data - API-Compatible
// This dummy data matches the actual API response structures exactly

import {
  TodayWidgetsResponse,
  DailyWidget,
  TodoTodayResponse,
  TodoActivity,
  AlarmDetailsAndActivityResponse,
  AlarmDetails,
  AlarmActivity,
  TrackerDetailsAndActivityResponse,
  TrackerDetails,
  TrackerActivity,
  WebSearchSummaryAndActivityResponse,
  WebSearchDetails,
  WebSearchActivity,
  WebSearchAISummaryResponse
} from '../types';

// ============================================================================
// DASHBOARD DUMMY DATA
// ============================================================================

export const getDummyTodayWidgets = (): TodayWidgetsResponse => {
  return {
    date: new Date().toISOString().split('T')[0],
    widgets: [
      {
        daily_widget_id: "daily-todo-001",
        widget_ids: ["widget-todo-001", "widget-todo-002", "widget-todo-003"],
        widget_type: "todo",
        priority: "HIGH",
        reasoning: "Todo widget is essential for daily productivity",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-alarm-001",
        widget_ids: ["widget-alarm-001"],
        widget_type: "alarm",
        priority: "HIGH",
        reasoning: "Alarm widget for important reminders",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-tracker-001",
        widget_ids: ["widget-tracker-001"],
        widget_type: "singleitemtracker",
        priority: "MEDIUM",
        reasoning: "Tracker widget for health monitoring",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-websearch-001",
        widget_ids: ["widget-websearch-001"],
        widget_type: "websearch",
        priority: "LOW",
        reasoning: "Web search widget for research tasks",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      }
    ],
    total_widgets: 4,
    ai_generated: true,
    last_updated: "2024-01-15T10:00:00Z"
  };
};

// ============================================================================
// TODO WIDGET DUMMY DATA
// ============================================================================

export const getDummyTodoTodayResponse = (todoType: 'habit' | 'task'): TodoTodayResponse => {
  return {
    todo_type: todoType,
    todos: [
      {
        activity_id: "activity-001",
        widget_id: "widget-todo-001",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-001",
        title: todoType === 'task' ? "Complete project documentation" : "Morning meditation",
        todo_type: todoType,
        description: todoType === 'task' ? "Finish the project documentation by end of day" : "Practice mindfulness for 10 minutes",
        due_date: "2024-01-20",
        status: "pending",
        progress: 0.0,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z"
      },
      {
        activity_id: "activity-002",
        widget_id: "widget-todo-002",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-002",
        title: todoType === 'task' ? "Review code changes" : "Drink 8 glasses of water",
        todo_type: todoType,
        description: todoType === 'task' ? "Review and approve pending code changes" : "Stay hydrated throughout the day",
        due_date: "2024-01-16",
        status: "in_progress",
        progress: 0.5,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z"
      }
    ],
    total_todos: 2
  };
};

// ============================================================================
// ALARM WIDGET DUMMY DATA
// ============================================================================

export const getDummyAlarmDetailsAndActivity = (widgetId: string): AlarmDetailsAndActivityResponse => {
  return {
    alarm_details: {
      id: "alarm-details-001",
      title: "Morning Workout Alarm",
      alarm_times: ["06:00", "06:15"],
      enabled: true
    },
    activity: {
      id: "alarm-activity-001",
      status: "pending",
      snooze_count: 0,
      last_triggered: "2024-01-15T06:00:00Z"
    }
  };
};

// ============================================================================
// SINGLE ITEM TRACKER WIDGET DUMMY DATA
// ============================================================================

export const getDummyTrackerDetailsAndActivity = (widgetId: string): TrackerDetailsAndActivityResponse => {
  return {
    tracker_details: {
      id: "tracker-details-001",
      title: "Weight Tracker",
      value_type: "number",
      unit: "kg",
      target_value: 70
    },
    activity: {
      id: "tracker-activity-001",
      current_value: 72.5,
      last_updated: "2024-01-15T08:00:00Z"
    }
  };
};

// ============================================================================
// WEBSEARCH WIDGET DUMMY DATA
// ============================================================================

export const getDummyWebSearchSummaryAndActivity = (widgetId: string): WebSearchSummaryAndActivityResponse => {
  return {
    websearch_details: {
      id: "websearch-details-001",
      title: "AI Research",
      search_query: "latest artificial intelligence developments 2024"
    },
    activity: {
      id: "websearch-activity-001",
      status: "completed",
      reaction: "positive",
      summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
      sources: [
        "https://example.com/ai-news-1",
        "https://example.com/ai-news-2",
        "https://example.com/ai-news-3"
      ]
    }
  };
};

export const getDummyWebSearchAISummary = (widgetId: string): WebSearchAISummaryResponse => {
  return {
    summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
    sources: [
      "https://example.com/ai-news-1",
      "https://example.com/ai-news-2",
      "https://example.com/ai-news-3"
    ],
    generated_at: "2024-01-15T10:00:00Z",
    confidence_score: 0.85
  };
};

// ============================================================================
// LEGACY COMPATIBILITY (for existing widget components)
// ============================================================================

// These functions maintain compatibility with existing widget components
// They will be removed once widgets are updated to use API types directly

export const getDummyAlarms = (widgetId: string) => {
  return getDummyAlarmDetailsAndActivity(widgetId);
};

export const getDummyTasks = () => {
  const response = getDummyTodoTodayResponse('task');
  return response.todos;
};

export const getDummyWebSearchResult = (searchQuery: string) => {
  const response = getDummyWebSearchSummaryAndActivity('widget-websearch-001');
  return response.activity;
};

export const getDummyTracker = (widgetId: string) => {
  return getDummyTrackerDetailsAndActivity(widgetId);
};

export const getDummyCalendarData = (year: number, month: number) => {
  // Calendar widget is not in the API, so we return empty data
  return {
    year,
    month,
    days: [],
    events: [],
    milestones: []
  };
};

export const getDummyAllSchedulesWidgets = () => {
  // AllSchedules widget is UI-only, so we return empty data
  return [];
};

export const getDummyWebSummary = (query: string) => {
  return getDummyWebSearchAISummary('widget-websearch-001');
};

export const getDummyReminders = () => {
  // Reminders are handled by alarm widget in the API
  return [];
}; 