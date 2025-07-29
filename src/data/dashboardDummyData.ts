import { TodayWidgetsResponse } from '../types';

// Dummy data that matches the new API response structure
export const getDummyTodayWidgets = (): TodayWidgetsResponse => {
  return {
    date: new Date().toISOString().split('T')[0],
    widgets: [
      {
        id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
        type: "todo",
        title: "Test Todo Widget",
        size: "medium",
        category: "testing",
        importance: 5,
        frequency: "daily",
        settings: {},
        data: {
          tasks: [
            {
              id: "230a0dd7-4532-42bd-8f30-7c0c7aac67cd",
              dashboard_widget_id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
              content: "Monthly task - Budget review",
              due_date: null,
              frequency: "daily",
              priority: 2,
              category: "work",
              is_done: false,
              is_recurring: true,
              last_completed_date: null,
              created_at: "2025-07-28T08:07:09.285093",
              updated_at: "2025-07-28T08:07:09.285093"
            },
            {
              id: "9c369ab9-2a63-4203-a6e0-b402771651ff",
              dashboard_widget_id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
              content: "Updated task content",
              due_date: null,
              frequency: "daily",
              priority: 1,
              category: "personal",
              is_done: false,
              is_recurring: false,
              last_completed_date: null,
              created_at: "2025-07-28T08:07:09.282820",
              updated_at: "2025-07-28T08:07:09.282820"
            },
            {
              id: "a5755376-9480-4658-9b8e-ea2c46e74670",
              dashboard_widget_id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
              content: "Daily task - Check emails",
              due_date: null,
              frequency: "daily",
              priority: 3,
              category: "work",
              is_done: true,
              is_recurring: true,
              last_completed_date: "2025-07-28T08:07:09.280270",
              created_at: "2025-07-28T08:07:09.280270",
              updated_at: "2025-07-28T08:07:09.280270"
            }
          ],
          stats: {
            total_tasks: 3,
            completed_tasks: 1,
            pending_tasks: 2,
            completion_rate: 33.33333333333333,
            tasks_by_priority: {
              "1": 1,
              "2": 1,
              "3": 1
            },
            tasks_by_category: {
              "work": 2,
              "personal": 1
            }
          }
        }
      },
      {
        id: "68c2ab14-23e0-41f9-8d98-50b04d01961d",
        type: "habittracker",
        title: "Daily Habits",
        size: "medium",
        category: "health",
        importance: 5,
        frequency: "daily",
        settings: {
          streak_goal: 30,
          reminder_time: "09:00"
        },
        data: {
          habits: [],
          total_habits: 0
        }
      },
      {
        id: "08db6466-e5a4-4c6c-9341-0cd2366360a4",
        type: "websearch",
        title: "FastAPI Research Widget",
        size: "medium",
        category: null,
        importance: null,
        frequency: "daily",
        settings: {},
        data: {
          message: "No search queries configured",
          searches: []
        }
      },
      {
        id: "b2df57d5-d5a5-4eb0-8c27-fe5edc67dcde",
        type: "allSchedules",
        title: "Updated Widget Title",
        size: "medium",
        category: "productivity",
        importance: 3,
        frequency: "daily",
        settings: {
          max_tasks: 10,
          show_completed: true
        },
        data: {
          tasks: [],
          stats: {
            total_tasks: 0,
            completed_tasks: 0,
            pending_tasks: 0,
            completion_rate: 0,
            tasks_by_priority: {
              "1": 0,
              "2": 0,
              "3": 0
            },
            tasks_by_category: {
              "work": 0,
              "personal": 0
            }
          }
        }
      }
    ],
    stats: {
      total_widgets: 4,
      daily_count: 4,
      weekly_count: 0,
      monthly_count: 0
    }
  };
};

// Helper function to filter enabled widgets (not needed with new structure)
export const getEnabledWidgets = (widgets: TodayWidgetsResponse): TodayWidgetsResponse => {
  return widgets; // All widgets are enabled by default in new structure
}; 