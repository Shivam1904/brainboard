// Types for dashboard widget configuration

export interface ScheduledItem {
  id: string;
  title: string;
  type: string; // 'userTask', 'userHabit', 'itemTracker', 'webSearch', 'aiWebChart', 'weatherWig', 'calendar', 'alarm', 'statsWidget', 'newsWidget'
  frequency: string; // 'daily', 'weekly-2', 'onGym', 'alternate', 'hourly', 'Jun 20', 'daily-5', etc.
  category?: string; // 'health', 'self-imp', 'finance', 'awareness', etc.
  importance?: 'High' | 'Medium' | 'Low';
  alarm?: string; // '[7am]', '[every 2 hr]', '[list of times]', etc.
  searchQuery?: string; // For aiWebSearch type
  config?: Record<string, any>; // Additional configuration
}

export interface DashboardWidgetConfig {
  id: string;
  type: string; // widget type (e.g., 'everydayWebSearch', 'everydayTaskList')
  layout: {
    x: number;
    y: number;
    w: number;
    h: number;
    minW?: number;
    minH?: number;
    maxW?: number;
    maxH?: number;
  };
  config?: Record<string, any>; // Additional widget-specific configuration
  priority?: number; // Widget priority for positioning
  enabled?: boolean; // Whether the widget should be shown
  scheduledItem?: ScheduledItem; // Reference to the original scheduled item
}

export interface TodayWidgetsResponse {
  date: string; // ISO date string
  widgets: DashboardWidgetConfig[];
  layout?: {
    gridCols: number;
    gridRows: number;
  };
}

// Widget-specific data types
export interface WebSearchWidgetData {
  scheduledSearches: Array<{
    id: string;
    searchTerm: string;
    scheduledTime: string;
  }>;
}

export interface TaskListWidgetData {
  todayTasks: Array<{
    id: string;
    title: string;
    completed: boolean;
    priority: 'high' | 'medium' | 'low';
    category: string;
  }>;
}

export interface CalendarWidgetData {
  monthData: Array<{
    date: string;
    completedTasks: number;
    totalTasks: number;
    top3Completed: boolean;
    milestones: string[];
  }>;
}

// Union type for all widget data
export type WidgetData = 
  | { type: 'everydayWebSearch'; data: WebSearchWidgetData }
  | { type: 'everydayTaskList'; data: TaskListWidgetData }
  | { type: 'monthlyCalendar'; data: CalendarWidgetData }
  | { type: string; data: any }; 