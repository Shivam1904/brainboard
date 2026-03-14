import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, ApiError } from '../services/api';
import { retryApiCall, createApiCache } from '../utils/apiUtils';

interface UseApiOptions<T> {
  immediate?: boolean;
  retry?: boolean;
  retryAttempts?: number;
  cache?: boolean;
  cacheKey?: string;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
  dependencies?: unknown[];
}

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

// Create a global cache instance
const globalCache = createApiCache<unknown>();

export function useApi<T = unknown>(
  endpoint: string,
  options: UseApiOptions<T> = {}
): UseApiState<T> {
  const {
    immediate = true,
    retry = true,
    retryAttempts = 3,
    cache = false,
    cacheKey,
    onSuccess,
    onError,
    dependencies = []
  } = options;

  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
    refetch: async () => { }
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async (signal?: AbortSignal) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Check cache first if enabled
      if (cache && cacheKey) {
        const cachedData = globalCache.get(cacheKey);
        if (cachedData) {
          setState(prev => ({
            ...prev,
            data: cachedData as T,
            loading: false
          }));
          onSuccess?.(cachedData as T);
          return;
        }
      }

      // Make API call
      const apiCall = () => apiService.get<T>(endpoint);
      const data = retry ?
        await retryApiCall(apiCall, retryAttempts) :
        await apiCall();

      // Cache the result if enabled
      if (cache && cacheKey) {
        globalCache.set(cacheKey, data);
      }

      setState(prev => ({
        ...prev,
        data,
        loading: false
      }));
      onSuccess?.(data);

    } catch (error) {
      if (signal?.aborted) return;

      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        status: 500,
        details: error
      };

      setState(prev => ({
        ...prev,
        error: apiError,
        loading: false
      }));
      onError?.(apiError);
    }
  }, [endpoint, retry, retryAttempts, cache, cacheKey, onSuccess, onError]);

  const refetch = useCallback(async () => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    await fetchData(abortControllerRef.current.signal);
  }, [fetchData]);

  // Set up the refetch function
  useEffect(() => {
    setState(prev => ({ ...prev, refetch }));
  }, [refetch]);

  // Initial fetch
  useEffect(() => {
    if (immediate) {
      refetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, refetch, ...dependencies]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return state;
}

// Hook for POST requests
export function useApiPost<T = unknown, D = unknown>(
  endpoint: string,
  options: UseApiOptions<T> = {}
) {
  const {
    onSuccess,
    onError,
    retry = false,
    retryAttempts = 1
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: ApiError | null;
  }>({
    data: null,
    loading: false,
    error: null
  });

  const post = useCallback(async (data: D) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const apiCall = () => apiService.post<T>(endpoint, data);
      const result = retry ?
        await retryApiCall(apiCall, retryAttempts) :
        await apiCall();

      setState(prev => ({
        ...prev,
        data: result,
        loading: false
      }));
      onSuccess?.(result as T);

    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        status: 500,
        details: error
      };

      setState(prev => ({
        ...prev,
        error: apiError,
        loading: false
      }));
      onError?.(apiError);
    }
  }, [endpoint, retry, retryAttempts, onSuccess, onError]);

  return { ...state, post };
}

// Hook for PUT requests
export function useApiPut<T = unknown, D = unknown>(
  endpoint: string,
  options: UseApiOptions<T> = {}
) {
  const {
    onSuccess,
    onError,
    retry = false,
    retryAttempts = 1
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: ApiError | null;
  }>({
    data: null,
    loading: false,
    error: null
  });

  const put = useCallback(async (data: D) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const apiCall = () => apiService.put<T>(endpoint, data);
      const result = retry ?
        await retryApiCall(apiCall, retryAttempts) :
        await apiCall();

      setState(prev => ({
        ...prev,
        data: result,
        loading: false
      }));
      onSuccess?.(result as T);

    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        status: 500,
        details: error
      };

      setState(prev => ({
        ...prev,
        error: apiError,
        loading: false
      }));
      onError?.(apiError);
    }
  }, [endpoint, retry, retryAttempts, onSuccess, onError]);

  return { ...state, put };
}

// Hook for DELETE requests
export function useApiDelete<T = unknown>(
  endpoint: string,
  options: UseApiOptions<T> = {}
) {
  const {
    onSuccess,
    onError,
    retry = false,
    retryAttempts = 1
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: ApiError | null;
  }>({
    data: null,
    loading: false,
    error: null
  });

  const del = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const apiCall = () => apiService.delete<T>(endpoint);
      const result = retry ?
        await retryApiCall(apiCall, retryAttempts) :
        await apiCall();

      setState(prev => ({
        ...prev,
        data: result,
        loading: false
      }));
      onSuccess?.(result as T);

    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        status: 500,
        details: error
      };

      setState(prev => ({
        ...prev,
        error: apiError,
        loading: false
      }));
      onError?.(apiError);
    }
  }, [endpoint, retry, retryAttempts, onSuccess, onError]);

  return { ...state, delete: del };
} 