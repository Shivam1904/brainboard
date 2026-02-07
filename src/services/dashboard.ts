// Dashboard Service - Clean implementation using new consolidated API
// This service provides a simplified interface for dashboard operations

import { apiService, DashboardWidget, DailyWidget } from './api';

export interface CreateWidgetData {
  widget_type: string;
  title: string;
  frequency: string;
  frequency_details?: Record<string, any>;
  importance: number;
  category: string;
  description?: string;
  is_permanent?: boolean;
  widget_config?: Record<string, any>;
}

export interface UpdateWidgetData {
  title?: string;
  frequency?: string;
  frequency_details?: Record<string, any>;
  importance?: number;
  category?: string;
  description?: string;
  is_permanent?: boolean;
  widget_config?: Record<string, any>;
}

export class DashboardService {
  // ============================================================================
  // DASHBOARD WIDGETS OPERATIONS
  // ============================================================================

  // Get today's widget list from API
  async getTodayWidgets(targetDate: string): Promise<DailyWidget[]> {
    return apiService.getTodayWidgetList(targetDate);
  }

  // Get all widgets list from API
  async getAllWidgets(): Promise<DashboardWidget[]> {
    return apiService.getAllWidgets();
  }

  // Create new widget
  async createWidget(data: CreateWidgetData): Promise<DashboardWidget> {
    return apiService.createWidget(data);
  }

  // Get specific widget by ID
  async getWidget(widgetId: string): Promise<DashboardWidget> {
    return apiService.getWidget(widgetId);
  }

  // Update widget
  async updateWidget(widgetId: string, data: UpdateWidgetData): Promise<DashboardWidget> {
    return apiService.updateWidget(widgetId, data);
  }

  // Delete widget
  async deleteWidget(widgetId: string): Promise<{ message: string }> {
    return apiService.deleteWidget(widgetId);
  }

  // Get widgets by type
  async getWidgetsByType(widgetType: string): Promise<DashboardWidget[]> {
    return apiService.getWidgetsByType(widgetType);
  }

  // ============================================================================
  // DASHBOARD MANAGEMENT OPERATIONS
  // ============================================================================

  // Add widget to today's dashboard
  async addWidgetToToday(widgetId: string, targetDate: string): Promise<{
    success: boolean;
    message: string;
    daily_widget_id: string;
    widget_id: string;
  }> {
    return apiService.addWidgetToToday(widgetId, targetDate);
  }

  // Remove widget from today's dashboard
  async removeWidgetFromToday(dailyWidgetId: string, targetDate: string): Promise<{
    success: boolean;
    message: string;
    daily_widget_id: string;
    is_active: boolean;
  }> {
    return apiService.removeWidgetFromToday(dailyWidgetId, targetDate);
  }

