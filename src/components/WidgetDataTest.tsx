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

const WidgetDataTest = () => {
  const [data, setData] = useState<TodayWidgetsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await dashboardService.getTodayWidgets();
        setData(response);
        console.log('Widget data loaded:', response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        console.error('Error fetching widget data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const renderWidgetInfo = (widget: BaseWidget) => {
    return (
      <div key={widget.id} className="border rounded p-4 mb-4">
        <h3 className="font-bold text-lg">{widget.title}</h3>
        <div className="text-sm text-gray-600 mb-2">
          Type: {widget.type} | Size: {widget.size} | Category: {widget.category || 'None'}
        </div>
        
        {isTodoWidget(widget) && (
          <div className="bg-blue-50 p-3 rounded">
            <h4 className="font-semibold">Todo Widget Data:</h4>
            <p>Total Tasks: {widget.data.stats.total_tasks}</p>
            <p>Completed: {widget.data.stats.completed_tasks}</p>
            <p>Pending: {widget.data.stats.pending_tasks}</p>
            <p>Completion Rate: {widget.data.stats.completion_rate.toFixed(1)}%</p>
            <div className="mt-2">
              <h5 className="font-medium">Tasks:</h5>
              {widget.data.tasks.map(task => (
                <div key={task.id} className="ml-4 text-sm">
                  • {task.content} {task.is_done ? '✅' : '⏳'}
                </div>
              ))}
            </div>
          </div>
        )}

        {isHabitTrackerWidget(widget) && (
          <div className="bg-green-50 p-3 rounded">
            <h4 className="font-semibold">Habit Tracker Data:</h4>
            <p>Total Habits: {widget.data.total_habits}</p>
            {widget.data.habits.length > 0 ? (
              <div className="mt-2">
                <h5 className="font-medium">Habits:</h5>
                {widget.data.habits.map(habit => (
                  <div key={habit.id} className="ml-4 text-sm">
                    • {habit.name} (Streak: {habit.streak}) {habit.completed_today ? '✅' : '⏳'}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No habits configured</p>
            )}
          </div>
        )}

        {isWebSearchWidget(widget) && (
          <div className="bg-yellow-50 p-3 rounded">
            <h4 className="font-semibold">Web Search Data:</h4>
            {widget.data.message ? (
              <p>{widget.data.message}</p>
            ) : (
              <div>
                <p>Searches: {widget.data.searches.length}</p>
                {widget.data.searches.map(search => (
                  <div key={search.id} className="ml-4 text-sm">
                    • {search.query}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!isTodoWidget(widget) && !isHabitTrackerWidget(widget) && !isWebSearchWidget(widget) && (
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold">Other Widget Type:</h4>
            <p>Widget type: {widget.type}</p>
            <pre className="text-xs mt-2 bg-white p-2 rounded overflow-auto">
              {JSON.stringify(widget.data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-center mt-2">Loading widget data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-red-600 text-center">
          <p>Error: {error}</p>
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
        <h1 className="text-2xl font-bold mb-2">Widget Data Test</h1>
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

      <div className="space-y-4">
        {data.widgets.map(widget => renderWidgetInfo(widget))}
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

export default WidgetDataTest; 