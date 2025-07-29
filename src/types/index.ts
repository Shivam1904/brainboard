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
  AlarmStatus,
  WebSearchStatus,
  ReactionType
} from './widgets'; 