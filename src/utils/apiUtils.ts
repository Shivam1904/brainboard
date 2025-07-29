import { ApiError } from '../services/api';

// Utility functions for API operations

export const handleApiError = (error: any): ApiError => {
  if (error instanceof Error) {
    return {
      message: error.message,
      status: 500,
      details: error
    };
  }
  
  return {
    message: 'An unexpected error occurred',
    status: 500,
    details: error
  };
};

export const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
  
  throw lastError;
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Data transformation utilities
export const transformApiResponse = <T>(response: any): T => {
  // Handle different response formats
  if (response && typeof response === 'object') {
    if ('data' in response) {
      return response.data;
    }
    if ('result' in response) {
      return response.result;
    }
  }
  
  return response;
};

export const validateApiResponse = <T>(response: any, schema?: any): T => {
  // Basic validation - can be extended with proper schema validation
  if (!response) {
    throw new Error('Invalid API response: response is null or undefined');
  }
  
  return response as T;
};

// URL and parameter utilities
export const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
};

export const parseQueryString = (queryString: string): Record<string, string> => {
  const params: Record<string, string> = {};
  const searchParams = new URLSearchParams(queryString);
  
  searchParams.forEach((value, key) => {
    params[key] = value;
  });
  
  return params;
};

// Date and time utilities for API calls
export const formatDateForApi = (date: Date): string => {
  return date.toISOString();
};

export const parseApiDate = (dateString: string): Date => {
  return new Date(dateString);
};

// Cache utilities
export const createApiCache = <T>() => {
  const cache = new Map<string, { data: T; timestamp: number }>();
  
  return {
    get: (key: string): T | null => {
      const item = cache.get(key);
      if (!item) return null;
      
      // Check if cache is expired (5 minutes)
      if (Date.now() - item.timestamp > 5 * 60 * 1000) {
        cache.delete(key);
        return null;
      }
      
      return item.data;
    },
    
    set: (key: string, data: T): void => {
      cache.set(key, { data, timestamp: Date.now() });
    },
    
    clear: (): void => {
      cache.clear();
    },
    
    delete: (key: string): boolean => {
      return cache.delete(key);
    }
  };
};

// Request/Response interceptors
export const createRequestInterceptor = () => {
  const interceptors: Array<(request: Request) => Request> = [];
  
  return {
    add: (interceptor: (request: Request) => Request) => {
      interceptors.push(interceptor);
    },
    
    apply: (request: Request): Request => {
      return interceptors.reduce((req, interceptor) => interceptor(req), request);
    }
  };
};

export const createResponseInterceptor = () => {
  const interceptors: Array<(response: Response) => Response | Promise<Response>> = [];
  
  return {
    add: (interceptor: (response: Response) => Response | Promise<Response>) => {
      interceptors.push(interceptor);
    },
    
    apply: async (response: Response): Promise<Response> => {
      let result = response;
      for (const interceptor of interceptors) {
        result = await interceptor(result);
      }
      return result;
    }
  };
}; 