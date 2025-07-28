// Types for dashboard widget configuration
import { BaseWidget, WidgetType, WidgetFrequency, WidgetImportance } from './widgets';

export interface ScheduledItem {
  id: string;
  title: string;
  type: WidgetType;
  frequency: WidgetFrequency;
  category?: string;
  importance?: WidgetImportance;
  alarm?: string;
  searchQuery?: string;
  config?: Record<string, any>;
}

export interface DashboardWidgetConfig {
  id: string;
  type: WidgetType;
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
  config?: Record<string, any>;
  priority?: number;
  enabled?: boolean;
  scheduledItem?: ScheduledItem;
}

// Legacy types for backward compatibility
export interface TodayWidgetsResponse {
  date: string;
  widgets: BaseWidget[];
  layout?: {
    gridCols: number;
    gridRows: number;
  };
}

// Re-export widget types for convenience
export type { BaseWidget, WidgetType, WidgetFrequency, WidgetImportance } from './widgets'; 