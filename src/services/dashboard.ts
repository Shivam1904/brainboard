// Dashboard Service - Simple wrapper around API service
// No conversions, just direct API calls

import { apiService } from './api';
import { 
  TodayWidgetsResponse,
  AllWidgetsResponse,
  ApiWidgetType,
  ApiFrequency,
  ApiCategory
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

  // Get todo list by type
  async getTodoList(todoType: 'habit' | 'task'): Promise<{
    todo_type: 'habit' | 'task';
    todos: Array<{
      id: string;
      title: string;
      todo_type: 'habit' | 'task';
      description: string;
      due_date: string;
      created_at: string;
    }>;
    total_todos: number;
  }> {
    return apiService.getTodoList(todoType);
  }
}

// Export singleton instance
export const dashboardService = new DashboardService(); 