// Environment configuration for different deployment stages

export type Environment = 'development' | 'staging' | 'production';

interface EnvironmentConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  enableLogging: boolean;
  enableCache: boolean;
  retryAttempts: number;
  timeout: number;
}

const environments: Record<Environment, EnvironmentConfig> = {
  development: {
    apiBaseUrl: 'http://localhost:8000',
    wsBaseUrl: 'ws://localhost:8000',
    enableLogging: true,
    enableCache: false,
    retryAttempts: 3,
    timeout: 10000,
  },
  staging: {
    apiBaseUrl: 'https://staging-api.brainboard.com',
    wsBaseUrl: 'wss://staging-api.brainboard.com',
    enableLogging: true,
    enableCache: true,
    retryAttempts: 3,
    timeout: 15000,
  },
  production: {
    apiBaseUrl: 'https://api.brainboard.com',
    wsBaseUrl: 'wss://api.brainboard.com',
    enableLogging: false,
    enableCache: true,
    retryAttempts: 2,
    timeout: 20000,
  },
};

// Get current environment
export const getCurrentEnvironment = (): Environment => {
  const env = import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE;
  
  switch (env) {
    case 'production':
      return 'production';
    case 'staging':
      return 'staging';
    default:
      return 'development';
  }
};

// Get current environment config
export const getEnvironmentConfig = (): EnvironmentConfig => {
  const currentEnv = getCurrentEnvironment();
  return environments[currentEnv];
};

// Environment-specific utilities
export const isDevelopment = (): boolean => getCurrentEnvironment() === 'development';
export const isProduction = (): boolean => getCurrentEnvironment() === 'production';
export const isStaging = (): boolean => getCurrentEnvironment() === 'staging';

// Feature flags
export const FEATURE_FLAGS = {
  enableRealTimeUpdates: !isProduction(),
  enableDebugMode: isDevelopment(),
  enableAnalytics: isProduction() || isStaging(),
  enableErrorReporting: isProduction() || isStaging(),
} as const;

// API endpoints configuration
export const API_ENDPOINTS = {
  dashboard: {
    widgets: '/api/v1/dashboard/widgets/today',
    layout: '/api/v1/dashboard/layout',
    preferences: '/api/v1/dashboard/preferences',
  },
} as const;

// WebSocket events
export const WS_EVENTS = {
  REMINDER_CREATED: 'reminder_created',
  REMINDER_UPDATED: 'reminder_updated',
  REMINDER_DELETED: 'reminder_deleted',
  SUMMARY_CREATED: 'summary_created',
  SUMMARY_UPDATED: 'summary_updated',
  SUMMARY_DELETED: 'summary_deleted',
} as const;

// HTTP status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
} as const; 