  // Update activity data for a daily widget
  async updateActivity(dailyWidgetId: string, activityData: Record<string, any>): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    return apiService.updateActivity(dailyWidgetId, activityData);
  }

  // Get activity data for a daily widget
  async getTodayWidget(dailyWidgetId: string): Promise<DailyWidget> {
    return apiService.getTodayWidget(dailyWidgetId);
  }

  // Get today's daily widget by underlying widget id
  async getTodayWidgetByWidgetId(widgetId: string, targetDate: string): Promise<DailyWidget | null> {
    return apiService.getTodayWidgetByWidgetId(widgetId, targetDate);
  }

  // ============================================================================
  // CONVENIENCE METHODS FOR WIDGET-SPECIFIC OPERATIONS
  // ============================================================================

  // Helper method for creating widgets with common fields
  private async _createBaseWidget(
    widgetType: string,
    data: {
      title: string;
      importance: number;
      category: string;
      description?: string;
      frequency?: string;
    },
    config: Record<string, any>
  ): Promise<DashboardWidget> {
    return this.createWidget({
      widget_type: widgetType,
      title: data.title,
      frequency: data.frequency || 'daily',
      importance: data.importance,
      category: data.category,
      description: data.description,
      widget_config: config
    });
  }

  // Create an alarm widget
  async createAlarmWidget(data: {
    title: string;
    importance: number;
    category: string;
    description?: string;
    alarm_times: string[];
    is_snoozable?: boolean;
  }): Promise<DashboardWidget> {
    return this._createBaseWidget(
      'alarm',
      data,
      {
        alarm_times: data.alarm_times,
        is_snoozable: data.is_snoozable ?? true
      }
    );
  }

  // Create a todo widget
  async createTodoWidget(data: {
    title: string;
    importance: number;
    category: string;
    description?: string;
    todo_type: 'habit' | 'task' | 'event';
    due_date?: string;
  }): Promise<DashboardWidget> {
    return this._createBaseWidget(
      'todo',
      data,
      {
        todo_type: data.todo_type,
        due_date: data.due_date
      }
    );
  }

  // Create a single item tracker widget
  async createTrackerWidget(data: {
    title: string;
    importance: number;
    category: string;
    description?: string;
    value_type: string;
    value_unit: string;
    target_value: string;
  }): Promise<DashboardWidget> {
    return this._createBaseWidget(
      'single_item_tracker',
      data,
      {
        value_type: data.value_type,
        value_unit: data.value_unit,
        target_value: data.target_value
      }
    );
  }

  // Create a web search widget
  async createWebSearchWidget(data: {
    title: string;
    importance: number;
    category: string;
    description?: string;
    frequency?: string;
    search_query_detailed: string;
  }): Promise<DashboardWidget> {
    return this._createBaseWidget(
      'websearch',
      data,
      {
        search_query_detailed: data.search_query_detailed
      }
    );
  }

  // Update alarm activity
  async updateAlarmActivity(dailyWidgetId: string, alarmActivity: {
    started_at?: string;
    snoozed_at?: string;
    snooze_until?: string;
    snooze_count?: number;
    activity_history?: Array<{
      type: 'snooze' | 'stop';
      timestamp: string;
      snooze_until?: string;
      snooze_count?: number;
      total_snooze_count?: number;
    }>;
  }): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    return this.updateActivity(dailyWidgetId, alarmActivity);
  }

  // Update todo activity
  async updateTodoActivity(dailyWidgetId: string, todoActivity: {
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
    progress?: number;
    started_at?: string;
  }): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    return this.updateActivity(dailyWidgetId, todoActivity);
  }

  // Update tracker activity
  async updateTrackerActivity(dailyWidgetId: string, trackerActivity: {
    value: string;
    time_added?: string;
    notes?: string;
  }): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    return this.updateActivity(dailyWidgetId, trackerActivity);
  }

  // Update web search activity
  async updateWebSearchActivity(dailyWidgetId: string, webSearchActivity: {
    status: 'pending' | 'completed' | 'failed';
    reaction?: string;
    summary?: string;
    source_json?: any;
    completed_at?: string;
  }): Promise<{
    success: boolean;
    message: string;
    activity_data: Record<string, any>;
  }> {
    return this.updateActivity(dailyWidgetId, webSearchActivity);
  }

  // Get alarm activity data
  async getAlarmActivity(dailyWidgetId: string): Promise<DailyWidget> {
    const activityData = await this.getTodayWidget(dailyWidgetId);
    return activityData || {};
  }

  // Get todo activity data
  async getTodoActivity(dailyWidgetId: string): Promise<DailyWidget> {
    const activityData = await this.getTodayWidget(dailyWidgetId);
    return activityData || {};
  }

  // Get tracker activity data
  async getTrackerActivity(dailyWidgetId: string): Promise<DailyWidget> {
    const activityData = await this.getTodayWidget(dailyWidgetId);
    return activityData || {};
  }

  // Get web search activity data
  async getWebSearchActivity(dailyWidgetId: string): Promise<DailyWidget> {
    const activityData = await this.getTodayWidget(dailyWidgetId);
    return activityData || {};
  }

  // ============================================================================
  // WIDGET-SPECIFIC METHODS
  // ============================================================================

  // Get alarm details and activity
  async getAlarmDetailsAndActivity(widgetId: string): Promise<any> {
    return apiService.getAlarmDetailsAndActivity(widgetId);
  }

  // Get tracker details and activity
  async getTrackerDetailsAndActivity(widgetId: string): Promise<any> {
    // This would typically call a specific tracker endpoint
    // For now, we'll use the general getTodayWidget method
    return this.getTodayWidget(widgetId);
  }

  // Get todo item details and activity
  async getTodoItemDetailsAndActivity(dailyWidgetId: string, _widgetId: string): Promise<any> {
    // This would typically call a specific todo endpoint
    // For now, we'll use the general getTodayWidget method
    return this.getTodayWidget(dailyWidgetId);
  }
}

// Export singleton instance
export const dashboardService = new DashboardService(); 