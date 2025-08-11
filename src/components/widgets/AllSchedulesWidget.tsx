import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DashboardWidget, DailyWidget } from '../../services/api';
import { dashboardService } from '../../services/dashboard';

import AddWidgetForm from '../AddWidgetForm';
import { createPortal } from 'react-dom';

interface AllSchedulesWidgetProps {
  widget: DailyWidget;
  onRemove: () => void;
  onWidgetAddedToToday: (widget: DashboardWidget) => void;
  onHeightChange: (dailyWidgetId: string, newHeight: number) => void;
  targetDate: string;
}

interface GroupedWidgets {
  [key: string]: DashboardWidget[];
}

const AllSchedulesWidget = ({ widget, onRemove, onWidgetAddedToToday, onHeightChange, targetDate }: AllSchedulesWidgetProps) => {
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingWidget, setEditingWidget] = useState<DashboardWidget | null>(null);
  const [todayWidgetIds, setTodayWidgetIds] = useState<string[]>([]);
  const [addingToToday, setAddingToToday] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Helper function to extract today widget IDs from API response
  const extractTodayWidgetIds = (todayWidgetsResponse: any[]): string[] => {
    let todayIds: string[] = [];
    if (Array.isArray(todayWidgetsResponse)) {
      todayWidgetsResponse.forEach((dailyWidget: any) => {
        if (dailyWidget.widget_id) {
          todayIds.push(dailyWidget.widget_id);
        }
      });
    }
    return todayIds;
  };

  // Load widgets from API using getAllWidgets
  useEffect(() => {
    const loadWidgets = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Load all widgets and today's widgets in parallel
        const [allWidgetsResponse, todayWidgetsResponse] = await Promise.all([
          dashboardService.getAllWidgets(),
          dashboardService.getTodayWidgets(targetDate)
        ]);
        
        console.log('All widgets response:', allWidgetsResponse);
        
        // Extract widget IDs that are already in today's dashboard
        const todayIds = extractTodayWidgetIds(todayWidgetsResponse);
        setTodayWidgetIds(todayIds);
        console.log('Today widgets ids:', todayIds);
        console.log('Today widgets response:', todayWidgetsResponse);
        
        setWidgets(allWidgetsResponse);
      } catch (err) {
        console.error('Failed to load widgets:', err);
        setError('Failed to load widget schedules');
        setWidgets([]);
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
      const widgetDetails = await dashboardService.getWidget(widget.id);      
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
      setWidgets(response);
    } catch (err) {
      console.error('Failed to refresh widgets after edit:', err);
    }
  };

  // Handle add to today
  const handleAddToToday = async (widget: DashboardWidget, targetDate: string) => {
    try {
      setAddingToToday(widget.id);
      
      const response = await dashboardService.addWidgetToToday(widget.id, targetDate);
      console.log('Widget added to today:', response);
      
      // Refresh today's widgets to update the list
      const todayWidgetsResponse = await dashboardService.getTodayWidgets(targetDate);
      const todayIds = extractTodayWidgetIds(todayWidgetsResponse);
      setTodayWidgetIds(todayIds);
      
      // Show success message
      // alert(`${widget.title} has been added to today's dashboard!`);
      onWidgetAddedToToday(widget);
      
    } catch (err) {
      console.error('Failed to add widget to today:', err);
      if (err instanceof Error) {
        alert(`Failed to add widget to today: ${err.message}`);
      } else {
        alert('Failed to add widget to today');
      }
    } finally {
      setAddingToToday(null);
    }
  };

  

  // Get widget type icon
  const getWidgetTypeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      'todo-habit': '🔄',
      'todo-task': '📋',
      'todo-event': '📅',
      'alarm': '⏰',
      'single_item_tracker': '📊',
      'websearch': '🔍',
      'aiChat': '🤖',
      'allSchedules': '⚙️',
      'moodTracker': '😊',
      'weatherWidget': '⛅️',
      'simpleClock': '🕒'
    };
    return icons[type] || '⚙️';
  };

  // Get category color
  const getCategoryColor = (category?: string | null): string => {
    const colors: Record<string, string> = {
      'health': 'bg-red-50 text-red-700 border-red-200',
      'productivity': 'bg-blue-50 text-blue-700 border-blue-200',
      'job': 'bg-green-50 text-green-700 border-green-200',
      'information': 'bg-purple-50 text-purple-700 border-purple-200',
      'entertainment': 'bg-yellow-50 text-yellow-700 border-yellow-200',
      'utilities': 'bg-gray-50 text-gray-700 border-gray-200'
    };
    return colors[category?.toLowerCase() || ''] || 'bg-gray-50 text-gray-700 border-gray-200';
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

  // Group widgets into Trackers and Missions, excluding specific types
  const groupedWidgets = widgets.reduce((groups: GroupedWidgets, widget) => {
    const type = widget.widget_type;
    const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar']);
    const excludedTypes = new Set(['aiChat', 'moodTracker', 'weatherWidget', 'simpleClock', 'allSchedules']);

    // Skip excluded types
    if (excludedTypes.has(type)) {
      return groups;
    }

    const groupName = trackerTypes.has(type) ? 'trackers' : 'missions';
    if (!groups[groupName]) {
      groups[groupName] = [];
    }
    groups[groupName].push(widget);
    return groups;
  }, {} as GroupedWidgets);

  // Toggle group expansion
  const toggleGroup = (groupName: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupName)) {
      newExpanded.delete(groupName);
    } else {
      newExpanded.add(groupName);
    }
    setExpandedGroups(newExpanded);
    // set number of total items in the list = total groups + sum of items in expanded groups only
    const expandedItemsCount = Object.entries(groupedWidgets)
      .reduce((sum, [name, group]) => sum + (newExpanded.has(name) ? group.length : 0), 0);
    const totalItems = Object.keys(groupedWidgets).length + expandedItemsCount;
    onHeightChange(widget.id, totalItems * 2 + 2);
  };

  if (loading) {
    return (
      <BaseWidget title="All Widgets" icon="⚙️" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-muted-foreground text-sm">Loading widgets...</p>
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
            <p className="text-destructive mb-2 text-sm">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1.5 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title={`Widget Library (${widgets.length})`} icon="📚" onRemove={onRemove} >
      <div className="h-full flex flex-col">
        <div className="flex mt-2"><h4>Widget Library</h4></div>
        {/* Widget groups */}
        <div className="flex-1 overflow-y-auto space-y-3">
          {Object.keys(groupedWidgets).length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <div className="text-4xl mb-2">📚</div>
              <p className="text-sm font-medium">No widgets found</p>
              <p className="text-xs text-muted-foreground mt-1">Widgets will appear here when added to your dashboard</p>
            </div>
          ) : (
            Object.entries(groupedWidgets).map(([groupName, groupWidgets]) => {
              const isExpanded = expandedGroups.has(groupName);
              const widgetType = groupWidgets[0]?.widget_type;
              const icon = getWidgetTypeIcon(widgetType);
              
              return (
                <div key={groupName} className="bg-card/30 border border-border/50 rounded-lg overflow-hidden">
                  {/* Group header */}
                  <button
                    onClick={() => toggleGroup(groupName)}
                    className="w-full px-4 py-3 bg-gradient-to-r from-primary/10 to-primary/5 flex items-center justify-between "
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{icon}</span>
                      <div className="text-left">
                        <h3 className="font-medium text-sm">{groupName}</h3>
                        <p className="text-xs text-muted-foreground">{groupWidgets.length} widget{groupWidgets.length !== 1 ? 's' : ''}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-muted-foreground">
                        {groupWidgets.filter(w => todayWidgetIds.includes(w.id)).length} in today
                      </span>
                      <svg
                        className={`w-4 h-4 text-muted-foreground transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </button>

                  {/* Group content */}
                  {isExpanded && (
                    <div className="border-t border-border/50 bg-card/20">
                      <div className="p-3 space-y-2">
                        {groupWidgets.map((widget) => (
                          <div
                            key={widget.id}
                            className="bg-background/80 border border-border/30 rounded-md p-3 hover:bg-background transition-all duration-200 hover:shadow-sm"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-1">
                                  <h4 className="font-medium text-sm truncate">{widget.title}</h4>
                                  {widget.category && (
                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getCategoryColor(widget.category)}`}>
                                      {widget.category}
                                    </span>
                                  )}
                                </div>
                                
                                <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                                  <span className="flex items-center space-x-1">
                                    <span className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></span>
                                    <span>{getFrequencyDisplayName(widget.frequency)}</span>
                                  </span>
                                  {todayWidgetIds.includes(widget.id) && (
                                    <span className="flex items-center space-x-1 text-blue-600">
                                      <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                                      <span>In Today</span>
                                    </span>
                                  )}
                                </div>
                              </div>
                              
                              {/* Action buttons */}
                              <div className="flex items-center space-x-1 ml-3">
                                <button
                                  onClick={() => handleEditWidget(widget)}
                                  className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded transition-colors"
                                  title="Edit widget"
                                >
                                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                  </svg>
                                </button>
                                
                                {!todayWidgetIds.includes(widget.id) && (
                                  <button
                                    onClick={() => handleAddToToday(widget, targetDate)}
                                    disabled={addingToToday === widget.id}
                                    className={`p-1.5 rounded transition-colors ${
                                      addingToToday === widget.id
                                        ? 'text-muted-foreground cursor-not-allowed'
                                        : 'text-green-600 hover:text-green-700 hover:bg-green-50'
                                    }`}
                                    title="Add to this day"
                                  >
                                    {addingToToday === widget.id ? (
                                      <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-current"></div>
                                    ) : (
                                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                      </svg>
                                    )}
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Edit Widget Form Modal */}
      {editingWidget && createPortal(
        <AddWidgetForm
          widgetId={editingWidget.widget_type}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
          editMode={true}
          existingWidget={editingWidget}
        />
      , document.body)}
    </BaseWidget>
  );
};

export default AllSchedulesWidget; 
