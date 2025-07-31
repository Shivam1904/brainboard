// API Response Types - Single Source of Truth
// These types match exactly what the backend API returns

import { Layout } from "react-grid-layout";

// Main dashboard response from /api/v1/dashboard/getTodayWidgetList
// Updated to match new API response structure - direct array
export type TodayWidgetsResponse = DailyWidget[];

// Daily widget structure from API - Updated to match new response
export interface DailyWidget {
  id: string;
  daily_widget_id: string;
  widget_ids: string[];
  widget_type: string;
  priority: string;
  reasoning: string;
  date: string;
  layout: Layout;
  title: string;
  category: string;
  frequency: string;
  importance: number;
  is_permanent: boolean;
  created_at: string;
  updated_at: string;
}

// All widgets response from /api/v1/dashboard/getAllWidgetList
// Updated to match new API response structure - direct array
export type AllWidgetsResponse = DailyWidget[];

// Dashboard widget structure from API (keeping for backward compatibility)
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