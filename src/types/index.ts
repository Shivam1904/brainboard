// Export all API-compatible types
// These types match the actual backend API responses exactly

// Dashboard types
export type {
  TodayWidgetsResponse,
  DailyWidget,
  AllWidgetsResponse,
  DashboardWidget,
  ApiWidgetType,
  ApiFrequency,
  ApiPriority,
  ApiCategory
} from './dashboard';

// Widget-specific API types
export type {
  // Todo widget types
  TodoTodayResponse,
  TodoActivity,
  TodoDetailsAndActivityResponse,
  TodoDetails,
  TodoActivityStatus,
  TodoDetailsResponse,
  
  // Alarm widget types
  AlarmDetailsAndActivityResponse,
  AlarmDetails,
  AlarmActivity,
  AlarmDetailsResponse,
  
  // Single item tracker widget types
  TrackerDetailsAndActivityResponse,
  TrackerDetails,
  TrackerActivity,
  TrackerDetailsResponse,
  
  // WebSearch widget types
  WebSearchSummaryAndActivityResponse,
  WebSearchDetails,
  WebSearchActivity,
  WebSearchDetailsResponse,
  WebSearchAISummaryResponse,
  
  // Common status types
  TodoStatus,
  WebSearchStatus
} from './widgets';

// UI-specific types
import { Layout } from 'react-grid-layout';

// Updated UIWidget interface to be compatible with new API response
export interface UIWidget {
  daily_widget_id: string; // Maps to DailyWidget.id for UI compatibility
  widget_ids: string[]; // Empty array for new API structure
  widget_type: string;
  priority: string; // Derived from importance or default
  reasoning: string; // Default value for new API structure
  date: string; // Current date for new API structure
  created_at: string;
  layout: Layout;
} 