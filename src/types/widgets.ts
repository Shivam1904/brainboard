// Base widget types and interfaces

export type WidgetType = 'todo' | 'habittracker' | 'websearch' | 'websummary' | 'calendar' | 'alarm' | 'allSchedules' | 'singleitemtracker' | 'thisHour';
export type WidgetSize = 'small' | 'medium' | 'large' | 'full';
export type WidgetFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'once';
export type WidgetImportance = 1 | 2 | 3 | 4 | 5;

// New API response structure for dashboard widgets
export interface ApiDashboardWidget {
  id: string;
  daily_widget_id: string;
  title: string;
  widget_type: string;
  category: string;
  importance: number;
  frequency: string;
  position: number;
  grid_position: any; // Can be null or layout object
  is_pinned: boolean;
  ai_reasoning: string;
  settings: any; // Can be null or settings object
  created_at: string;
  updated_at: string;
}

// Updated TodayWidgetsResponse to match new API structure
export interface TodayWidgetsResponse {
  date: string;
  widgets: ApiDashboardWidget[];
  total_widgets: number;
  ai_generated: boolean;
  last_updated: string;
}

// Base widget interface (for internal use)
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
  | ReminderWidgetData
  | SingleItemTrackerWidgetData
  | AlarmWidgetData;

// Todo Widget Types
export interface TodoTask {
  id: string;
  dashboard_widget_id: string;
  content: string;
  due_date: string | null;
  frequency: string;
  priority: number;
  category: string;
  is_done: boolean;
  is_recurring: boolean;
  last_completed_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TodoStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  tasks_by_priority: Record<string, number>;
  tasks_by_category: Record<string, number>;
}

export interface TodoWidgetData {
  tasks: TodoTask[];
  stats: TodoStats;
}

// API Response Types for Todo Widget
export interface TodoTodayResponse {
  widget_id: string;
  date: string;
  tasks: TodoTask[];
  stats: TodoStats;
}

// API Response Types for Web Search Widget
export interface WebSearchResponse {
  widget_id: string;
  date: string;
  searches: WebSearch[];
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

// Single Item Tracker Widget Types
export interface SingleItemTrackerLog {
  id: string;
  value: string;
  date: string;
  notes?: string;
  created_at: string;
}

export interface SingleItemTracker {
  id: string;
  dashboard_widget_id: string;
  item_name: string;
  item_unit?: string;
  current_value?: string;
  target_value?: string;
  value_type: string;
  created_at: string;
  updated_at: string;
}

export interface SingleItemTrackerStats {
  total_entries: number;
  current_value?: string;
  target_value?: string;
  progress_percentage?: number;
  last_updated?: string;
  streak_days: number;
}

export interface SingleItemTrackerWidgetData {
  tracker: SingleItemTracker;
  stats: SingleItemTrackerStats;
  recent_logs: SingleItemTrackerLog[];
}

// API Response Types for Single Item Tracker Widget
export interface SingleItemTrackerResponse {
  id: string;
  dashboard_widget_id: string;
  item_name: string;
  item_unit?: string;
  current_value?: string;
  target_value?: string;
  value_type: string;
  created_at: string;
  updated_at: string;
  recent_logs: SingleItemTrackerLog[];
}

export interface SingleItemTrackerWidgetDataResponse {
  widget_id: string;
  tracker: SingleItemTrackerResponse;
  stats: SingleItemTrackerStats;
  recent_logs: SingleItemTrackerLog[];
}

// Alarm Widget Types
export interface Alarm {
  id: string;
  dashboard_widget_id: string;
  title: string;
  alarm_type: string; // 'once', 'daily', 'weekly', 'monthly', 'yearly'
  alarm_times: string[]; // List of times: ["09:00", "15:00"]
  frequency_value?: number; // For daily-5, weekly-2, etc. (interval)
  specific_date?: string; // For one-time alarms
  is_active: boolean;
  is_snoozed: boolean;
  snooze_until?: string;
  last_triggered?: string;
  next_trigger_time?: string;
  created_at: string;
  updated_at: string;
}

export interface AlarmStats {
  total_alarms: number;
  active_alarms: number;
  next_alarm_time?: string;
  next_alarm_title?: string;
}

export interface AlarmWidgetData {
  alarms: Alarm[];
  stats: AlarmStats;
}

export interface AlarmWidgetDataResponse {
  widget_id: string;
  alarms: Alarm[];
  stats: AlarmStats;
}

// Dashboard response types
export interface DashboardStats {
  total_widgets: number;
  daily_count: number;
  weekly_count: number;
  monthly_count: number;
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
  return widget.type === 'alarm';
};

export const isSingleItemTrackerWidget = (widget: BaseWidget): widget is BaseWidget & { data: SingleItemTrackerWidgetData } => {
  return widget.type === 'singleitemtracker';
};

export const isAlarmWidget = (widget: BaseWidget): widget is BaseWidget & { data: AlarmWidgetData } => {
  return widget.type === 'alarm';
}; 