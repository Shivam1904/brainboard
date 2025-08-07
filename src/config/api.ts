// API Configuration for Brainboard widgets
export const API_CONFIG = {
  baseUrl: 'http://localhost:8000', // Backend server URL
  
  // Dashboard endpoints
  dashboard: {
    getTodayWidgets: '/api/v1/dashboard/getTodayWidgetList', // Get today's widget configuration
    getAllWidgets: '/api/v1/widgets/getAllWidgetList', // Get all widgets
    addNewWidget: '/api/v1/widgets/create', // Add new widget
    addWidgetToToday: '/api/v1/dashboard/widget/addtotoday', // Add widget to today
    removeWidgetFromToday: '/api/v1/dashboard/widget/removefromtoday', // Remove widget from today
    updateWidget: '/api/v1/widgets/updateDetails', // Update widget
    updateWidgetDetails: '/api/v1/widgets/updateDetails', // Update widget details
    updateDailyWidget: '/api/v1/dashboard/widget/updateActive', // Update daily widget active status
    getTodoList: '/api/v1/getTodoList', // Get todo list by type
  },
  
  // Todo widget endpoints
  todo: {
    getTodayTodoList: '/api/v1/todo/getTodayTodoList', // Get today's todo list
    updateActivity: '/api/v1/todo/updateActivity', // Update todo activity
    getTodoItemDetailsAndActivity: '/api/v1/todo/getTodoItemDetailsAndActivity', // Get todo details and activity
    getTodoDetails: '/api/v1/todo/getTodoDetails', // Get todo details
    updateDetails: '/api/v1/todo/updateDetails', // Update todo details
  },
  
  // Alarm widget endpoints
  alarm: {
    getAlarmDetailsAndActivity: '/api/v1/alarms/getAlarmDetailsAndActivity', // Get alarm details and activity
    snoozeAlarm: '/api/v1/alarms/snoozeAlarm', // Snooze alarm
    stopAlarm: '/api/v1/alarms/stopAlarm', // Stop alarm
    updateActivity: '/api/v1/alarms/updateActivity', // Update alarm activity
    getAlarmDetails: '/api/v1/alarms/getAlarmDetails', // Get alarm details
    updateDetails: '/api/v1/alarms/updateDetails', // Update alarm details
  },
  
  // Single item tracker endpoints
  singleItemTracker: {
    getTrackerDetailsAndActivity: '/api/v1/single-item-tracker/getTrackerDetailsAndActivity', // Get tracker details and activity
    updateActivity: '/api/v1/single-item-tracker/updateActivity', // Update tracker activity
    getTrackerDetails: '/api/v1/single-item-tracker/getTrackerDetails', // Get tracker details
    updateDetails: '/api/v1/single-item-tracker/updateDetails', // Update tracker details
  },
  
  // Web search endpoints
  webSearch: {
    getScheduledSearches: '/api/v1/web-search/scheduled',
    getSearchResult: '/api/v1/web-search/result',
    getSummaryAndActivity: '/api/v1/websearch/getSummaryAndActivity', // Get web search summary and activity
    updateActivity: '/api/v1/websearch/updateActivity', // Update web search activity
    getWebsearchDetails: '/api/v1/websearch/getWebsearchDetails', // Get web search details
    updateDetails: '/api/v1/websearch/updateDetails', // Update web search details
    getAISummary: '/api/v1/websearch/getaisummary', // Get AI summary
  },
  
  // Health check endpoints
  health: {
    getHealth: '/api/v1/health', // Basic health check
    getDetailedHealth: '/api/v1/health/detailed', // Detailed health check
  },
  
  // Legacy endpoints (keeping for backward compatibility)
  tasks: {
    getTodayTasks: '/api/v1/widgets/todo/tasks/today', // Get today's tasks for todo widget
    updateTask: '/api/v1/widgets/todo/tasks/update', // Update task status
    addMission: '/api/v1/widgets/todo/tasks/mission', // Add new mission
  },
  singleItemTrackerLegacy: {
    getTracker: '/api/v1/widgets/single-item-tracker/{widget_id}', // Get tracker with recent logs
    updateValue: '/api/v1/widgets/single-item-tracker/{widget_id}/update-value', // Update tracker value
    getWidgetData: '/api/v1/widgets/single-item-tracker/{widget_id}', // Get complete widget data
  },
  alarmLegacy: {
    getAlarms: '/api/v1/widgets/alarm/{widget_id}', // Get all alarms for widget
    createAlarm: '/api/v1/widgets/alarm/create', // Create new alarm
    updateAlarmStatus: '/api/v1/widgets/alarm/{widget_id}/updateStatus', // Snooze or activate alarm
    getWidgetData: '/api/v1/widgets/alarm/{widget_id}', // Get alarm widget data
  },
  reminders: {
    getReminders: '/api/v1/reminders',
    createReminder: '/api/v1/reminders/create',
  },
  calendar: {
    getMonthlyCalendar: '/api/v1/calendar/monthly',
  },
  schedules: {
    getAllSchedules: '/api/v1/schedules',
    createSchedule: '/api/v1/schedules',
    updateSchedule: '/api/v1/schedules/{id}',
    deleteSchedule: '/api/v1/schedules/{id}',
  },
  weather: {
    getWeather: '/api/v1/weather/current',
  },
  news: {
    getNews: '/api/v1/news/feed',
  },
  stats: {
    getStats: '/api/v1/stats/daily',
  },
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string, params?: Record<string, string>): string => {
  let url = `${API_CONFIG.baseUrl}${endpoint}`;
  
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }
  
  return url;
};

// Helper function for API calls with error handling
export const apiCall = async <T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> => {
  try {
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
}; 