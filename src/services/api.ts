import { API_CONFIG, buildApiUrl } from '../config/api';
import { TodayWidgetsResponse, BaseWidget } from '../types';

// Types for API responses
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

// Base API service class
class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_CONFIG.baseUrl) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('auth_token');
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'bypass-tunnel-reminder': 'true',
      'ngrok-skip-browser-warning': 'true',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = buildApiUrl(`${endpoint}`, params);
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    const url = buildApiUrl(`${this.baseUrl}${endpoint}`);
    const response = await fetch(url, {
      method: 'POST',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    const url = buildApiUrl(`${this.baseUrl}${endpoint}`);
    const response = await fetch(url, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(endpoint: string): Promise<T> {
    const url = buildApiUrl(`${this.baseUrl}${endpoint}`);
    const response = await fetch(url, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Specific API services
export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>('/api/auth/login', credentials);
    apiService.setToken(response.access_token);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await apiService.post('/api/auth/logout');
    } finally {
      apiService.clearToken();
    }
  }

  async register(userData: { email: string; password: string; name: string }): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>('/api/auth/register', userData);
    apiService.setToken(response.access_token);
    return response;
  }
}

export class ReminderService {
  async getReminders(): Promise<any[]> {
    return apiService.get<any[]>('/api/reminders');
  }

  async createReminder(reminder: any): Promise<any> {
    return apiService.post<any>('/api/reminders', reminder);
  }

  async updateReminder(id: string, reminder: any): Promise<any> {
    return apiService.put<any>(`/api/reminders/${id}`, reminder);
  }

  async deleteReminder(id: string): Promise<void> {
    return apiService.delete(`/api/reminders/${id}`);
  }
}

export class SummaryService {
  async getSummaries(): Promise<any[]> {
    return apiService.get<any[]>('/api/summaries');
  }

  async createSummary(summary: any): Promise<any> {
    return apiService.post<any>('/api/summaries', summary);
  }
}

export class DashboardService {
  async getTodayWidgets(): Promise<TodayWidgetsResponse> {
    return apiService.get<TodayWidgetsResponse>('/api/v1/dashboard/widgets/today');
  }

  async getWidget(widgetId: string): Promise<BaseWidget> {
    return apiService.get<BaseWidget>(`/api/v1/widgets/${widgetId}`);
  }

  async updateWidget(widgetId: string, widgetData: Partial<BaseWidget>): Promise<BaseWidget> {
    return apiService.put<BaseWidget>(`/api/v1/widgets/${widgetId}`, widgetData);
  }

  async deleteWidget(widgetId: string): Promise<void> {
    return apiService.delete(`/api/v1/widgets/${widgetId}`);
  }

  async createWidget(widgetData: Omit<BaseWidget, 'id'>): Promise<BaseWidget> {
    return apiService.post<BaseWidget>('/api/v1/widgets', widgetData);
  }
}

// Export service instances
export const authService = new AuthService();
export const reminderService = new ReminderService();
export const summaryService = new SummaryService();
export const dashboardService = new DashboardService(); 