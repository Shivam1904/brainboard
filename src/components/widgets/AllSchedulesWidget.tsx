import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DashboardWidget, DailyWidget } from '../../services/api';
import { useAllWidgetsData, useTodayWidgetsData } from '../../hooks/useDashboardData';

import AddWidgetForm from '../AddWidgetForm';
import { createPortal } from 'react-dom';
import { dashboardService } from '@/services/dashboard';
import { Check, Pen, Plus } from 'lucide-react';
import { categoryColors } from './CalendarWidget';

interface AllSchedulesWidgetProps {
  widget: DailyWidget;
  onRemove: () => void;
  onWidgetAddedToToday: (widget: DashboardWidget) => void;
  onHeightChange: (dailyWidgetId: string, newHeight: number) => void;
  onRefresh?: () => void;
  targetDate: string;
}

interface GroupedWidgets {
  [key: string]: DashboardWidget[];
}

const AllSchedulesWidget = ({ widget, onRemove, onWidgetAddedToToday, onHeightChange, onRefresh, targetDate }: AllSchedulesWidgetProps) => {
  const { allWidgets: widgets, isLoading, error } = useAllWidgetsData()
  const { todayWidgets } = useTodayWidgetsData(targetDate)
  const [editingWidget, setEditingWidget] = useState<DashboardWidget | null>(null);
  const [todayWidgetIds, setTodayWidgetIds] = useState<string[]>([]);
  const [addingToToday, setAddingToToday] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['missions']));

  const getCategoryColor = (category: string) => {
    category = category.toLowerCase();
    if (!category || !categoryColors[category as keyof typeof categoryColors]) {
      return 'gray';
    }
    return categoryColors[category as keyof typeof categoryColors].color;
  };

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

  // Extract today widget IDs when todayWidgets changes
  useEffect(() => {
    const todayIds = extractTodayWidgetIds(todayWidgets);
    setTodayWidgetIds(todayIds);
  }, [todayWidgets]);

  // Handle edit widget
  const handleEditWidget = async (widget: DashboardWidget) => {
    try {
      // Fetch widget-specific details based on widget type
      const widgetDetails = await dashboardService.getWidget(widget.id);
      setEditingWidget(widgetDetails);
    } catch (err) {
      console.error('Failed to fetch widget details:', err);
    }
  };

  // Handle form close
  const handleFormClose = () => {
    setEditingWidget(null);
  };

  // Handle form success (refresh widget list)
  const handleFormSuccess = async () => {
    setEditingWidget(null);
    if (onRefresh) onRefresh();
  };

  // Handle add to today
  const handleAddToToday = async (widget: DashboardWidget, targetDate: string) => {
    try {
      setAddingToToday(widget.id);

      // Use the centralized state management
      await onWidgetAddedToToday(widget);

      // Notify parent to refresh if needed
      if (onRefresh) onRefresh();

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


  // Group widgets into Trackers and Missions, excluding specific types
  const groupedWidgets = widgets.reduce((groups: GroupedWidgets, widget) => {
    const type = widget.widget_type;
    const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);
    const excludedTypes = new Set(['aiChat', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock', 'allSchedules']);

    if (excludedTypes.has(type)) return groups;

    const groupName = trackerTypes.has(type) ? 'trackers' : 'missions';
    if (!groups[groupName]) groups[groupName] = [];
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

    // Adjust height for parent
    const expandedItemsCount = Object.entries(groupedWidgets)
      .reduce((sum, [name, group]) => sum + (newExpanded.has(name) ? group.length : 0), 0);
    const totalItems = Object.keys(groupedWidgets).length + expandedItemsCount;
    onHeightChange(widget.daily_widget_id || widget.id, totalItems * 5 + 10);
  };

  if (isLoading) {
    return (
      <BaseWidget title="Widget Library" icon="📚" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-full p-8 space-y-4">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-primary">BW</div>
          </div>
          <p className="text-muted-foreground text-sm font-medium animate-pulse">Syncing Library...</p>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="Widget Library" icon="📚" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
          <div className="text-4xl mb-4">🩹</div>
          <p className="text-destructive font-medium mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all font-medium text-sm"
          >
            Try Again
          </button>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title="Library" icon="📦" onRemove={onRemove}>
      <div className="h-full flex flex-col pt-2 ">
        {/* Widget groups */}
        <div className="flex-1 overflow-y-auto space-y-4 px-1 pb-4 custom-scrollbar">
          {Object.keys(groupedWidgets).length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center opacity-40">
              <div className="text-6xl mb-4">📭</div>
              <p className="text-sm font-bold uppercase tracking-widest">Library Empty</p>
              <p className="text-xs mt-1">Add widgets to see them here</p>
            </div>
          ) : (
            Object.entries(groupedWidgets).map(([groupName, groupWidgets]) => {
              const isExpanded = expandedGroups.has(groupName);
              const groupIcon = groupName === 'missions' ? '🎯' : '📊';
              const isInTodayCount = groupWidgets.filter(w => todayWidgetIds.includes(w.id)).length;

              return (
                <div key={groupName} className="group/section border border-border/40 rounded-2xl overflow-hidden bg-card/40 backdrop-blur-md shadow-sm transition-all duration-300 hover:border-primary/20">
                  {/* Group header */}
                  <button
                    onClick={() => toggleGroup(groupName)}
                    className={`w-full px-4 py-4 flex items-center justify-between transition-colors ${isExpanded ? 'bg-gradient-to-r from-primary/10 via-transparent to-transparent' : 'hover:bg-muted/30'
                      }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl shadow-inner ${isExpanded ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'
                        }`}>
                        {groupIcon}
                      </div>
                      <div className="text-left">
                        <h3 className="font-bold text-sm capitalize tracking-tight text-foreground/80">{groupName}</h3>
                        <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-tighter">
                          {groupWidgets.length} items
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="hidden sm:flex flex-col items-end">
                        <span className="text-[10px] font-bold text-primary/80 uppercase tracking-tighter">
                          {isInTodayCount} ACTIVE
                        </span>
                        <div className="w-16 h-1 bg-muted rounded-full mt-1 overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all duration-500"
                            style={{ width: `${(isInTodayCount / groupWidgets.length) * 100}%` }}
                          />
                        </div>
                      </div>
                      <svg
                        className={`w-5 h-5 text-muted-foreground/60 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </button>

                  {/* Group content */}
                  {isExpanded && (
                    <div className="px-3 pb-3 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                      {groupWidgets.map((widget) => {
                        const isAdded = todayWidgetIds.includes(widget.id);
                        return (
                          <div
                            key={widget.id}
                            className={`fp-2 ${isAdded
                              ? 'font-bold'
                              : 'font-normal'
                              }`}
                          >
                            <div className="flex lex flex-row justify-between ">

                              <span className={`text-xs }`}>
                                {widget.title}
                              </span>
                              <div className="flex items-center gap-2">

                                {widget.category && (
                                  <span className={`px-1.5 py-0.5 rounded-full text-xs font-medium text-${getCategoryColor(widget.category)}-800 bg-${getCategoryColor(widget.category)}-100`}>
                                    {widget.category}
                                  </span>
                                )}
                                <button
                                  onClick={() => handleEditWidget(widget)}
                                  className="px-2 text-muted-foreground/60 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                                  title="Edit baseline"
                                >
                                  <Pen className='w-3 h-3' />
                                </button>

                                <button
                                  onClick={() => handleAddToToday(widget, targetDate)}
                                  disabled={addingToToday === widget.id || isAdded}
                                  className={`px-2 rounded-lg transition-all ${isAdded
                                    ? 'text-primary bg-primary/10'
                                    : addingToToday === widget.id
                                      ? 'text-muted-foreground animate-pulse'
                                      : 'text-emerald-500 hover:bg-emerald-500/10 hover:shadow-inner'
                                    }`}
                                  title={isAdded ? 'Already active today' : 'Add to today'}
                                >
                                  {addingToToday === widget.id ? (
                                    <div className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                  ) : isAdded ? (
                                    <Check className='w-4 h-4' />
                                  ) : (
                                    <Plus className='w-4 h-4' />
                                  )}
                                </button>
                              </div>
                            </div>


                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Edit form: AddWidgetForm renders its own overlay and portal to body */}
      {editingWidget && createPortal(
        <AddWidgetForm
          widgetId={editingWidget.widget_type}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
          editMode={true}
          existingWidget={editingWidget}
        />,
        document.body
      )}
    </BaseWidget>
  );
};

export default AllSchedulesWidget; 
