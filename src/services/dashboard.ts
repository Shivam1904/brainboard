import { apiService } from './api';
import { API_ENDPOINTS } from '../config/environment';

export interface DashboardWidget {
  id: string;
  type: string;
  layout: {
    x: number;
    y: number;
    w: number;
    h: number;
    minW?: number;
    minH?: number;
    maxW?: number;
    maxH?: number;
  };
  config?: Record<string, any>;
  priority?: number;
  enabled?: boolean;
  scheduledItem?: {
    id: string;
    title: string;
    type: string;
    frequency: string;
    category?: string;
    importance?: 'High' | 'Medium' | 'Low';
    alarm?: string;
    searchQuery?: string;
  };
}

export interface TodayWidgetsResponse {
  widgets: DashboardWidget[];
  date: string;
  user_id?: string;
  layout_version?: string;
}

export interface DashboardLayout {
  widgets: DashboardWidget[];
  layout_version: string;
  last_updated: string;
}

export class DashboardService {
  /**
   * Get today's widget configuration for the current user
   */
  async getTodayWidgets(date?: string): Promise<TodayWidgetsResponse> {
    const params: Record<string, string> = {};
    
    if (date) {
      params.date = date;
    } else {
      // Default to today's date
      params.date = new Date().toISOString().split('T')[0];
    }

    return apiService.get<TodayWidgetsResponse>(API_ENDPOINTS.dashboard.widgets, params);
  }

  /**
   * Save dashboard layout and widget configuration
   */
  async saveDashboardLayout(layout: DashboardLayout): Promise<void> {
    return apiService.post(API_ENDPOINTS.dashboard.layout, layout);
  }

  /**
   * Get user dashboard preferences
   */
  async getDashboardPreferences(): Promise<Record<string, any>> {
    return apiService.get(API_ENDPOINTS.dashboard.preferences);
  }

  /**
   * Update user dashboard preferences
   */
  async updateDashboardPreferences(preferences: Record<string, any>): Promise<void> {
    return apiService.put(API_ENDPOINTS.dashboard.preferences, preferences);
  }

  /**
   * Get widget-specific data
   */
  async getWidgetData(widgetId: string, params?: Record<string, any>): Promise<any> {
    return apiService.get(`/api/widgets/${widgetId}/data`, params);
  }

  /**
   * Update widget configuration
   */
  async updateWidgetConfig(widgetId: string, config: Record<string, any>): Promise<void> {
    return apiService.put(`/api/widgets/${widgetId}/config`, config);
  }

  /**
   * Enable/disable a widget
   */
  async toggleWidget(widgetId: string, enabled: boolean): Promise<void> {
    return apiService.put(`/api/widgets/${widgetId}/toggle`, { enabled });
  }

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(date?: string): Promise<{
    total_widgets: number;
    active_widgets: number;
    completed_tasks: number;
    pending_reminders: number;
    last_activity: string;
  }> {
    const params: Record<string, string> = {};
    if (date) {
      params.date = date;
    }
    
    return apiService.get('/api/dashboard/stats', params);
  }
}

// Create singleton instance
export const dashboardService = new DashboardService(); 