// API Response Types - Single Source of Truth
// These types match exactly what the backend API returns

// Main dashboard response from /api/v1/dashboard/getTodayWidgetList
export interface TodayWidgetsResponse {
  date: string;
  widgets: DailyWidget[];
  total_widgets: number;
  ai_generated: boolean;
  last_updated: string;
}

// Daily widget structure from API
export interface DailyWidget {
  daily_widget_id: string;
  widget_ids: string[];
  widget_type: string;
  priority: 'HIGH' | 'LOW';
  reasoning: string;
  date: string;
  created_at: string;
}

// All widgets response from /api/v1/dashboard/getAllWidgetList
export interface AllWidgetsResponse {
  widgets: DashboardWidget[];
  total_widgets: number;
}

// Dashboard widget structure from API
export interface DashboardWidget {
  id: string;
  widget_type: string;
  frequency: string;
  importance: number;
  title: string;
  category: string;
  created_at: string;
  updated_at: string;
}

// Widget types supported by the API
export type ApiWidgetType = 'todo-habit' | 'todo-task' | 'todo-event' | 'alarm' | 'singleitemtracker' | 'websearch';

// Frequency types supported by the API
export type ApiFrequency = 'daily' | 'weekly' | 'monthly';

// Priority types supported by the API
export type ApiPriority = 'HIGH' | 'LOW';

// Categories supported by the API
export type ApiCategory = 'productivity' | 'health' | 'job' | 'information' | 'entertainment' | 'utilities'; 