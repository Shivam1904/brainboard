// API Configuration for Brainboard widgets
export const API_CONFIG = {
  baseUrl: 'http://localhost:8000', // Backend server URL
  dashboard: {
    getTodayWidgets: '/api/v1/dashboard/widgets/today', // Get today's widget configuration
  },
  webSearch: {
    getScheduledSearches: '/api/v1/web-search/scheduled',
    getSearchResult: '/api/v1/web-search/result',
  },
  tasks: {
    getTodayTasks: '/api/v1/widgets/todo/tasks/today', // Get today's tasks for todo widget
    updateTask: '/api/v1/widgets/todo/tasks/update', // Update task status
    addMission: '/api/v1/widgets/todo/tasks/mission', // Add new mission
  },
  singleItemTracker: {
    getTracker: '/api/v1/widgets/single-item-tracker/{widget_id}', // Get tracker with recent logs
    updateValue: '/api/v1/widgets/single-item-tracker/{widget_id}/update-value', // Update tracker value
    getWidgetData: '/api/v1/widgets/single-item-tracker/{widget_id}', // Get complete widget data
  },
  alarm: {
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