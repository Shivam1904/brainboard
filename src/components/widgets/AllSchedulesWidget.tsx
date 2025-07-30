import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DashboardWidget, ApiWidgetType } from '../../types';
import { dashboardService } from '../../services/dashboard';
import { getDummyAllSchedulesWidgets } from '../../data/widgetDummyData';
import AddWidgetForm from '../AddWidgetForm';

interface AllSchedulesWidgetProps {
  onRemove: () => void;
}

const AllSchedulesWidget = ({ onRemove }: AllSchedulesWidgetProps) => {
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingWidget, setEditingWidget] = useState<DashboardWidget | null>(null);

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

  // Handle edit widget
  const handleEditWidget = async (widget: DashboardWidget) => {
    try {
      setLoading(true);
      
      // Fetch widget-specific details based on widget type
      let widgetDetails: any = {};
      
      switch (widget.widget_type) {
        case 'todo-habit':
        case 'todo-task':
        case 'todo-event':
          try {
            const todoDetails = await dashboardService.getTodoDetails(widget.id);
            widgetDetails = {
              ...widget,
              todo_type: todoDetails.todo_type,
              due_date: todoDetails.due_date,
              description: todoDetails.description
            };
          } catch (err) {
            console.warn('Failed to fetch todo details, using basic widget data:', err);
            widgetDetails = widget;
          }
          break;
          
        case 'alarm':
          try {
            const alarmDetails = await dashboardService.getAlarmDetails(widget.id);
            widgetDetails = {
              ...widget,
              alarm_times: alarmDetails.alarm_times,
              description: alarmDetails.description,
              target_value: alarmDetails.target_value,
              is_snoozable: alarmDetails.is_snoozable
            };
          } catch (err) {
            console.warn('Failed to fetch alarm details, using basic widget data:', err);
            widgetDetails = widget;
          }
          break;
          
        case 'singleitemtracker':
          try {
            const trackerDetails = await dashboardService.getTrackerDetails(widget.id);
            widgetDetails = {
              ...widget,
              value_type: trackerDetails.value_type,
              value_unit: trackerDetails.value_unit,
              target_value: trackerDetails.target_value
            };
          } catch (err) {
            console.warn('Failed to fetch tracker details, using basic widget data:', err);
            widgetDetails = widget;
          }
          break;
          
        case 'websearch':
          try {
            await dashboardService.getWebSearchDetails(widget.id);
            widgetDetails = {
              ...widget,
              // Websearch details are minimal, just title
            };
          } catch (err) {
            console.warn('Failed to fetch websearch details, using basic widget data:', err);
            widgetDetails = widget;
          }
          break;
          
        default:
          widgetDetails = widget;
          break;
      }
      
      setEditingWidget(widgetDetails);
    } catch (err) {
      console.error('Failed to fetch widget details:', err);
      setError('Failed to load widget details for editing');
    } finally {
      setLoading(false);
    }
  };

  // Handle form close
  const handleFormClose = () => {
    setEditingWidget(null);
  };

  // Handle form success (refresh widget list)
  const handleFormSuccess = async () => {
    try {
      const response = await dashboardService.getAllWidgets();
      setWidgets(response.widgets);
    } catch (err) {
      console.error('Failed to refresh widgets after edit:', err);
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
                    <div className="flex items-center">
                      <span className="text-sm font-medium truncate">{widget.title}</span>

                    </div>
                    
                    <div className="flex flex-row text-xs text-muted-foreground">
                      <div className="flex flex-col items-center">
                        <div>Frequency: {getFrequencyDisplayName(widget.frequency)}</div>
                        <div>Importance: {widget.importance}/1.0</div>
                        <div>Created: {new Date(widget.created_at).toLocaleDateString()}</div>
                      </div>
                      <div className="flex flex-col items-center">
                      </div>
                      <div className="flex flex-col items-center">
                        <span className={`text-xs rounded `}>
                          {getWidgetTypeDisplayName(widget.widget_type as ApiWidgetType)}
                        </span>
                        {widget.category && (
                          <span className={`text-xs rounded text-muted-foreground ${getCategoryColor((widget.category).toLowerCase())}`}>
                            {widget.category}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Edit button */}
                  <button
                    onClick={() => handleEditWidget(widget)}
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

      {/* Edit Widget Form Modal */}
      {editingWidget && (
        <AddWidgetForm
          widgetId={editingWidget.widget_type}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
          editMode={true}
          existingWidget={editingWidget}
        />
      )}
    </BaseWidget>
  );
};

export default AllSchedulesWidget; 