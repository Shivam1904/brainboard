// API Service - Clean implementation using new consolidated backend API
// This service matches the new backend API endpoints exactly

import { API_CONFIG, buildApiUrl, buildApiUrlWithParams } from '../config/api';

// Basic types for the new API structure
export interface DashboardWidget {
  id: string;
  user_id: string;
  widget_type: string;
  title: string;
  frequency: string;
  importance: number;
  category: string;
  description?: string;
  is_permanent: boolean;
  widget_config: Record<string, any>;
  created_at: string;
  updated_at: string;
  delete_flag: boolean;
}

import { Layout } from 'react-grid-layout';
// Daily widget structure from API - Updated to match new response
export interface DailyWidget {
  id: string;
  daily_widget_id: string;
  widget_id: string;
  widget_type: string;
  title: string;
  frequency: string;
  importance: number;
  category: string;
  description?: string;
  is_permanent?: boolean;
  priority?: string;
  reasoning?: string;
  date?: string;
  is_active?: boolean;
  isVisible?: boolean;
  layout: Layout;
  widget_config?: Record<string, any>;
  activity_data?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  delete_flag?: boolean;
}

export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================================================
  // DASHBOARD WIDGETS ENDPOINTS (/api/v1/dashboard-widgets/)
  // ============================================================================

  // POST /api/v1/dashboard-widgets/newwidget
  async createWidget(data: {
    widget_type: string;
    title: string;
    frequency: string;
    importance: number;
    category: string;
    description?: string;
    is_permanent?: boolean;
    widget_config?: Record<string, any>;
  }): Promise<DashboardWidget> {
    const url = buildApiUrl(API_CONFIG.dashboardWidgets.createWidget);
    return this.request<DashboardWidget>(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/dashboard-widgets/allwidgets
  async getAllWidgets(): Promise<DashboardWidget[]> {
    const url = buildApiUrl(API_CONFIG.dashboardWidgets.getAllWidgets);
    return this.request<DashboardWidget[]>(url);
  }

  // GET /api/v1/dashboard-widgets/{widget_id}
  async getWidget(widgetId: string): Promise<DashboardWidget> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboardWidgets.getWidget, { widget_id: widgetId });
    return this.request<DashboardWidget>(url);
  }

  // PUT /api/v1/dashboard-widgets/{widget_id}/update
  async updateWidget(widgetId: string, data: Partial<DashboardWidget>): Promise<DashboardWidget> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboardWidgets.updateWidget, { widget_id: widgetId });
    return this.request<DashboardWidget>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE /api/v1/dashboard-widgets/{widget_id}/delete
  async deleteWidget(widgetId: string): Promise<{ message: string }> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboardWidgets.deleteWidget, { widget_id: widgetId });
    return this.request<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // GET /api/v1/dashboard-widgets/alloftype/{widget_type}
  async getWidgetsByType(widgetType: string): Promise<DashboardWidget[]> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboardWidgets.getWidgetsByType, { widget_type: widgetType });
    return this.request<DashboardWidget[]>(url);
  }

  // ============================================================================
  // CHAT ENDPOINTS (/api/v1/chat/)
  // ============================================================================

  // GET /api/v1/chat/health
  async getChatHealth(): Promise<{ status: string; message: string }> {
    const url = buildApiUrl(API_CONFIG.chat.health);
    return this.request<{ status: string; message: string }>(url);
  }

  // POST /api/v1/chat/message
  async sendChatMessage(data: ChatMessage): Promise<ChatResponse> {
    const url = buildApiUrl(API_CONFIG.chat.message);
    return this.request<ChatResponse>(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/chat/sessions
  async getChatSessions(): Promise<ChatSession[]> {
    const url = buildApiUrl(API_CONFIG.chat.sessions);
    return this.request<ChatSession[]>(url);
  }

  // GET /api/v1/chat/sessions/{session_id}
  async getChatSession(sessionId: string): Promise<ChatSession> {
    const url = buildApiUrlWithParams(API_CONFIG.chat.getSession, { session_id: sessionId });
    return this.request<ChatSession>(url);
  }

  // DELETE /api/v1/chat/sessions/{session_id}
  async clearChatSession(sessionId: string): Promise<{ message: string }> {
    const url = buildApiUrlWithParams(API_CONFIG.chat.clearSession, { session_id: sessionId });
    return this.request<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // POST /api/v1/chat/cleanup
  async cleanupChatSessions(): Promise<{ message: string }> {
    const url = buildApiUrl(API_CONFIG.chat.cleanup);
    return this.request<{ message: string }>(url, {
      method: 'POST',
    });
  }

  // ============================================================================
  // DASHBOARD ENDPOINTS (/api/v1/dashboard/)
  // ============================================================================

  // GET /api/v1/dashboard/getTodayWidgetList
  async getTodayWidgetList(targetDate: string): Promise<DailyWidget[]> {
    const params = targetDate ? { target_date: targetDate } : undefined;
    const url = buildApiUrl(API_CONFIG.dashboard.getTodayWidgetList, params);
    return this.request<DailyWidget[]>(url);
  }

  // POST /api/v1/dashboard/widget/addtotoday/{widget_id}
  async addWidgetToToday(widgetId: string, targetDate: string): Promise<{
    success: boolean;
    message: string;
    daily_widget_id: string;
    widget_id: string;
  }> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboard.addWidgetToToday, { widget_id: widgetId }, { target_date: targetDate });
    return this.request(url, {
      method: 'POST',
    });
  }

  // POST /api/v1/dashboard/widget/removefromtoday/{daily_widget_id}
  async removeWidgetFromToday(dailyWidgetId: string, targetDate: string): Promise<{
    success: boolean;
    message: string;
    daily_widget_id: string;
    is_active: boolean;
  }> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboard.removeWidgetFromToday, { daily_widget_id: dailyWidgetId }, { target_date: targetDate });
    return this.request(url, {
      method: 'POST',
    });
  }

  // PUT /api/v1/dashboard/daily-widgets/{daily_widget_id}/updateactivity
  async updateActivity(dailyWidgetId: string, activityData: Record<string, any>): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboard.updateActivity, { daily_widget_id: dailyWidgetId });
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(activityData),
    });
  }

  // GET /api/v1/dashboard/daily-widgets/{daily_widget_id}/getactivity
  async getTodayWidget(dailyWidgetId: string): Promise<DailyWidget> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboard.getTodayWidget, { daily_widget_id: dailyWidgetId });
    return this.request<DailyWidget>(url);
  }

  // GET /api/v1/dashboard/daily-widgets/{widget_id}/getTodayWidgetbyWidgetId
  async getTodayWidgetByWidgetId(widgetId: string, targetDate: string): Promise<DailyWidget | null> {
    const url = buildApiUrlWithParams(API_CONFIG.dashboard.getTodayWidgetbyWidgetId, { widget_id: widgetId }, { target_date: targetDate });
    return this.request<DailyWidget | null>(url);
  }

  // ============================================================================
  // WIDGET-SPECIFIC API METHODS
  // ============================================================================

  // Get alarm details and activity
  async getAlarmDetailsAndActivity(widgetId: string): Promise<any> {
    // This would typically call a specific alarm endpoint
    // For now, we'll use the general getTodayWidget method
    return this.getTodayWidget(widgetId);
  }

  // Snooze alarm
  async snoozeAlarm(activityId: string, minutes: number): Promise<any> {
    // This would typically call a specific alarm snooze endpoint
    // For now, we'll use the general updateActivity method
    return this.updateActivity(activityId, {
      snooze_until: new Date(Date.now() + minutes * 60 * 1000).toISOString()
    });
  }

  // Stop alarm
  async stopAlarm(activityId: string): Promise<any> {
    // This would typically call a specific alarm stop endpoint
    // For now, we'll use the general updateActivity method
    return this.updateActivity(activityId, {
      started_at: new Date().toISOString()
    });
  }

  // ============================================================================
  // HEALTH CHECK ENDPOINTS
  // ============================================================================

  // GET /health
  async getHealth(): Promise<{ status: string; message: string }> {
    const url = buildApiUrl(API_CONFIG.health.getHealth);
    return this.request<{ status: string; message: string }>(url);
  }

  // ============================================================================
  // TRACKER ENDPOINTS (/api/v1/tracker/)
  // ============================================================================

  async getWidgetActivityForCalendar(params: {
    calendar_id: string;
    start_date: string; // YYYY-MM-DD
    end_date: string;   // YYYY-MM-DD
    calendar_type: string;
  }): Promise<DailyWidget[]> {
    const url = buildApiUrl(API_CONFIG.tracker.getWidgetActivityForCalendar, {
      calendar_id: params.calendar_id,
      start_date: params.start_date,
      end_date: params.end_date,
      calendar_type: params.calendar_type,
    });
    return this.request<DailyWidget[]>(url);
  }

  // GET /
  async getApiInfo(): Promise<{ message: string; version: string; docs: string; health: string }> {
    const url = buildApiUrl(API_CONFIG.health.getRoot);
    return this.request<{ message: string; version: string; docs: string; health: string }>(url);
  }

  // ============================================================================
  // WEATHER ENDPOINTS (/api/v1/weather/)
  // ============================================================================

  async getWeather(lat: number, lon: number, units: string = 'metric'): Promise<{
    temperature: number;
    humidity: number;
    pressure: number;
    description: string;
    icon_code: string;
    wind_speed: number;
    wind_direction: number;
    visibility: number;
    data_timestamp: string;
    location: string;
    units: string;
  }> {
    const url = buildApiUrl(API_CONFIG.weather.getWeather, { lat: lat.toString(), lon: lon.toString(), units });
    return this.request(url);
  }
}

// Export singleton instance
export const apiService = new ApiService(); 