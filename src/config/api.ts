// API Configuration for Brainboard Backend
export const API_CONFIG = {
  baseUrl: 'http://localhost:8989', // Backend server URL

  // Dashboard Widgets endpoints (/api/v1/dashboard-widgets/)
  dashboardWidgets: {
    createWidget: '/api/v1/dashboard-widgets/newwidget', // POST - Create new widget
    getAllWidgets: '/api/v1/dashboard-widgets/allwidgets', // GET - Get all user widgets
    getWidget: '/api/v1/dashboard-widgets/{widget_id}', // GET - Get specific widget
    updateWidget: '/api/v1/dashboard-widgets/{widget_id}/update', // PUT - Update widget
    deleteWidget: '/api/v1/dashboard-widgets/{widget_id}/delete', // DELETE - Delete widget
    getWidgetsByType: '/api/v1/dashboard-widgets/alloftype/{widget_type}', // GET - Get widgets by type
    getWidgetPriorityForDate: '/api/v1/dashboard-widgets/{widget_id}/priority', // GET - Priority + reason for widget on date
  },

  // AI Service endpoints (/api/v1/ai/)
  ai: {
    health: '/api/v1/ai/health', // GET - AI service health check
  },

  // Chat service endpoints (/api/v1/chat/)
  chat: {
    health: '/api/v1/chat/health', // GET - Chat service health check
    message: '/api/v1/chat/message', // POST - Send chat message
    sessions: '/api/v1/chat/sessions', // GET - Get all sessions
    getSession: '/api/v1/chat/sessions/{session_id}', // GET - Get specific session
    clearSession: '/api/v1/chat/sessions/{session_id}', // DELETE - Clear session
    cleanup: '/api/v1/chat/cleanup', // POST - Cleanup old sessions
  },

  // AI WebSocket endpoint
  aiWebSocket: {
    aiService: '/api/v1/ai/ws', // WebSocket - Real-time AI processing updates
  },

  // Dashboard endpoints (/api/v1/dashboard/)
  dashboard: {
    getTodayWidgetList: '/api/v1/dashboard/getTodayWidgetList', // GET - Get today's widget list
    addWidgetToToday: '/api/v1/dashboard/widget/addtotoday/{widget_id}', // POST - Add widget to today
    removeWidgetFromToday: '/api/v1/dashboard/widget/removefromtoday/{daily_widget_id}', // POST - Remove widget from today
    updateActivity: '/api/v1/dashboard/daily-widgets/{daily_widget_id}/updateactivity', // PUT - Update activity data
    updateTodayActivityByWidgetId: '/api/v1/dashboard/daily-widgets/{widget_id}/updateTodayActivityByWidgetId', // PUT - Update activity data by widget_id and date
    getTodayWidget: '/api/v1/dashboard/daily-widgets/{daily_widget_id}/getTodayWidget', // GET - Get activity data
    getTodayWidgetbyWidgetId: '/api/v1/dashboard/daily-widgets/{widget_id}/getTodayWidgetbyWidgetId', // GET - Get activity data by widget_id
  },

  // Tracker endpoints (/api/v1/tracker/)
  tracker: {
    getWidgetActivityForCalendar: '/api/v1/tracker/getWidgetActivityForCalendar',
  },

  // Weather endpoints (/api/v1/weather/)
  weather: {
    getWeather: '/api/v1/weather/', // GET - Get current weather data
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

// Simple AI service helper
export const aiService = {
  // Get AI service health
  getHealth: async () => {
    return apiCall(API_CONFIG.ai.health);
  }
};

// WebSocket helper for AI service
export const aiWebSocket = {
  // Create WebSocket connection for AI service
  connect: (onMessage?: (data: unknown) => void, onError?: (error: unknown) => void, onClose?: () => void) => {
    const wsUrl = `${API_CONFIG.baseUrl.replace('http', 'ws')}${API_CONFIG.aiWebSocket.aiService}`;

    const ws = new WebSocket(wsUrl);

    if (onMessage) {
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('🔴 API: Error parsing WebSocket message:', error);
          // Send error message to frontend for better user experience
          onMessage({
            type: 'error',
            content: {
              message: 'Failed to parse server response. Please try again.'
            },
            details: 'JSON parsing error',
            timestamp: new Date().toISOString()
          });
        }
      };
    }

    if (onError) {
      ws.onerror = (error) => {
        console.error('🔴 API: WebSocket error event:', error);
        onError(error);
      };
    }

    if (onClose) {
      ws.onclose = () => {
        onClose();
      };
    }

    return ws;
  },

  // Send message through WebSocket
  sendMessage: (ws: WebSocket, message: string, userTasks: string[], todaysDate: string, conversationHistory?: unknown[]) => {
    if (ws.readyState === WebSocket.OPEN) {
      const messageData = {
        message,
        user_tasks: userTasks,
        todays_date: todaysDate,
        conversation_history: conversationHistory || []
      };
      ws.send(JSON.stringify(messageData));
    } else {
      console.error('🔴 API: WebSocket is not open. ReadyState:', ws.readyState);
      throw new Error('WebSocket is not open');
    }
  }
}; 