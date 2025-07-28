// Base widget types and interfaces

export type WidgetType = 'todo' | 'habittracker' | 'websearch' | 'websummary' | 'calendar' | 'reminder' | 'allSchedules';
export type WidgetSize = 'small' | 'medium' | 'large' | 'full';
export type WidgetFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'once';
export type WidgetImportance = 1 | 2 | 3 | 4 | 5;

// Base widget interface
export interface BaseWidget {
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

// Widget data union type
export type WidgetData = 
  | TodoWidgetData
  | HabitTrackerWidgetData
  | WebSearchWidgetData
  | WebSummaryWidgetData
  | CalendarWidgetData
  | ReminderWidgetData;

// Todo Widget Types
export interface TodoTask {
  id: string;
  content: string;
  due_date: string | null;
  is_done: boolean;
  created_at: string;
}

export interface TodoStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
}

export interface TodoWidgetData {
  tasks: TodoTask[];
  stats: TodoStats;
}

// Habit Tracker Widget Types
export interface Habit {
  id: string;
  name: string;
  description?: string;
  streak: number;
  completed_today: boolean;
  created_at: string;
}

export interface HabitTrackerWidgetData {
  habits: Habit[];
  total_habits: number;
}

// Web Search Widget Types
export interface WebSearch {
  id: string;
  query: string;
  results?: WebSearchResult[];
  last_searched?: string;
}

export interface WebSearchResult {
  title: string;
  url: string;
  snippet: string;
}

export interface WebSearchWidgetData {
  message?: string;
  searches: WebSearch[];
}

// Web Summary Widget Types
export interface WebSummary {
  id: string;
  url: string;
  title: string;
  summary: string;
  created_at: string;
}

export interface WebSummaryWidgetData {
  summaries: WebSummary[];
  total_summaries: number;
}

// Calendar Widget Types
export interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  description?: string;
  is_completed: boolean;
}

export interface CalendarWidgetData {
  events: CalendarEvent[];
  current_date: string;
  total_events: number;
}

// Reminder Widget Types
export interface Reminder {
  id: string;
  title: string;
  message: string;
  due_date: string;
  is_completed: boolean;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface ReminderWidgetData {
  reminders: Reminder[];
  total_reminders: number;
  overdue_count: number;
}

// Dashboard response types
export interface DashboardStats {
  total_widgets: number;
  daily_count: number;
  weekly_count: number;
  monthly_count: number;
}

export interface TodayWidgetsResponse {
  date: string;
  widgets: BaseWidget[];
  stats: DashboardStats;
}

// Widget settings types
export interface TodoWidgetSettings {
  max_tasks?: number;
  show_completed?: boolean;
  sort_by?: 'created_at' | 'due_date' | 'priority';
}

export interface HabitTrackerWidgetSettings {
  streak_goal?: number;
  reminder_time?: string;
  show_streaks?: boolean;
}

export interface WebSearchWidgetSettings {
  max_results?: number;
  search_engines?: string[];
  auto_search?: boolean;
}

export interface WebSummaryWidgetSettings {
  max_summaries?: number;
  summary_length?: number;
  include_metadata?: boolean;
}

export interface CalendarWidgetSettings {
  view_mode?: 'day' | 'week' | 'month';
  show_completed?: boolean;
  max_events?: number;
}

export interface ReminderWidgetSettings {
  max_reminders?: number;
  show_overdue?: boolean;
  sort_by?: 'due_date' | 'priority' | 'created_at';
}

// Type guards for widget data
export const isTodoWidget = (widget: BaseWidget): widget is BaseWidget & { data: TodoWidgetData } => {
  return widget.type === 'todo';
};

export const isHabitTrackerWidget = (widget: BaseWidget): widget is BaseWidget & { data: HabitTrackerWidgetData } => {
  return widget.type === 'habittracker';
};

export const isWebSearchWidget = (widget: BaseWidget): widget is BaseWidget & { data: WebSearchWidgetData } => {
  return widget.type === 'websearch';
};

export const isWebSummaryWidget = (widget: BaseWidget): widget is BaseWidget & { data: WebSummaryWidgetData } => {
  return widget.type === 'websummary';
};

export const isCalendarWidget = (widget: BaseWidget): widget is BaseWidget & { data: CalendarWidgetData } => {
  return widget.type === 'calendar';
};

export const isReminderWidget = (widget: BaseWidget): widget is BaseWidget & { data: ReminderWidgetData } => {
  return widget.type === 'reminder';
}; 