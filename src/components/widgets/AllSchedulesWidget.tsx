import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { BaseWidget as WidgetData, WidgetType } from '../../types';
import { dashboardService } from '../../services/api';
import { Widget } from '../../utils/dashboardUtils';
import { getDummyAllSchedulesWidgets } from '../../data/widgetDummyData';

interface AllSchedulesWidgetProps {
  onRemove: () => void;
  widget: Widget
}

const AllSchedulesWidget = ({ onRemove, widget }: AllSchedulesWidgetProps) => {
  const [widgets, setWidgets] = useState<WidgetData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load widgets from API
  useEffect(() => {
    const loadWidgets = async () => {
      try {
        setLoading(true);
        const response = await dashboardService.getTodayWidgets();
        
        // If no widgets from API, use dummy data
        if (response.widgets.length === 0) {
          const dummyWidgets = getDummyAllSchedulesWidgets();
          setWidgets(dummyWidgets as any);
        } else {
          setWidgets(response.widgets as any);
        }
      } catch (err) {
        console.error('Failed to load widgets:', err);
        // Use dummy data on error
        const dummyWidgets = getDummyAllSchedulesWidgets();
        setWidgets(dummyWidgets as any);
      } finally {
        setLoading(false);
      }
    };

    loadWidgets();
  }, []);

  // Get widget type display name
  const getWidgetTypeDisplayName = (type: WidgetType): string => {
    const typeNames: Record<string, string> = {
      'todo': 'Todo',
      'habittracker': 'Habit Tracker',
      'websearch': 'Web Search',
      'websummary': 'Web Summary',
      'calendar': 'Calendar',
      'reminder': 'Reminder',
      'allSchedules': 'All Schedules'
    };
    return typeNames[type] || type;
  };

  // Get category color
  const getCategoryColor = (category?: string | null): string => {
    const colors: Record<string, string> = {
      'health': 'bg-red-100 text-red-800',
      'self-imp': 'bg-blue-100 text-blue-800',
      'finance': 'bg-green-100 text-green-800',
      'awareness': 'bg-purple-100 text-purple-800'
    };
    return colors[category || ''] || 'bg-gray-100 text-gray-800';
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
                        {getWidgetTypeDisplayName(widget.type)}
                      </span>
                      {widget.category && (
                        <span className="text-xs text-muted-foreground">
                          {widget.category}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-xs text-muted-foreground space-y-1">
                      Frequency: {widget.frequency} Size: {widget.size} Importance: {widget.importance}/5
                    </div>
                  </div>
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