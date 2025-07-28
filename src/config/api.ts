// API Configuration for Brainboard widgets
export const API_CONFIG = {
  baseUrl: 'http://localhost:8000', // Backend server URL
  
  // Dashboard endpoints
  dashboard: {
    getTodayWidgets: '/api/dashboard/today', // Get today's widget configuration
  },
  
  // Everyday Web Search endpoints
  everydayWebSearch: {
    getScheduledSearches: '/api/web-search/scheduled', // Get scheduled searches for today
    getSearchResult: '/api/web-search/result', // Get search result for specific search
  },
  
  // Task List endpoints
  taskList: {
    getTodayTasks: '/api/tasks/today',
    addMission: '/api/tasks/mission',
    updateTask: '/api/tasks/update',
    getMonthlySchedule: '/api/tasks/schedule',
  },
  
  // Calendar endpoints
  calendar: {
    getMonthlyData: '/api/calendar/monthly',
  },
  
  // Habit Tracker endpoints
  habitTracker: {
    getHabits: '/api/habits',
    updateHabit: '/api/habits/update',
  },
  
  // Reminders endpoints
  reminders: {
    getReminders: '/api/reminders',
    createReminder: '/api/reminders/create',
    updateReminder: '/api/reminders/update',
  },
  
  // Single Item Tracker endpoints
  singleItemTracker: {
    getItems: '/api/tracker/items',
    updateItem: '/api/tracker/update',
  },
  
  // Notifications endpoints
  notifications: {
    getNotifications: '/api/notifications',
    dismissNotification: '/api/notifications/dismiss',
  },
  
  // AI Task History endpoints
  aiTaskHistory: {
    getTodayActions: '/api/ai/actions/today',
  },
  
  // Web Search Chart endpoints
  webSearchChart: {
    getChartData: '/api/web-search/chart',
    getTrendAnalysis: '/api/web-search/trends',
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