// Export all types from the types directory
export * from './dashboard';
export * from './widgets';
export * from './frequency';

// Main types that should be used throughout the application
export type { 
  BaseWidget, 
  WidgetType, 
  WidgetSize, 
  WidgetFrequency, 
  WidgetImportance,
  TodayWidgetsResponse,
  DashboardStats
} from './widgets';

export type {
  TodoWidgetData,
  HabitTrackerWidgetData,
  WebSearchWidgetData,
  WebSummaryWidgetData,
  CalendarWidgetData,
  ReminderWidgetData
} from './widgets';

export type {
  TodoTask,
  TodoStats,
  Habit,
  WebSearch,
  WebSearchResult,
  WebSummary,
  CalendarEvent,
  Reminder
} from './widgets'; 