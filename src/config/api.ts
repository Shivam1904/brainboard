// API Configuration for Brainboard widgets
export const API_CONFIG = {
  baseUrl: 'http://localhost:8000', // Backend server URL
  dashboard: {
    getTodayWidgets: '/api/dashboard/today', // Get today's widget configuration
  },
  webSearch: {
    getScheduledSearches: '/api/web-search/scheduled',
    getSearchResult: '/api/web-search/result',
  },
  tasks: {
    getTodayTasks: '/api/tasks/today', // Get today's tasks
    updateTask: '/api/tasks/update', // Update task status
    addMission: '/api/tasks/mission', // Add new mission
  },
  reminders: {
    getReminders: '/api/reminders',
    createReminder: '/api/reminders/create',
  },
  calendar: {
    getMonthlyCalendar: '/api/calendar/monthly',
  },
  schedules: {
    getAllSchedules: '/api/schedules',
    createSchedule: '/api/schedules',
    updateSchedule: '/api/schedules/{id}',
    deleteSchedule: '/api/schedules/{id}',
  },
  weather: {
    getWeather: '/api/weather/current',
  },
  news: {
    getNews: '/api/news/feed',
  },
  stats: {
    getStats: '/api/stats/daily',
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