# API Services Documentation

This directory contains all the necessary utilities, services, and hooks for communicating with the REST API server.

## Overview

The API layer consists of:
- **Core API Service**: Base service for HTTP requests with authentication
- **Specialized Services**: Domain-specific services (Auth, Reminders, Summaries)
- **React Hooks**: Easy-to-use hooks for API calls
- **Utilities**: Helper functions for common operations
- **Configuration**: Environment-specific settings

## Quick Start

### 1. Basic API Call

```typescript
import { apiService } from '../services/api';

// GET request
const data = await apiService.get('/api/reminders');

// POST request
const newReminder = await apiService.post('/api/reminders', {
  title: 'New Reminder',
  description: 'Description',
  due_date: '2024-01-01'
});
```

### 2. Using React Hooks

```typescript
import { useApi, useApiPost } from '../hooks/useApi';

function MyComponent() {
  // Fetch data
  const { data, loading, error, refetch } = useApi('/api/reminders', {
    cache: true,
    retry: true
  });

  // Create data
  const { post: createReminder, loading: createLoading } = useApiPost('/api/reminders');

  const handleCreate = async () => {
    await createReminder({
      title: 'New Reminder',
      description: 'Description'
    });
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error.message}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

### 3. Authentication

```typescript
import { authService } from '../services/api';

// Login
const response = await authService.login({
  email: 'user@example.com',
  password: 'password123'
});

// Logout
await authService.logout();
```



## Services

### Core API Service (`api.ts`)

The base service that handles all HTTP requests with:
- Automatic authentication token management
- Error handling
- Request/response interceptors
- Type safety

```typescript
import { apiService } from '../services/api';

// Available methods
await apiService.get<T>(endpoint, params?);
await apiService.post<T>(endpoint, data?);
await apiService.put<T>(endpoint, data?);
await apiService.delete<T>(endpoint);

// Authentication
apiService.setToken(token);
apiService.clearToken();
apiService.isAuthenticated();
```

### Specialized Services

#### AuthService
```typescript
import { authService } from '../services/api';

await authService.login(credentials);
await authService.logout();
await authService.register(userData);
```

#### ReminderService
```typescript
import { reminderService } from '../services/api';

await reminderService.getReminders();
await reminderService.createReminder(reminder);
await reminderService.updateReminder(id, reminder);
await reminderService.deleteReminder(id);
```

#### SummaryService
```typescript
import { summaryService } from '../services/api';

await summaryService.getSummaries();
await summaryService.createSummary(summary);
```



## React Hooks

### useApi

Hook for GET requests with caching, retry logic, and loading states.

```typescript
const { data, loading, error, refetch } = useApi<T>(
  endpoint,
  {
    immediate: true,        // Auto-fetch on mount
    retry: true,           // Enable retry on failure
    retryAttempts: 3,      // Number of retry attempts
    cache: true,           // Enable caching
    cacheKey: 'unique-key', // Cache key
    onSuccess: (data) => {}, // Success callback
    onError: (error) => {},  // Error callback
    dependencies: []       // Dependencies for re-fetching
  }
);
```

### useApiPost

Hook for POST requests.

```typescript
const { post, loading, error } = useApiPost<T, D>(
  endpoint,
  {
    onSuccess: (data) => {},
    onError: (error) => {},
    retry: false,
    retryAttempts: 1
  }
);

// Usage
await post(data);
```

### useApiPut

Hook for PUT requests.

```typescript
const { put, loading, error } = useApiPut<T, D>(
  endpoint,
  options
);

// Usage
await put(data);
```

### useApiDelete

Hook for DELETE requests.

```typescript
const { delete: del, loading, error } = useApiDelete<T>(
  endpoint,
  options
);

// Usage
await del();
```

## Utilities (`apiUtils.ts`)

### Error Handling
```typescript
import { handleApiError } from '../utils/apiUtils';

const error = handleApiError(originalError);
```

### Retry Logic
```typescript
import { retryApiCall } from '../utils/apiUtils';

const result = await retryApiCall(
  () => apiCall(),
  maxRetries = 3,
  delay = 1000
);
```

### Debouncing
```typescript
import { debounce } from '../utils/apiUtils';

const debouncedSearch = debounce((searchTerm) => {
  // API call here
}, 500);
```

### Caching
```typescript
import { createApiCache } from '../utils/apiUtils';

const cache = createApiCache<T>();

cache.set('key', data);
const data = cache.get('key');
cache.delete('key');
cache.clear();
```

## Configuration (`environment.ts`)

Environment-specific configuration for different deployment stages.

```typescript
import { getEnvironmentConfig, isDevelopment, isProduction } from '../config/environment';

const config = getEnvironmentConfig();
// Returns environment-specific settings

if (isDevelopment()) {
  // Development-specific code
}
```

### Environment Variables

Create a `.env` file in your project root:

```env
VITE_ENVIRONMENT=development
VITE_API_BASE_URL=http://localhost:8000
```

## Error Handling

All API calls include comprehensive error handling:

```typescript
try {
  const data = await apiService.get('/api/endpoint');
} catch (error) {
  // Error is automatically converted to ApiError format
  console.error('API Error:', error.message);
  console.error('Status:', error.status);
  console.error('Details:', error.details);
}
```

## Best Practices

1. **Use Hooks for React Components**: Prefer `useApi` hooks over direct service calls in components
2. **Enable Caching**: Use caching for frequently accessed data
3. **Handle Loading States**: Always show loading indicators during API calls
4. **Error Boundaries**: Implement error boundaries for graceful error handling
5. **Type Safety**: Always define TypeScript interfaces for your API responses

7. **Retry Logic**: Enable retry for critical operations
8. **Debouncing**: Use debouncing for search and filter operations

## Example Usage

See `ApiExample.tsx` for a comprehensive example of how to use all the API services, hooks, and utilities together.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your backend has CORS properly configured
2. **Authentication Issues**: Check if the token is being set correctly

4. **Type Errors**: Make sure your TypeScript interfaces match the API response structure

### Debug Mode

Enable debug mode in development:

```typescript
import { isDevelopment } from '../config/environment';

if (isDevelopment()) {
  console.log('API Debug Mode Enabled');
}
``` 