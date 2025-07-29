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
        daily_widget_id: "daily-todo-habit-001",
        widget_ids: ["widget-todo-habit-001"],
        widget_type: "todo-habit",
        priority: "HIGH",
        reasoning: "Habit tracker is essential for daily routines",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-todo-task-001",
        widget_ids: ["widget-todo-task-001"],
        widget_type: "todo-task",
        priority: "HIGH",
        reasoning: "Task list is essential for daily productivity",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-todo-event-001",
        widget_ids: ["widget-todo-event-001"],
        widget_type: "todo-event",
        priority: "LOW",
        reasoning: "Event tracker for important appointments",
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
        priority: "LOW",
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
    total_widgets: 6,
    ai_generated: true,
    last_updated: "2024-01-15T10:00:00Z"
  };
};

// ============================================================================
// TODO WIDGET DUMMY DATA
// ============================================================================

export const getDummyTodoTodayResponse = (todoType: 'habit' | 'task' | 'event'): TodoTodayResponse => {
  if(todoType === 'event') {
    return {
      todo_type: todoType,
      todos: [
        {
          id: "activity-001",
          widget_id: "widget-todo-001",
          daily_widget_id: "daily-todo-001",
          todo_details_id: "todo-details-001",
          title: "Event 1",
          todo_type: todoType,
          description: "Event 1 description",
          due_date: "2024-01-20",
          status: "pending",
          progress: 0,
          created_at: "2024-01-15T10:00:00Z",
          updated_at: "2024-01-15T10:00:00Z"
        }
      ],
      total_todos: 1
    }
  }
  return {
    todo_type: todoType,
    todos: [
      {
        id: "activity-001",
        widget_id: "widget-todo-001",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-001",
        title: todoType === 'task' ? "Complete project documentation" : todoType === 'habit' ? "Morning meditation everyday" : "",
        todo_type: todoType,
        description: todoType === 'task' ? "Finish the project documentation by end of day" : todoType === 'habit' ? "Practice mindfulness for 10 minutes" : "",
        due_date: "2024-01-20",
        status: "pending",
        progress: 0,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z"
      },
      {
        id: "activity-002",
        widget_id: "widget-todo-002",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-002",
        title: todoType === 'task' ? "Review code changes" : "Drink 8 glasses of water",
        todo_type: todoType,
        description: todoType === 'task' ? "Review and approve pending code changes" : "Stay hydrated throughout the day",
        due_date: "2024-01-16",
        status: "in progress",
        progress: 50,
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
      widget_id: widgetId,
      title: "Morning Workout Alarm",
      description: "Alarm for morning workout routine",
      alarm_times: ["06:00", "06:15"],
      target_value: "workout",
      is_snoozable: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "alarm-activity-001",
      started_at: "",
      snoozed_at: "",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
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
      widget_id: widgetId,
      title: "Weight Tracker",
      value_type: "number",
      value_unit: "kg",
      target_value: "70",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "tracker-activity-001",
      value: "72.5",
      time_added: "2024-01-15T08:00:00Z",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
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
      widget_id: widgetId,
      title: "AI Research",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "websearch-activity-001",
      status: "completed",
      reaction: "positive",
      summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
      source_json: {
        sources: [
          "https://example.com/ai-news-1",
          "https://example.com/ai-news-2",
          "https://example.com/ai-news-3"
        ]
      },
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    }
  };
};

export const getDummyWebSearchAISummary = (widgetId: string): WebSearchAISummaryResponse => {
  return {
    ai_summary_id: "ai-summary-001",
    widget_id: widgetId,
    query: "AI Research",
    summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
    sources: [
      {
        title: "AI News Article 1",
        url: "https://example.com/ai-news-1"
      },
      {
        title: "AI News Article 2", 
        url: "https://example.com/ai-news-2"
      },
      {
        title: "AI News Article 3",
        url: "https://example.com/ai-news-3"
      }
    ],
    search_successful: true,
    results_count: 3,
    ai_model_used: "gpt-3.5-turbo",
    generation_type: "ai_generated",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z"
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