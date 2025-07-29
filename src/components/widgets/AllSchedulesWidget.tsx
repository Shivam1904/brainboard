import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DashboardWidget, ApiWidgetType, ApiCategory, ApiFrequency } from '../../types';
import { dashboardService } from '../../services/dashboard';
import { getDummyAllSchedulesWidgets } from '../../data/widgetDummyData';

interface AllSchedulesWidgetProps {
  onRemove: () => void;
  widget: any; // Using the UIWidget type from Dashboard
}

const AllSchedulesWidget = ({ onRemove, widget }: AllSchedulesWidgetProps) => {
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load widgets from API using getAllWidgetList
  useEffect(() => {
    const loadWidgets = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await dashboardService.getAllWidgets();
        console.log('All widgets response:', response);
        
        // If no widgets from API, use dummy data
        if (response.widgets.length === 0) {
          console.log('No widgets found, using dummy data');
          const dummyWidgets = getDummyAllSchedulesWidgets();
          setWidgets(dummyWidgets as any);
        } else {
          setWidgets(response.widgets);
        }
      } catch (err) {
        console.error('Failed to load widgets:', err);
        setError('Failed to load widget schedules');
        // Use dummy data on error
        const dummyWidgets = getDummyAllSchedulesWidgets();
        setWidgets(dummyWidgets as any);
      } finally {
        setLoading(false);
      }
    };

    loadWidgets();
  }, []);

  // Update widget details
  const updateWidgetDetails = async (widgetId: string, updateData: {
    title?: string;
    frequency?: ApiFrequency;
    importance?: number;
    category?: ApiCategory;
  }) => {
    try {
      // Call the updateDetails API endpoint
      const response = await dashboardService.updateWidgetDetails(widgetId, updateData);
      console.log('Widget updated:', response);
      
      // Refresh the widget list
      const refreshResponse = await dashboardService.getAllWidgets();
      setWidgets(refreshResponse.widgets);
    } catch (err) {
      console.error('Failed to update widget:', err);
      setError('Failed to update widget');
    }
  };

  // Get widget type display name
  const getWidgetTypeDisplayName = (type: ApiWidgetType): string => {
    const typeNames: Record<ApiWidgetType, string> = {
      'todo-habit': 'Habit Tracker',
      'todo-task': 'Task List',
      'todo-event': 'Event Tracker',
      'alarm': 'Alarm',
      'singleitemtracker': 'Item Tracker',
      'websearch': 'Web Search'
    };
    return typeNames[type] || type;
  };

  // Get category color
  const getCategoryColor = (category?: string | null): string => {
    const colors: Record<string, string> = {
      'health': 'bg-red-100 text-red-800',
      'productivity': 'bg-blue-100 text-blue-800',
      'job': 'bg-green-100 text-green-800',
      'information': 'bg-purple-100 text-purple-800',
      'entertainment': 'bg-yellow-100 text-yellow-800',
      'utilities': 'bg-gray-100 text-gray-800'
    };
    return colors[category || ''] || 'bg-gray-100 text-gray-800';
  };

  // Get frequency display name
  const getFrequencyDisplayName = (frequency: string): string => {
    const frequencyNames: Record<string, string> = {
      'daily': 'Daily',
      'weekly': 'Weekly',
      'monthly': 'Monthly'
    };
    return frequencyNames[frequency] || frequency;
  };

  if (loading) {
    return (
      <BaseWidget title="All Widgets" icon="⚙️" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading widgets...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="All Widgets" icon="⚙️" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-destructive mb-2">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title={`Widget Schedules (${widgets.length})`} icon="⚙️" onRemove={onRemove}>
      <div className="h-full flex flex-col">

        {/* Widget list */}
        <div className="flex-1 overflow-y-auto space-y-2">
          {widgets.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No widgets found</p>
              <p className="text-sm">Widgets will appear here when added to your dashboard</p>
            </div>
          ) : (
            widgets.map((widget) => (
              <div
                key={widget.id}
                className="bg-card/50 border border-border rounded-lg p-3 hover:bg-card/70 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium truncate">{widget.title}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getCategoryColor(widget.category)}`}>
                        {getWidgetTypeDisplayName(widget.widget_type as ApiWidgetType)}
                      </span>
                      {widget.category && (
                        <span className="text-xs text-muted-foreground">
                          {widget.category}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div>Frequency: {getFrequencyDisplayName(widget.frequency)}</div>
                      <div>Importance: {widget.importance}/1.0</div>
                      <div>Created: {new Date(widget.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                  
                  {/* Edit button */}
                  <button
                    onClick={() => {
                      // For now, just log the widget ID for editing
                      console.log('Edit widget:', widget.id);
                      // TODO: Implement edit modal/form
                    }}
                    className="text-xs px-2 py-1 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
                  >
                    Edit
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </BaseWidget>
  );
};

export default AllSchedulesWidget; 