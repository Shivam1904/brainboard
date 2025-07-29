import { TodayWidgetsResponse } from '../types';

// Dummy data that matches the new API response structure
export const getDummyTodayWidgets = (): TodayWidgetsResponse => {
  return {
    date: new Date().toISOString().split('T')[0],
    widgets: [
      {
        id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
        daily_widget_id: "daily-todo-001",
        title: "Daily Task Manager",
        widget_type: "todo",
        category: "productivity",
        importance: 5,
        frequency: "daily",
        position: 0,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Todo widget is essential for daily productivity",
        settings: null,
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "68c2ab14-23e0-41f9-8d98-50b04d01961d",
        daily_widget_id: "daily-habit-001",
        title: "Daily Habits",
        widget_type: "habittracker",
        category: "health",
        importance: 5,
        frequency: "daily",
        position: 1,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Habit tracking is important for health goals",
        settings: {
          streak_goal: 30,
          reminder_time: "09:00"
        },
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "08db6466-e5a4-4c6c-9341-0cd2366360a4",
        daily_widget_id: "daily-websearch-001",
        title: "FastAPI Research Widget",
        widget_type: "websearch",
        category: "research",
        importance: 3,
        frequency: "daily",
        position: 2,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Web search widget for research tasks",
        settings: null,
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "b2df57d5-d5a5-4eb0-8c27-fe5edc67dcde",
        daily_widget_id: "daily-schedules-001",
        title: "All Schedules",
        widget_type: "allSchedules",
        category: "productivity",
        importance: 4,
        frequency: "daily",
        position: 3,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Schedule overview is important for productivity",
        settings: {
          max_tasks: 10,
          show_completed: true
        },
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      }
    ],
    total_widgets: 4,
    ai_generated: true,
    last_updated: "2025-07-29T02:36:55.560747"
  };
};

// Helper function to filter enabled widgets (not needed with new structure)
export const getEnabledWidgets = (widgets: TodayWidgetsResponse): TodayWidgetsResponse => {
  return widgets; // All widgets are enabled by default in new structure
}; 