// API Service - Direct API calls without conversions
// This service matches the actual backend API endpoints exactly

import { 
  TodoTodayResponse,
  TodoDetailsAndActivityResponse,
  TodoDetailsResponse,
  AlarmDetailsAndActivityResponse,
  AlarmDetailsResponse,
  TrackerDetailsAndActivityResponse,
  TrackerDetailsResponse,
  WebSearchSummaryAndActivityResponse,
  WebSearchDetailsResponse,
  WebSearchAISummaryResponse,
  ApiWidgetType,
  ApiFrequency,
  ApiCategory,
  TodoStatus,
  WebSearchStatus,
  DailyWidget
} from '../types';
import { API_CONFIG, buildApiUrl } from '../config/api';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // Check if endpoint is already a full URL (starts with http)
    const url = endpoint.startsWith('http') ? endpoint : buildApiUrl(endpoint);
    const response = await fetch(url, {
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
  // DASHBOARD ENDPOINTS
  // ============================================================================

  // GET /api/v1/dashboard/getTodayWidgetList
  async getTodayWidgetList(targetDate?: string): Promise<DailyWidget[]> {
    const params = targetDate ? { target_date: targetDate } : undefined;
    const url = buildApiUrl(API_CONFIG.dashboard.getTodayWidgets, params);
    return this.request<DailyWidget[]>(url);
  }

  // GET /api/v1/dashboard/getAllWidgetList
  async getAllWidgetList(): Promise<DailyWidget[]> {
    return this.request<DailyWidget[]>(API_CONFIG.dashboard.getAllWidgets);
  }

  // POST /api/v1/dashboard/widget/addnew
  async addNewWidget(data: {
    widget_type: ApiWidgetType;
    frequency: ApiFrequency;
    importance: number;
    title: string;
    category: ApiCategory;
    // Widget-specific fields
    todo_type?: string;
    due_date?: string;
    alarm_time?: string;
    value_data_type?: string;
    value_data_unit?: string;
    target_value?: string;
  }): Promise<{
    message: string;
    widget_id: string;
    widget_type: string;
    title: string;
  }> {
    return this.request(API_CONFIG.dashboard.addNewWidget, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // POST /api/v1/dashboard/widget/addtotoday/{widget_id}
  async addWidgetToToday(widgetId: string): Promise<{
    message: string;
    daily_widget_id: string;
    widget_id: string;
    widget_type: string;
    title: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.dashboard.addWidgetToToday}/${widgetId}`);
    return this.request(url, {
      method: 'POST',
    });
  }

  // POST /api/v1/dashboard/widget/updateWidgetDetails/{widget_id}
  async updateWidget(widgetId: string, data: {
    widget_type: ApiWidgetType;
    frequency: ApiFrequency;
    importance: number;
    title: string;
    category: ApiCategory;
    // Widget-specific fields
    todo_type?: string;
    due_date?: string;
    alarm_time?: string;
    value_data_type?: string;
    value_data_unit?: string;
    target_value?: string;
  }): Promise<{
    message: string;
    widget_id: string;
    widget_type: string;
    title: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.dashboard.updateWidget}/${widgetId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // POST /api/v1/dashboard/widget/updateDetails/{widget_id}
  async updateWidgetDetails(widgetId: string, data: {
    title?: string;
    frequency?: ApiFrequency;
    importance?: number;
    category?: ApiCategory;
  }): Promise<{
    message: string;
    widget_id: string;
    widget_type: string;
    title: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.dashboard.updateWidgetDetails}/${widgetId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // POST /api/v1/dashboard/widgets/updateDailyWidget/{daily_widget_id}
  async updateDailyWidgetActive(dailyWidgetId: string, isActive: boolean): Promise<{
    message: string;
    daily_widget_id: string;
    is_active: boolean;
  }> {
    const url = buildApiUrl(`${API_CONFIG.dashboard.updateDailyWidget}/${dailyWidgetId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify({ is_active: isActive }),
    });
  }

  // GET /api/v1/dashboard/getTodoList/{todo_type}
  async getTodoList(todoType: 'habit' | 'task' | 'event'): Promise<{
    todo_type: 'habit' | 'task' | 'event';
    todos: Array<{
      id: string;
      title: string;
      todo_type: 'habit' | 'task' | 'event';
      description: string;
      due_date: string;
      created_at: string;
    }>;
    total_todos: number;
  }> {
    const url = buildApiUrl(`${API_CONFIG.dashboard.getTodoList}/${todoType}`);
    return this.request(url);
  }

  // ============================================================================
  // TODO WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/todo/getTodayTodoList/{todo_type}
  async getTodayTodoList(todoType: 'habit' | 'task' | 'event'): Promise<TodoTodayResponse> {
    const url = buildApiUrl(`${API_CONFIG.todo.getTodayTodoList}/${todoType}`);
    return this.request<TodoTodayResponse>(url);
  }

  // POST /api/v1/widgets/todo/updateActivity/{activity_id}
  async updateTodoActivity(activityId: string, data: {
    status: TodoStatus;
    progress: number;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    status: TodoStatus;
    progress: number;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.todo.updateActivity}/${activityId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/todo/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}
  async getTodoItemDetailsAndActivity(dailyWidgetId: string, widgetId: string): Promise<TodoDetailsAndActivityResponse> {
    const url = buildApiUrl(`${API_CONFIG.todo.getTodoItemDetailsAndActivity}/${dailyWidgetId}/${widgetId}`);
    return this.request<TodoDetailsAndActivityResponse>(url);
  }

  // GET /api/v1/widgets/todo/getTodoDetails/{widget_id}
  async getTodoDetails(widgetId: string): Promise<TodoDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.todo.getTodoDetails}/${widgetId}`);
    return this.request<TodoDetailsResponse>(url);
  }

  // POST /api/v1/widgets/todo/updateDetails/{todo_details_id}
  async updateTodoDetails(todoDetailsId: string, data: {
    title: string;
    description: string;
    due_date: string;
    todo_type: 'habit' | 'task' | 'event';
  }): Promise<TodoDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.todo.updateDetails}/${todoDetailsId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // ALARM WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/alarm/getAlarmDetailsAndActivity/{widget_id}
  async getAlarmDetailsAndActivity(widgetId: string): Promise<AlarmDetailsAndActivityResponse> {
    const url = buildApiUrl(`${API_CONFIG.alarm.getAlarmDetailsAndActivity}/${widgetId}`);
    return this.request<AlarmDetailsAndActivityResponse>(url);
  }

  // POST /api/v1/widgets/alarm/snoozeAlarm/{activity_id}
  async snoozeAlarm(activityId: string, snoozeMinutes: number = 2): Promise<{
    activity_id: string;
    snoozed_at: string;
    snooze_until: string;
    snooze_count: number;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.alarm.snoozeAlarm}/${activityId}`, { snooze_minutes: snoozeMinutes.toString() });
    return this.request(url, {
      method: 'POST',
    });
  }

  // POST /api/v1/widgets/alarm/stopAlarm/{activity_id}
  async stopAlarm(activityId: string): Promise<{
    activity_id: string;
    started_at: string;
    snooze_until: null;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.alarm.stopAlarm}/${activityId}`);
    return this.request(url, {
      method: 'POST',
    });
  }

  // POST /api/v1/widgets/alarm/updateActivity/{activity_id}
  async updateAlarmActivity(activityId: string, data: {
    started_at?: string;
    snoozed_at?: string;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    started_at?: string;
    snoozed_at?: string;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.alarm.updateActivity}/${activityId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/alarm/getAlarmDetails/{widget_id}
  async getAlarmDetails(widgetId: string): Promise<AlarmDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.alarm.getAlarmDetails}/${widgetId}`);
    return this.request<AlarmDetailsResponse>(url);
  }

  // POST /api/v1/widgets/alarm/updateDetails/{alarm_details_id}
  async updateAlarmDetails(alarmDetailsId: string, data: {
    title: string;
    description: string;
    alarm_times: string[];
    target_value?: string;
    is_snoozable?: boolean;
  }): Promise<AlarmDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.alarm.updateDetails}/${alarmDetailsId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // SINGLE ITEM TRACKER WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}
  async getTrackerDetailsAndActivity(widgetId: string): Promise<TrackerDetailsAndActivityResponse> {
    const url = buildApiUrl(`${API_CONFIG.singleItemTracker.getTrackerDetailsAndActivity}/${widgetId}`);
    return this.request<TrackerDetailsAndActivityResponse>(url);
  }

  // POST /api/v1/widgets/single-item-tracker/updateActivity/{activity_id}
  async updateTrackerActivity(activityId: string, data: {
    value: string;
    time_added?: string;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    value: string;
    time_added?: string;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.singleItemTracker.updateActivity}/${activityId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}
  async getTrackerDetails(widgetId: string): Promise<TrackerDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.singleItemTracker.getTrackerDetails}/${widgetId}`);
    return this.request<TrackerDetailsResponse>(url);
  }

  // POST /api/v1/widgets/single-item-tracker/updateDetails/{tracker_details_id}
  async updateTrackerDetails(trackerDetailsId: string, data: {
    title: string;
    value_type: string;
    value_unit: string;
    target_value: string;
  }): Promise<TrackerDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.singleItemTracker.updateDetails}/${trackerDetailsId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // WEBSEARCH WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/websearch/getSummaryAndActivity/{widget_id}
  async getWebSearchSummaryAndActivity(widgetId: string): Promise<WebSearchSummaryAndActivityResponse> {
    const url = buildApiUrl(`${API_CONFIG.webSearch.getSummaryAndActivity}/${widgetId}`);
    return this.request<WebSearchSummaryAndActivityResponse>(url);
  }

  // POST /api/v1/widgets/websearch/updateActivity/{activity_id}
  async updateWebSearchActivity(activityId: string, data: {
    status: WebSearchStatus;
    reaction?: string;
    summary?: string;
    source_json?: any;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    status: WebSearchStatus;
    reaction?: string;
    summary?: string;
    source_json?: any;
    updated_at: string;
  }> {
    const url = buildApiUrl(`${API_CONFIG.webSearch.updateActivity}/${activityId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/websearch/getWebsearchDetails/{widget_id}
  async getWebSearchDetails(widgetId: string): Promise<WebSearchDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.webSearch.getWebsearchDetails}/${widgetId}`);
    return this.request<WebSearchDetailsResponse>(url);
  }

  // POST /api/v1/widgets/websearch/updateDetails/{websearch_details_id}
  async updateWebSearchDetails(webSearchDetailsId: string, data: {
    title: string;
  }): Promise<WebSearchDetailsResponse> {
    const url = buildApiUrl(`${API_CONFIG.webSearch.updateDetails}/${webSearchDetailsId}`);
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/websearch/getaisummary/{widget_id}
  async getWebSearchAISummary(widgetId: string): Promise<WebSearchAISummaryResponse> {
    const url = buildApiUrl(`${API_CONFIG.webSearch.getAISummary}/${widgetId}`);
    return this.request<WebSearchAISummaryResponse>(url);
  }

  // ============================================================================
  // HEALTH CHECK ENDPOINTS
  // ============================================================================

  // GET /api/v1/health
  async getHealth(): Promise<{
    status: string;
    service: string;
    version: string;
  }> {
    return this.request(API_CONFIG.health.getHealth);
  }

  // GET /api/v1/health/detailed
  async getDetailedHealth(): Promise<{
    status: string;
    service: string;
    version: string;
    services: {
      database: string;
      ai_services: string;
    };
  }> {
    return this.request(API_CONFIG.health.getDetailedHealth);
  }
}

// Export singleton instance
export const apiService = new ApiService(); 