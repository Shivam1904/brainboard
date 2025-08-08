// API Configuration for Brainboard Backend
export const API_CONFIG = {
  baseUrl: 'http://localhost:8000', // Backend server URL
  
  // Dashboard Widgets endpoints (/api/v1/dashboard-widgets/)
  dashboardWidgets: {
    createWidget: '/api/v1/dashboard-widgets/newwidget', // POST - Create new widget
    getAllWidgets: '/api/v1/dashboard-widgets/allwidgets', // GET - Get all user widgets
    getWidget: '/api/v1/dashboard-widgets/{widget_id}', // GET - Get specific widget
    updateWidget: '/api/v1/dashboard-widgets/{widget_id}/update', // PUT - Update widget
    deleteWidget: '/api/v1/dashboard-widgets/{widget_id}/delete', // DELETE - Delete widget
    getWidgetsByType: '/api/v1/dashboard-widgets/alloftype/{widget_type}', // GET - Get widgets by type
  },
  
  // Chat endpoints (/api/v1/chat/)
  chat: {
    health: '/api/v1/chat/health', // GET - Chat health check
    message: '/api/v1/chat/message', // POST - Send chat message
    sessions: '/api/v1/chat/sessions', // GET - List all sessions
    getSession: '/api/v1/chat/sessions/{session_id}', // GET - Get specific session
    clearSession: '/api/v1/chat/sessions/{session_id}', // DELETE - Clear session
    cleanup: '/api/v1/chat/cleanup', // POST - Cleanup sessions
  },
  
  // Dashboard endpoints (/api/v1/dashboard/)
  dashboard: {
    getTodayWidgetList: '/api/v1/dashboard/getTodayWidgetList', // GET - Get today's widget list
    addWidgetToToday: '/api/v1/dashboard/widget/addtotoday/{widget_id}', // POST - Add widget to today
    removeWidgetFromToday: '/api/v1/dashboard/widget/removefromtoday/{daily_widget_id}', // POST - Remove widget from today
    updateActivity: '/api/v1/dashboard/daily-widgets/{daily_widget_id}/updateactivity', // PUT - Update activity data
    getTodayWidget: '/api/v1/dashboard/daily-widgets/{daily_widget_id}/getTodayWidget', // GET - Get activity data
    getTodayWidgetbyWidgetId: '/api/v1/dashboard/daily-widgets/{widget_id}/getTodayWidgetbyWidgetId', // GET - Get activity data by widget_id
  },
  
  // Tracker endpoints (/api/v1/tracker/)
  tracker: {
    getWidgetActivityForCalendar: '/api/v1/tracker/getWidgetActivityForCalendar',
  },
  
  // Health check endpoints
  health: {
    getHealth: '/health', // GET - Basic health check
    getRoot: '/', // GET - API information
  }
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

// Helper function to replace URL parameters
export const buildApiUrlWithParams = (endpoint: string, pathParams: Record<string, string>, queryParams?: Record<string, string>): string => {
  let url = `${API_CONFIG.baseUrl}${endpoint}`;
  
  // Replace path parameters
  Object.entries(pathParams).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, value);
  });
  
  // Add query parameters
  if (queryParams) {
    const searchParams = new URLSearchParams(queryParams);
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