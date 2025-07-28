import { getEnvironmentConfig, WS_EVENTS } from '../config/environment';
import { apiService } from './api';

export interface WebSocketMessage {
  event: string;
  data: any;
  timestamp: number;
}

export interface WebSocketConfig {
  url: string;
  reconnectAttempts: number;
  reconnectDelay: number;
  heartbeatInterval: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval = 30000;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private eventListeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnecting = false;
  private isManualClose = false;

  constructor() {
    this.connect();
  }

  private getWebSocketUrl(): string {
    const config = getEnvironmentConfig();
    return `${config.wsBaseUrl}/ws`;
  }

  private connect(): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;
    const url = this.getWebSocketUrl();

    try {
      this.ws = new WebSocket(url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.handleReconnect();
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.emit('connected', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnecting = false;
      this.stopHeartbeat();
      this.emit('disconnected', { code: event.code, reason: event.reason });

      if (!this.isManualClose) {
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    const { event, data } = message;
    
    // Emit the specific event
    this.emit(event, data);
    
    // Also emit a generic message event
    this.emit('message', message);
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed', {});
      return;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  public send(event: string, data: any = {}): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        event,
        data,
        timestamp: Date.now(),
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', event);
    }
  }

  public on(event: string, callback: (data: any) => void): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback);
  }

  public off(event: string, callback: (data: any) => void): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  public disconnect(): void {
    this.isManualClose = true;
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  public reconnect(): void {
    this.isManualClose = false;
    this.reconnectAttempts = 0;
    this.disconnect();
    setTimeout(() => this.connect(), 100);
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();

// Convenience functions for common WebSocket operations
export const subscribeToReminders = (callback: (data: any) => void) => {
  websocketService.on(WS_EVENTS.REMINDER_CREATED, callback);
  websocketService.on(WS_EVENTS.REMINDER_UPDATED, callback);
  websocketService.on(WS_EVENTS.REMINDER_DELETED, callback);
};

export const subscribeToSummaries = (callback: (data: any) => void) => {
  websocketService.on(WS_EVENTS.SUMMARY_CREATED, callback);
  websocketService.on(WS_EVENTS.SUMMARY_UPDATED, callback);
  websocketService.on(WS_EVENTS.SUMMARY_DELETED, callback);
};

export const unsubscribeFromReminders = (callback: (data: any) => void) => {
  websocketService.off(WS_EVENTS.REMINDER_CREATED, callback);
  websocketService.off(WS_EVENTS.REMINDER_UPDATED, callback);
  websocketService.off(WS_EVENTS.REMINDER_DELETED, callback);
};

export const unsubscribeFromSummaries = (callback: (data: any) => void) => {
  websocketService.off(WS_EVENTS.SUMMARY_CREATED, callback);
  websocketService.off(WS_EVENTS.SUMMARY_UPDATED, callback);
  websocketService.off(WS_EVENTS.SUMMARY_DELETED, callback);
}; 