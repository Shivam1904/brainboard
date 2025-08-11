// API Response Types for Widgets - Single Source of Truth
// These types match exactly what the backend API returns

// ============================================================================
// TODO WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/todo/getTodayTodoList/{todo_type}
export interface TodoTodayResponse {
  todo_type: 'habit' | 'task' | 'event';
  todos: TodoActivity[];
  total_todos: number;
}

// Todo activity structure from API (matches backend ToDoItemActivity)
export interface TodoActivity {
  id: string;
  widget_id: string;
  daily_widget_id: string;
  todo_details_id: string; // Backend: tododetails_id
  title: string;
  todo_type: 'habit' | 'task' | 'event';
  description: string;
  due_date: string;
  status: 'pending' | 'in progress' | 'completed' | 'cancelled'; // Backend: 'in progress'
  progress: number;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/todo/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}
export interface TodoDetailsAndActivityResponse {
  todo_details: TodoDetails;
  activity: TodoActivityStatus;
}

// Todo details structure from API (matches backend ToDoDetails)
export interface TodoDetails {
  id: string;
  widget_id: string;
  title: string;
  todo_type: 'habit' | 'task' | 'event';
  description: string;
  due_date: string;
  created_at: string;
  updated_at: string;
}

// Todo activity status from API
export interface TodoActivityStatus {
  id: string;
  status: 'pending' | 'in progress' | 'completed' | 'cancelled';
  progress: number;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/todo/getTodoDetails/{widget_id}
export interface TodoDetailsResponse {
  id: string;
  widget_id: string;
  title: string;
  todo_type: 'habit' | 'task' | 'event';
  description: string;
  due_date: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// ALARM WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/alarm/getAlarmDetailsAndActivity/{widget_id}
export interface AlarmDetailsAndActivityResponse {
  alarm_details: AlarmDetails;
  activity: AlarmActivity;
}

// Alarm details structure from API (matches backend AlarmDetails)
export interface AlarmDetails {
  id: string;
  widget_id: string;
  title: string;
  description: string;
  alarm_times: string[];
  target_value: string;
  is_snoozable: boolean;
  created_at: string;
  updated_at: string;
}

// Alarm activity structure from API (matches backend AlarmItemActivity)
export interface AlarmActivity {
  id: string;
  started_at: string;
  snoozed_at: string;
  snooze_until: string;
  snooze_count: number;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/alarm/getAlarmDetails/{widget_id}
export interface AlarmDetailsResponse {
  id: string;
  widget_id: string;
  title: string;
  description: string;
  alarm_times: string[];
  target_value: string;
  is_snoozable: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// SINGLE ITEM TRACKER WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}
export interface TrackerDetailsAndActivityResponse {
  tracker_details: TrackerDetails;
  activity: TrackerActivity;
}

// Tracker details structure from API (matches backend SingleItemTrackerDetails)
export interface TrackerDetails {
  id: string;
  widget_id: string;
  title: string;
  value_type: string;
  value_unit: string;
  target_value: string;
  created_at: string;
  updated_at: string;
}

// Tracker activity structure from API (matches backend SingleItemTrackerItemActivity)
export interface TrackerActivity {
  id: string;
  value: string;
  time_added: string;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}
export interface TrackerDetailsResponse {
  id: string;
  widget_id: string;
  title: string;
  value_type: string;
  value_unit: string;
  target_value: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// WEBSEARCH WIDGET API TYPES
// ============================================================================

// Response from /api/v1/widgets/websearch/getSummaryAndActivity/{widget_id}
export interface WebSearchSummaryAndActivityResponse {
  websearch_details: WebSearchDetails;
  activity: WebSearchActivity;
}

// WebSearch details structure from API (matches backend WebSearchDetails)
export interface WebSearchDetails {
  id: string;
  widget_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

// WebSearch activity structure from API (matches backend WebSearchItemActivity)
export interface WebSearchActivity {
  id: string;
  status: 'pending' | 'completed' | 'failed';
  reaction: string;
  summary: string;
  source_json: any; // Backend: source_json (JSON field)
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/websearch/getWebsearchDetails/{widget_id}
export interface WebSearchDetailsResponse {
  id: string;
  widget_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

// Response from /api/v1/widgets/websearch/getaisummary/{widget_id}
export interface WebSearchAISummaryResponse {
  ai_summary_id: string;
  widget_id: string;
  query: string;
  summary: string;
  sources: Array<{
    title: string;
    url: string;
  }>;
  search_successful: boolean;
  results_count: number;
  ai_model_used: string;
  generation_type: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// COMMON API TYPES
// ============================================================================

// Status types used across widgets (matching backend exactly)
export type TodoStatus = 'pending' | 'in progress' | 'completed' | 'cancelled';
export type WebSearchStatus = 'pending' | 'completed' | 'failed';

// Widget types supported by the API
export type ApiWidgetType = 'todo-habit' | 'todo-task' | 'todo-event' | 'alarm' | 'singleitemtracker' | 'websearch' | 'notes';

// Frequency types supported by the API
export type ApiFrequency = 'daily' | 'weekly' | 'monthly';

// Priority types supported by the API
export type ApiPriority = 'HIGH' | 'LOW';

// Categories supported by the API
export type ApiCategory = 'productivity' | 'health' | 'job' | 'information' | 'entertainment' | 'utilities'; 