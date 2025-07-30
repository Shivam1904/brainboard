// API Service - Direct API calls without conversions
// This service matches the actual backend API endpoints exactly

import { 
  TodayWidgetsResponse,
  AllWidgetsResponse,
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
  ApiPriority,
  ApiCategory,
  TodoStatus,
  WebSearchStatus
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
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
  async getTodayWidgetList(targetDate?: string): Promise<TodayWidgetsResponse> {
    const params = targetDate ? `?target_date=${targetDate}` : '';
    return this.request<TodayWidgetsResponse>(`/dashboard/getTodayWidgetList${params}`);
  }

  // GET /api/v1/dashboard/getAllWidgetList
  async getAllWidgetList(): Promise<AllWidgetsResponse> {
    return this.request<AllWidgetsResponse>('/dashboard/getAllWidgetList');
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
    return this.request('/dashboard/widget/addnew', {
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
    return this.request(`/dashboard/widget/addtotoday/${widgetId}`, {
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
    return this.request(`/dashboard/widget/updateWidgetDetails/${widgetId}`, {
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
    return this.request(`/dashboard/widget/updateDetails/${widgetId}`, {
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
    return this.request(`/dashboard/widgets/updateDailyWidget/${dailyWidgetId}`, {
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
    return this.request(`/dashboard/getTodoList/${todoType}`);
  }

  // ============================================================================
  // TODO WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/todo/getTodayTodoList/{todo_type}
  async getTodayTodoList(todoType: 'habit' | 'task' | 'event'): Promise<TodoTodayResponse> {
    return this.request<TodoTodayResponse>(`/widgets/todo/getTodayTodoList/${todoType}`);
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
    return this.request(`/widgets/todo/updateActivity/${activityId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/todo/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}
  async getTodoItemDetailsAndActivity(dailyWidgetId: string, widgetId: string): Promise<TodoDetailsAndActivityResponse> {
    return this.request<TodoDetailsAndActivityResponse>(`/widgets/todo/getTodoItemDetailsAndActivity/${dailyWidgetId}/${widgetId}`);
  }

  // GET /api/v1/widgets/todo/getTodoDetails/{widget_id}
  async getTodoDetails(widgetId: string): Promise<TodoDetailsResponse> {
    return this.request<TodoDetailsResponse>(`/widgets/todo/getTodoDetails/${widgetId}`);
  }

  // POST /api/v1/widgets/todo/updateDetails/{todo_details_id}
  async updateTodoDetails(todoDetailsId: string, data: {
    title: string;
    description: string;
    due_date: string;
    todo_type: 'habit' | 'task' | 'event';
  }): Promise<TodoDetailsResponse> {
    return this.request(`/widgets/todo/updateDetails/${todoDetailsId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // ALARM WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/alarm/getAlarmDetailsAndActivity/{widget_id}
  async getAlarmDetailsAndActivity(widgetId: string): Promise<AlarmDetailsAndActivityResponse> {
    return this.request<AlarmDetailsAndActivityResponse>(`/widgets/alarm/getAlarmDetailsAndActivity/${widgetId}`);
  }

  // POST /api/v1/widgets/alarm/snoozeAlarm/{activity_id}
  async snoozeAlarm(activityId: string, snoozeMinutes: number = 2): Promise<{
    activity_id: string;
    snoozed_at: string;
    snooze_until: string;
    snooze_count: number;
    updated_at: string;
  }> {
    return this.request(`/widgets/alarm/snoozeAlarm/${activityId}?snooze_minutes=${snoozeMinutes}`, {
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
    return this.request(`/widgets/alarm/stopAlarm/${activityId}`, {
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
    return this.request(`/widgets/alarm/updateActivity/${activityId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/alarm/getAlarmDetails/{widget_id}
  async getAlarmDetails(widgetId: string): Promise<AlarmDetailsResponse> {
    return this.request<AlarmDetailsResponse>(`/widgets/alarm/getAlarmDetails/${widgetId}`);
  }

  // POST /api/v1/widgets/alarm/updateDetails/{alarm_details_id}
  async updateAlarmDetails(alarmDetailsId: string, data: {
    title: string;
    description: string;
    alarm_times: string[];
    target_value?: string;
    is_snoozable?: boolean;
  }): Promise<AlarmDetailsResponse> {
    return this.request(`/widgets/alarm/updateDetails/${alarmDetailsId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // SINGLE ITEM TRACKER WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/single-item-tracker/getTrackerDetailsAndActivity/{widget_id}
  async getTrackerDetailsAndActivity(widgetId: string): Promise<TrackerDetailsAndActivityResponse> {
    return this.request<TrackerDetailsAndActivityResponse>(`/widgets/single-item-tracker/getTrackerDetailsAndActivity/${widgetId}`);
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
    return this.request(`/widgets/single-item-tracker/updateActivity/${activityId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/single-item-tracker/getTrackerDetails/{widget_id}
  async getTrackerDetails(widgetId: string): Promise<TrackerDetailsResponse> {
    return this.request<TrackerDetailsResponse>(`/widgets/single-item-tracker/getTrackerDetails/${widgetId}`);
  }

  // POST /api/v1/widgets/single-item-tracker/updateDetails/{tracker_details_id}
  async updateTrackerDetails(trackerDetailsId: string, data: {
    title: string;
    value_type: string;
    value_unit: string;
    target_value: string;
  }): Promise<TrackerDetailsResponse> {
    return this.request(`/widgets/single-item-tracker/updateDetails/${trackerDetailsId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // WEBSEARCH WIDGET ENDPOINTS
  // ============================================================================

  // GET /api/v1/widgets/websearch/getSummaryAndActivity/{widget_id}
  async getWebSearchSummaryAndActivity(widgetId: string): Promise<WebSearchSummaryAndActivityResponse> {
    return this.request<WebSearchSummaryAndActivityResponse>(`/widgets/websearch/getSummaryAndActivity/${widgetId}`);
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
    return this.request(`/widgets/websearch/updateActivity/${activityId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/websearch/getWebsearchDetails/{widget_id}
  async getWebSearchDetails(widgetId: string): Promise<WebSearchDetailsResponse> {
    return this.request<WebSearchDetailsResponse>(`/widgets/websearch/getWebsearchDetails/${widgetId}`);
  }

  // POST /api/v1/widgets/websearch/updateDetails/{websearch_details_id}
  async updateWebSearchDetails(webSearchDetailsId: string, data: {
    title: string;
  }): Promise<WebSearchDetailsResponse> {
    return this.request(`/widgets/websearch/updateDetails/${webSearchDetailsId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // GET /api/v1/widgets/websearch/getaisummary/{widget_id}
  async getWebSearchAISummary(widgetId: string): Promise<WebSearchAISummaryResponse> {
    return this.request<WebSearchAISummaryResponse>(`/widgets/websearch/getaisummary/${widgetId}`);
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
    return this.request('/health');
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
    return this.request('/health/detailed');
  }
}

// Export singleton instance
export const apiService = new ApiService(); 