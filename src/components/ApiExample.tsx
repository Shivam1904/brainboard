import React, { useState, useEffect } from 'react';
import { useApi, useApiPost, useApiPut, useApiDelete } from '../hooks/useApi';
import { authService, reminderService, summaryService } from '../services/api';
import { websocketService, subscribeToReminders } from '../services/websocket';
import { retryApiCall, debounce } from '../utils/apiUtils';
import { API_ENDPOINTS, ERROR_MESSAGES } from '../config/environment';

interface Reminder {
  id: string;
  title: string;
  description: string;
  due_date: string;
  completed: boolean;
}

interface Summary {
  id: string;
  title: string;
  content: string;
  created_at: string;
}

const ApiExample: React.FC = () => {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [newReminder, setNewReminder] = useState({ title: '', description: '', due_date: '' });

  // Example: Using the useApi hook to fetch reminders
  const { data: reminders, loading: remindersLoading, error: remindersError, refetch: refetchReminders } = useApi<Reminder[]>(
    '/api/reminders',
    {
      cache: true,
      cacheKey: 'reminders',
      retry: true,
      retryAttempts: 3,
      onSuccess: (data) => console.log('Reminders loaded:', data),
      onError: (error) => console.error('Failed to load reminders:', error)
    }
  );

  // Example: Using the useApiPost hook to create reminders
  const { post: createReminder, loading: createLoading, error: createError } = useApiPost<Reminder>(
    '/api/reminders',
    {
      onSuccess: (data) => {
        console.log('Reminder created:', data);
        refetchReminders(); // Refresh the list
        setNewReminder({ title: '', description: '', due_date: '' });
      },
      onError: (error) => console.error('Failed to create reminder:', error)
    }
  );

  // Example: Using the useApiPut hook to update reminders
  const { put: updateReminder, loading: updateLoading } = useApiPut<Reminder, Partial<Reminder>>(
    '/api/reminders',
    {
      onSuccess: (data) => {
        console.log('Reminder updated:', data);
        refetchReminders();
      }
    }
  );

  // Example: Using the useApiDelete hook to delete reminders
  const { delete: deleteReminder, loading: deleteLoading } = useApiDelete(
    '/api/reminders',
    {
      onSuccess: () => {
        console.log('Reminder deleted');
        refetchReminders();
      }
    }
  );

  // Example: Authentication
  const handleLogin = async () => {
    try {
      const response = await authService.login({
        email: 'user@example.com',
        password: 'password123'
      });
      setAuthToken(response.access_token);
      console.log('Logged in successfully');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setAuthToken(null);
      console.log('Logged out successfully');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Example: WebSocket subscription
  useEffect(() => {
    const handleReminderUpdate = (data: any) => {
      console.log('Real-time reminder update:', data);
      refetchReminders(); // Refresh data when we get real-time updates
    };

    // Subscribe to real-time reminder updates
    subscribeToReminders(handleReminderUpdate);

    // Cleanup subscription on unmount
    return () => {
      // Note: In a real app, you'd want to implement proper cleanup
      console.log('Cleaned up WebSocket subscription');
    };
  }, [refetchReminders]);

  // Example: Debounced search
  const debouncedSearch = debounce((searchTerm: string) => {
    console.log('Searching for:', searchTerm);
    // You could call an API here with the search term
  }, 500);

  // Example: Retry mechanism
  const handleRetryOperation = async () => {
    try {
      const result = await retryApiCall(
        () => reminderService.getReminders(),
        3,
        1000
      );
      console.log('Retry operation successful:', result);
    } catch (error) {
      console.error('Retry operation failed:', error);
    }
  };

  const handleCreateReminder = async () => {
    if (!newReminder.title.trim()) return;
    
    await createReminder(newReminder);
  };

  const handleToggleReminder = async (reminder: Reminder) => {
    await updateReminder({
      ...reminder,
      completed: !reminder.completed
    });
  };

  const handleDeleteReminder = async (id: string) => {
    await deleteReminder();
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">API Service Examples</h1>
      
      {/* Authentication Section */}
      <div className="mb-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Authentication</h2>
        <div className="flex gap-4">
          <button
            onClick={handleLogin}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Login
          </button>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
        {authToken && (
          <p className="mt-2 text-sm text-green-600">✓ Authenticated</p>
        )}
      </div>

      {/* Create Reminder Section */}
      <div className="mb-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Create Reminder</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Title"
            value={newReminder.title}
            onChange={(e) => setNewReminder(prev => ({ ...prev, title: e.target.value }))}
            className="w-full p-2 border rounded"
          />
          <input
            type="text"
            placeholder="Description"
            value={newReminder.description}
            onChange={(e) => setNewReminder(prev => ({ ...prev, description: e.target.value }))}
            className="w-full p-2 border rounded"
          />
          <input
            type="date"
            value={newReminder.due_date}
            onChange={(e) => setNewReminder(prev => ({ ...prev, due_date: e.target.value }))}
            className="w-full p-2 border rounded"
          />
          <button
            onClick={handleCreateReminder}
            disabled={createLoading}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            {createLoading ? 'Creating...' : 'Create Reminder'}
          </button>
          {createError && (
            <p className="text-red-600">{createError.message}</p>
          )}
        </div>
      </div>

      {/* Reminders List Section */}
      <div className="mb-8 p-4 border rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Reminders</h2>
          <div className="flex gap-2">
            <button
              onClick={refetchReminders}
              disabled={remindersLoading}
              className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50"
            >
              {remindersLoading ? 'Loading...' : 'Refresh'}
            </button>
            <button
              onClick={handleRetryOperation}
              className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              Test Retry
            </button>
          </div>
        </div>

        {remindersLoading && <p>Loading reminders...</p>}
        {remindersError && (
          <p className="text-red-600">Error: {remindersError.message}</p>
        )}
        
        {reminders && reminders.length > 0 ? (
          <div className="space-y-2">
            {reminders.map((reminder) => (
              <div key={reminder.id} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={reminder.completed}
                    onChange={() => handleToggleReminder(reminder)}
                    disabled={updateLoading}
                  />
                  <div>
                    <h3 className={`font-medium ${reminder.completed ? 'line-through text-gray-500' : ''}`}>
                      {reminder.title}
                    </h3>
                    <p className="text-sm text-gray-600">{reminder.description}</p>
                    <p className="text-xs text-gray-400">Due: {new Date(reminder.due_date).toLocaleDateString()}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteReminder(reminder.id)}
                  disabled={deleteLoading}
                  className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No reminders found</p>
        )}
      </div>

      {/* WebSocket Status */}
      <div className="mb-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">WebSocket Status</h2>
        <p className="text-sm">
          Status: {websocketService.isConnected() ? 'Connected' : 'Disconnected'}
        </p>
        <p className="text-sm text-gray-600">
          Real-time updates are {websocketService.isConnected() ? 'enabled' : 'disabled'}
        </p>
      </div>

      {/* Search Example */}
      <div className="mb-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Debounced Search</h2>
        <input
          type="text"
          placeholder="Search reminders..."
          onChange={(e) => debouncedSearch(e.target.value)}
          className="w-full p-2 border rounded"
        />
        <p className="text-sm text-gray-600 mt-2">
          This search is debounced (500ms delay) to avoid excessive API calls
        </p>
      </div>
    </div>
  );
};

export default ApiExample; 