// Dashboard Service - Simple wrapper around API service
// No conversions, just direct API calls

import { apiService } from './api';
import { 
  TodayWidgetsResponse,
  AllWidgetsResponse,
  ApiWidgetType,
  ApiFrequency,
  ApiCategory,
  TodoTodayResponse
} from '../types';

export class DashboardService {
  // Get today's widget list from API
  async getTodayWidgets(targetDate?: string): Promise<TodayWidgetsResponse> {
    return apiService.getTodayWidgetList(targetDate);
  }

  // Get all widgets list from API
  async getAllWidgets(): Promise<AllWidgetsResponse> {
    return apiService.getAllWidgetList();
  }

  // Add new widget
  async addNewWidget(data: {
    widget_type: ApiWidgetType;
    frequency: ApiFrequency;
    importance: number;
    title: string;
    category: ApiCategory;
  }): Promise<{
    message: string;
    widget_id: string;
    widget_type: string;
    title: string;
  }> {
    return apiService.addNewWidget(data);
  }

  // Update widget details
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
    return apiService.updateWidgetDetails(widgetId, data);
  }

  // Get todo list by type
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
    return apiService.getTodoList(todoType);
  }

  // Get today's todo list by type
  async getTodayTodoList(todoType: 'habit' | 'task' | 'event'): Promise<TodoTodayResponse> {
    return apiService.getTodayTodoList(todoType);
  }

  // Update todo activity status
  async updateTodoActivity(activityId: string, data: {
    status: 'pending' | 'in progress' | 'completed' | 'cancelled';
    progress: number;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    status: 'pending' | 'in progress' | 'completed' | 'cancelled';
    progress: number;
    updated_at: string;
  }> {
    return apiService.updateTodoActivity(activityId, data);
  }

  // Update alarm activity
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
    return apiService.updateAlarmActivity(activityId, data);
  }

  // Update tracker activity
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
    return apiService.updateTrackerActivity(activityId, data);
  }

  // Update websearch activity
  async updateWebSearchActivity(activityId: string, data: {
    status: 'pending' | 'completed' | 'failed';
    reaction?: string;
    summary?: string;
    source_json?: any;
    updated_by: string;
  }): Promise<{
    activity_id: string;
    status: 'pending' | 'completed' | 'failed';
    reaction?: string;
    summary?: string;
    source_json?: any;
    updated_at: string;
  }> {
    return apiService.updateWebSearchActivity(activityId, data);
  }

  // Get alarm details and activity
  async getAlarmDetailsAndActivity(widgetId: string): Promise<{
    alarm_details: {
      id: string;
      widget_id: string;
      title: string;
      description: string;
      alarm_times: string[];
      target_value: string;
      is_snoozable: boolean;
      created_at: string;
      updated_at: string;
    };
    activity: {
      id: string;
      started_at: string;
      snoozed_at: string;
      created_at: string;
      updated_at: string;
    };
  }> {
    return apiService.getAlarmDetailsAndActivity(widgetId);
  }

  // Get tracker details and activity
  async getTrackerDetailsAndActivity(widgetId: string): Promise<{
    tracker_details: {
      id: string;
      widget_id: string;
      title: string;
      value_type: string;
      value_unit: string;
      target_value: string;
      created_at: string;
      updated_at: string;
    };
    activity: {
      id: string;
      value: string;
      time_added: string;
      created_at: string;
      updated_at: string;
    };
  }> {
    return apiService.getTrackerDetailsAndActivity(widgetId);
  }

  // Get websearch summary and activity
  async getWebSearchSummaryAndActivity(widgetId: string): Promise<{
    websearch_details: {
      id: string;
      widget_id: string;
      title: string;
      created_at: string;
      updated_at: string;
    };
    activity: {
      id: string;
      status: 'pending' | 'completed' | 'failed';
      reaction: string;
      summary: string;
      source_json: any;
      created_at: string;
      updated_at: string;
    };
  }> {
    return apiService.getWebSearchSummaryAndActivity(widgetId);
  }

  // Get websearch AI summary
  async getWebSearchAISummary(widgetId: string): Promise<{
    ai_summary_id: string;
    widget_id: string;
    query: string;
    summary: string;
    sources: Array<{
      title: string;
      url: string;
    }>;
    search_successful: boolean;
    results_count: number;
    ai_model_used: string;
    generation_type: string;
    created_at: string;
    updated_at: string;
  }> {
    return apiService.getWebSearchAISummary(widgetId);
  }
}

// Export singleton instance
export const dashboardService = new DashboardService(); 