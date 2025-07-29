// API Response Types for Widgets - Single Source of Truth
// These types match exactly what the backend API returns

// ============================================================================
// TODO WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/todo/getTodayTodoList/{todo_type}
export interface TodoTodayResponse {
  todo_type: 'habit' | 'task';
  todos: TodoActivity[];
  total_todos: number;
}

// Todo activity structure from API
export interface TodoActivity {
  activity_id: string;
  widget_id: string;
  daily_widget_id: string;
  todo_details_id: string;
  title: string;
  todo_type: 'habit' | 'task';
  description: string;
  due_date: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  progress: number;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/todo/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}
export interface TodoDetailsAndActivityResponse {
  todo_details: TodoDetails;
  activity: TodoActivityStatus;
}

// Todo details structure from API
export interface TodoDetails {
  id: string;
  title: string;
  todo_type: 'habit' | 'task';
  description: string;
  due_date: string;
}

// Todo activity status from API
export interface TodoActivityStatus {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  progress: number;
  created_at: string;
}

// Response from /api/v1/widgets/todo/getTodoDetails/{widget_id}
export interface TodoDetailsResponse {
  id: string;
  title: string;
  todo_type: 'habit' | 'task';
  description: string;
  due_date: string;
  created_at: string;
}

// ============================================================================
// ALARM WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/alarm/getAlarmDetailsAndActivity/{widget_id}
export interface AlarmDetailsAndActivityResponse {
  alarm_details: AlarmDetails;
  activity: AlarmActivity;
}

// Alarm details structure from API
export interface AlarmDetails {
  id: string;
  title: string;
  alarm_times: string[];
  enabled: boolean;
}

// Alarm activity structure from API
export interface AlarmActivity {
  id: string;
  status: 'pending' | 'triggered' | 'started' | 'snoozed' | 'dismissed';
  snooze_count: number;
  last_triggered: string;
}

// Response from /api/v1/widgets/alarm/getAlarmDetails/{widget_id}
export interface AlarmDetailsResponse {
  id: string;
  title: string;
  alarm_times: string[];
  enabled: boolean;
  created_at: string;
}

// ============================================================================
// SINGLE ITEM TRACKER WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}
export interface TrackerDetailsAndActivityResponse {
  tracker_details: TrackerDetails;
  activity: TrackerActivity;
}

// Tracker details structure from API
export interface TrackerDetails {
  id: string;
  title: string;
  value_type: string;
  unit: string;
  target_value: number;
}

// Tracker activity structure from API
export interface TrackerActivity {
  id: string;
  current_value: number;
  last_updated: string;
}

// Response from /api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}
export interface TrackerDetailsResponse {
  id: string;
  title: string;
  value_type: string;
  unit: string;
  target_value: number;
  created_at: string;
}

// ============================================================================
// WEBSEARCH WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/websearch/getSummaryAndActivity/{widget_id}
export interface WebSearchSummaryAndActivityResponse {
  websearch_details: WebSearchDetails;
  activity: WebSearchActivity;
}

// WebSearch details structure from API
export interface WebSearchDetails {
  id: string;
  title: string;
  search_query: string;
}

// WebSearch activity structure from API
export interface WebSearchActivity {
  id: string;
  status: 'pending' | 'searching' | 'summarizing' | 'completed' | 'failed';
  reaction: 'positive' | 'negative' | 'neutral';
  summary: string;
  sources: string[];
}

// Response from /api/v1/widgets/websearch/getWebsearchDetails/{widget_id}
export interface WebSearchDetailsResponse {
  id: string;
  title: string;
  search_query: string;
  created_at: string;
}

// Response from /api/v1/widgets/websearch/getaisummary/{widget_id}
export interface WebSearchAISummaryResponse {
  summary: string;
  sources: string[];
  generated_at: string;
  confidence_score: number;
}

// ============================================================================
// COMMON API TYPES
// ============================================================================

// Status types used across widgets
export type TodoStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type AlarmStatus = 'pending' | 'triggered' | 'started' | 'snoozed' | 'dismissed';
export type WebSearchStatus = 'pending' | 'searching' | 'summarizing' | 'completed' | 'failed';
export type ReactionType = 'positive' | 'negative' | 'neutral';

// Widget types supported by the API
export type ApiWidgetType = 'todo' | 'alarm' | 'singleitemtracker' | 'websearch';

// Frequency types supported by the API
export type ApiFrequency = 'daily' | 'weekly' | 'monthly';

// Priority types supported by the API
export type ApiPriority = 'HIGH' | 'LOW';

// Categories supported by the API
export type ApiCategory = 'productivity' | 'health' | 'job' | 'information' | 'entertainment' | 'utilities'; 