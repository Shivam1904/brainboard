import { useState, useEffect } from 'react';
import { 
  TodayWidgetsResponse, 
  BaseWidget, 
  TodoWidgetData, 
  HabitTrackerWidgetData,
  WebSearchWidgetData,
  isTodoWidget,
  isHabitTrackerWidget,
  isWebSearchWidget
} from '../types';
import { dashboardService } from '../services/api';

const DashboardApiTest = () => {
  const [data, setData] = useState<TodayWidgetsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTodayWidgets();
  }, []);

  const fetchTodayWidgets = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardService.getTodayWidgets();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const renderTodoWidget = (widget: BaseWidget & { data: TodoWidgetData }) => {
    return (
      <div key={widget.id} className="border rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2">{widget.title}</h3>
        <div className="text-sm text-gray-600 mb-2">
          Category: {widget.category || 'None'} | Importance: {widget.importance || 'None'}
        </div>
        <div className="mb-4">
          <div className="flex justify-between text-sm">
            <span>Total: {widget.data.stats.total_tasks}</span>
            <span>Completed: {widget.data.stats.completed_tasks}</span>
            <span>Pending: {widget.data.stats.pending_tasks}</span>
            <span>Rate: {widget.data.stats.completion_rate.toFixed(1)}%</span>
          </div>
        </div>
        <div className="space-y-2">
          {widget.data.tasks.map(task => (
            <div key={task.id} className="flex items-center gap-2">
              <input 
                type="checkbox" 
                checked={task.is_done}
                readOnly
                className="rounded"
              />
              <span className={task.is_done ? 'line-through text-gray-500' : ''}>
                {task.content}
              </span>
              {task.due_date && (
                <span className="text-xs text-gray-400">
                  Due: {new Date(task.due_date).toLocaleDateString()}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderHabitTrackerWidget = (widget: BaseWidget & { data: HabitTrackerWidgetData }) => {
    return (
      <div key={widget.id} className="border rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2">{widget.title}</h3>
        <div className="text-sm text-gray-600 mb-2">
          Category: {widget.category || 'None'} | Importance: {widget.importance || 'None'}
        </div>
        <div className="mb-4">
          <div className="text-sm">
            Total Habits: {widget.data.total_habits}
          </div>
        </div>
        {widget.data.habits.length > 0 ? (
          <div className="space-y-2">
            {widget.data.habits.map(habit => (
              <div key={habit.id} className="flex items-center justify-between">
                <div>
                  <span className="font-medium">{habit.name}</span>
                  {habit.description && (
                    <p className="text-sm text-gray-600">{habit.description}</p>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm">Streak: {habit.streak}</div>
                  <div className={`text-xs ${habit.completed_today ? 'text-green-600' : 'text-gray-400'}`}>
                    {habit.completed_today ? 'Completed Today' : 'Not Done Today'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No habits configured</p>
        )}
      </div>
    );
  };

  const renderWebSearchWidget = (widget: BaseWidget & { data: WebSearchWidgetData }) => {
    return (
      <div key={widget.id} className="border rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2">{widget.title}</h3>
        <div className="text-sm text-gray-600 mb-2">
          Category: {widget.category || 'None'} | Importance: {widget.importance || 'None'}
        </div>
        {widget.data.message ? (
          <p className="text-gray-500 text-sm">{widget.data.message}</p>
        ) : (
          <div className="space-y-2">
            {widget.data.searches.map(search => (
              <div key={search.id} className="border-l-2 border-blue-500 pl-3">
                <div className="font-medium">{search.query}</div>
                {search.last_searched && (
                  <div className="text-xs text-gray-400">
                    Last searched: {new Date(search.last_searched).toLocaleString()}
                  </div>
                )}
                {search.results && search.results.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {search.results.slice(0, 3).map((result, index) => (
                      <div key={index} className="text-sm">
                        <div className="font-medium">{result.title}</div>
                        <div className="text-gray-600">{result.snippet}</div>
                        <div className="text-blue-600 text-xs">{result.url}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderWidget = (widget: BaseWidget) => {
    // Use type guards to safely render different widget types
    if (isTodoWidget(widget)) {
      return renderTodoWidget(widget);
    }
    
    if (isHabitTrackerWidget(widget)) {
      return renderHabitTrackerWidget(widget);
    }
    
    if (isWebSearchWidget(widget)) {
      return renderWebSearchWidget(widget);
    }
    
    // Fallback for unknown widget types
    return (
      <div key={widget.id} className="border rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2">{widget.title}</h3>
        <div className="text-sm text-gray-600 mb-2">
          Type: {widget.type} | Category: {widget.category || 'None'} | Importance: {widget.importance || 'None'}
        </div>
        <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
          {JSON.stringify(widget.data, null, 2)}
        </pre>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-center mt-2">Loading today's widgets...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-red-600 text-center">
          <p>Error: {error}</p>
          <button 
            onClick={fetchTodayWidgets}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-4">
        <p className="text-center text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Today's Dashboard</h1>
        <p className="text-gray-600">Date: {data.date}</p>
        <div className="mt-2 text-sm text-gray-500">
          <span>Total Widgets: {data.stats.total_widgets}</span>
          <span className="mx-2">|</span>
          <span>Daily: {data.stats.daily_count}</span>
          <span className="mx-2">|</span>
          <span>Weekly: {data.stats.weekly_count}</span>
          <span className="mx-2">|</span>
          <span>Monthly: {data.stats.monthly_count}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.widgets.map(widget => renderWidget(widget))}
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Raw API Response</h2>
        <pre className="text-xs overflow-auto max-h-96">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default DashboardApiTest; 