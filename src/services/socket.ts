// Socket service for real-time AI chat communication
// This will handle WebSocket connections for live AI responses and thinking feedback

export interface SocketMessage {
  type: 'thinking' | 'response' | 'interactive' | 'error' | 'connection';
  data: any;
  timestamp: number;
}

export interface ThinkingStep {
  id: string;
  step: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  details?: string;
}

export interface AIResponse {
  id: string;
  content: string;
  thinkingSteps: ThinkingStep[];
  interactiveComponents?: InteractiveComponent[];
  isComplete: boolean;
}

export interface InteractiveComponent {
  id: string;
  type: 'button' | 'select' | 'input' | 'slider' | 'checkbox';
  label: string;
  options?: string[];
  value?: any;
  metadata?: any;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'thinking';
  content: string;
  timestamp: Date;
  thinkingSteps?: ThinkingStep[];
  interactiveComponents?: InteractiveComponent[];
  isComplete?: boolean;
}

class SocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();
  private isConnecting = false;

  // Connection state
  public isConnected = false;
  public connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error' = 'disconnected';

  constructor() {
    // Auto-reconnect on page visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !this.isConnected && !this.isConnecting) {
        this.connect();
      }
    });
  }

  // Connect to WebSocket server
  public connect(url?: string): Promise<void> {
    if (this.isConnecting || this.isConnected) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.isConnecting = true;
      this.connectionStatus = 'connecting';

      const wsUrl = url || this.getWebSocketUrl();
      
      try {
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.isConnected = true;
          this.isConnecting = false;
          this.connectionStatus = 'connected';
          this.reconnectAttempts = 0;
          this.emit('connection', { status: 'connected' });
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            console.log('Received WebSocket message:', message);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnected = false;
          this.isConnecting = false;
          this.connectionStatus = 'disconnected';
          this.emit('connection', { status: 'disconnected', code: event.code });
          
          // Attempt to reconnect if not a clean close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          this.connectionStatus = 'error';
          this.emit('connection', { status: 'error', error });
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        this.connectionStatus = 'error';
        reject(error);
      }
    });
  }

  // Disconnect from WebSocket server
  public disconnect(): void {
    if (this.socket) {
      this.socket.close(1000, 'User initiated disconnect');
      this.socket = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    this.connectionStatus = 'disconnected';
  }

  // Send message to server
  public send(type: SocketMessage['type'] | string, data: any): void {
    if (!this.isConnected || !this.socket) {
      console.warn('WebSocket not connected, cannot send message');
      return;
    }

    const message: SocketMessage = {
      type: type as SocketMessage['type'],
      data,
      timestamp: Date.now()
    };

    this.socket.send(JSON.stringify(message));
  }

  // Send chat message to AI
  public sendChatMessage(message: string, sessionId?: string): void {
    // Send message in the format expected by our backend
    const messageData = {
      message,
      session_id: sessionId
    };
    
    if (this.socket && this.isConnected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      console.error('WebSocket not connected');
    }
  }

  // Send interactive component action
  public sendInteractiveAction(componentId: string, action: string, value: any): void {
    this.send('interactive_action', {
      componentId,
      action,
      value,
      timestamp: new Date().toISOString()
    });
  }

  // Subscribe to events
  public on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  // Unsubscribe from events
  public off(event: string, callback: (data: any) => void): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  // Emit event to listeners
  private emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event callback:', error);
        }
      });
    }
  }

  // Handle incoming messages
  private handleMessage(message: any): void {
    // Handle the format sent by our backend
    switch (message.type) {
      case 'thinking':
        this.emit('thinking', {
          step: message.step,
          details: message.details,
          timestamp: message.timestamp
        });
        break;
      case 'response':
        this.emit('response', {
          content: message.content,
          session_id: message.session_id,
          is_complete: message.is_complete,
          timestamp: message.timestamp
        });
        break;
      case 'component':
        this.emit('response', {
          type: 'component',
          content: message.content,
          component: message.component,
          session_id: message.session_id,
          is_complete: message.is_complete,
          timestamp: message.timestamp
        });
        break;
      case 'error':
        this.emit('error', {
          error: message.error,
          timestamp: message.timestamp
        });
        break;
      case 'connection':
        // Set connection status to connected when we receive connection message
        this.isConnected = true;
        this.connectionStatus = 'connected';
        this.emit('connection', {
          status: 'connected',
          connection_id: message.connection_id,
          message: message.message,
          timestamp: message.timestamp
        });
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  // Schedule reconnection attempt
  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (!this.isConnected && !this.isConnecting) {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  // Get WebSocket URL based on environment
  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NODE_ENV === 'development' 
      ? 'localhost:8000' 
      : window.location.host;
    
    return `${protocol}//${host}/api/v1/chat/ws/chat`;
  }

  // Get connection status
  public getStatus(): { isConnected: boolean; status: string; reconnectAttempts: number } {
    return {
      isConnected: this.isConnected,
      status: this.connectionStatus,
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

// Create singleton instance
export const socketService = new SocketService(); 