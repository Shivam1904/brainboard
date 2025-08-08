import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import BaseWidget from './widgets/BaseWidget'
import CalendarWidget from './widgets/CalendarWidget'
import AdvancedSingleTaskWidget from './widgets/AdvancedSingleTaskWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties, findEmptyPosition } from '../config/grid'
import { dashboardService } from '../services/dashboard'
// import { getDummyTodayWidgets } from '../data/widgetDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import AiChatWidget from './widgets/AiChatWidget';
import MoodTrackerWidget from './widgets/MoodTrackerWidget';
import SimpleClockWidget from './widgets/SimpleClockWidget';
import { apiService, DailyWidget } from '../services/api';
import { ApiCategory, ApiFrequency, ApiWidgetType } from '@/types/widgets';

const ResponsiveGridLayout = WidthProvider(Responsive)


const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  const [widgets, setWidgets] = useState<DailyWidget[]>([])
  const [viewWidgetStates, setViewWidgetStates] = useState<DailyWidget[]>([])
  // Apply grid CSS properties on component mount
  useEffect(() => {
    const cssProperties = getGridCSSProperties()
    Object.entries(cssProperties).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value)
    })
  }, [])

  // Find optimal position for a new widget
  const findOptimalPosition = (widgetType: string, existingWidgets: DailyWidget[]): { x: number; y: number } => {
    const config = getWidgetConfig(widgetType);
    if (!config) return { x: 0, y: 0 };

    // Try to find empty space using the existing function
    const emptyPosition = findEmptyPosition({
      widgetId: widgetType,
      widgets: existingWidgets,
      getWidgetConfig,
      gridCols: GRID_CONFIG.cols.lg,
      maxRows: 100
    });

    if (emptyPosition) {
      return emptyPosition;
    }

    // Fallback: simple horizontal placement with wrapping
    let currentX = 0;
    let currentY = 0;
    const maxX = GRID_CONFIG.cols.lg - config.defaultSize.w;

    // Find the rightmost widget to start from
    if (existingWidgets.length > 0) {
      const rightmostWidget = existingWidgets.reduce((rightmost, widget) => {
        return widget.layout.x + widget.layout.w > rightmost.layout.x + rightmost.layout.w ? widget : rightmost;
      });
      currentX = rightmostWidget.layout.x + rightmostWidget.layout.w;
      currentY = rightmostWidget.layout.y;
    }

    // If we can't fit horizontally, move to next row
    if (currentX + config.defaultSize.w > maxX) {
      currentX = 0;
      currentY += 2; // Add some spacing between rows
    }

    return { x: currentX, y: currentY };
  };

  // Fetch all widgets and today's widgets
  const fetchTodayWidgets = async () => {
    try {
      setDashboardLoading(true)
      setDashboardError(null)

      let allWidgetsData: any[] = [];
      let todayWidgetsData: DailyWidget[] = [];
      try {
        // Fetch all widgets first
        allWidgetsData = await dashboardService.getAllWidgets();
        console.log('Successfully fetched all widgets from API:', allWidgetsData);

        // Fetch today's widgets
        todayWidgetsData = await dashboardService.getTodayWidgets();
        console.log('Successfully fetched today\'s widgets from API:', todayWidgetsData);

        // Enhanced logging for debugging
        todayWidgetsData.forEach((widget, index) => {
          console.log(`Widget ${index + 1}:`, {
            daily_widget_id: widget.daily_widget_id,
            widget_id: widget.widget_id,
            title: widget.title,
            widget_type: widget.widget_type,
            widget_config: widget.widget_config
          });
        });
      } catch (apiError) {
        console.warn('API call failed, falling back to dummy data:', apiError);
      }

      // Convert widgets to UI format with proper placement
      const uiWidgets: DailyWidget[] = [];

      // Track view widget states for the AddWidgetButton
      const viewWidgetTypes = ['allSchedules', 'aiChat', 'moodTracker', 'weatherWidget', 'simpleClock'];
      const allWidgetsDataViewWidgets = allWidgetsData.filter(w => viewWidgetTypes.includes(w.widget_type));
      setViewWidgetStates(allWidgetsDataViewWidgets);

      // Step 1: Handle view widgets (allSchedules, aiChat, moodTracker) from all widgets list
      viewWidgetTypes.forEach(widgetType => {
        // Find the widget in all widgets list
        const allWidgetsViewWidget = allWidgetsData.find(w => w.widget_type === widgetType);
        const isVisible = allWidgetsViewWidget?.widget_config?.visibility; // Default to true if not set
        if (isVisible) {
          const config = getWidgetConfig(widgetType);
          if (config) {
            const position = findOptimalPosition(widgetType, uiWidgets);
            const viewWidget: DailyWidget = {
              id: `auto-${widgetType}`,
              daily_widget_id: `auto-${widgetType}`,
              widget_id: allWidgetsViewWidget?.id || '',
              widget_type: widgetType,
              title: config.title,
              frequency: 'daily',
              importance: 0.5,
              category: 'utilities',
              description: config.description,
              is_permanent: true,
              priority: 'LOW',
              reasoning: 'View widget managed by visibility setting',
              date: new Date().toISOString().split('T')[0],
              created_at: allWidgetsViewWidget?.created_at || new Date().toISOString(),
              widget_config: allWidgetsViewWidget?.widget_config,
              layout: {
                i: `auto-${widgetType}`,
                x: position.x,
                y: position.y,
                w: config.defaultSize.w,
                h: config.defaultSize.h,
                minW: config.minSize.w,
                minH: config.minSize.h,
                maxW: config.maxSize.w,
                maxH: config.maxSize.h,
              }
            };

            uiWidgets.push(viewWidget);
          }
        }
      });
      const trackerWidgetTypes: any[] = ['calendar', 'weekchart'];

      // Step 2: Process today's widgets according to new logic
      const advancedSingleTaskWidgets: DailyWidget[] = [];
      const regularTaskWidgets: DailyWidget[] = [];
      const webSearchWidgets: DailyWidget[] = [];
      const individualTrackerWidgets: DailyWidget[] = [];
      console.log('Processing today\'s widgets:', todayWidgetsData.length, 'widgets');

      // Validate and filter out invalid widgets
      const validWidgets = todayWidgetsData.filter((widget: DailyWidget) => {
        if (!widget || !widget.daily_widget_id || !widget.widget_id || !widget.widget_type) {
          console.warn('Invalid widget data:', widget);
          return false;
        }
        return true;
      });

      console.log(`Found ${validWidgets.length} valid widgets out of ${todayWidgetsData.length} total`);

      validWidgets.forEach((widget: DailyWidget) => {
        // Skip view widgets as they're already handled above
        if (viewWidgetTypes.includes(widget.widget_type)) {
          return;
        }

        const widgetConfig = widget.widget_config || {};

        // Check if widget meets criteria for advanced single task
        const hasTrackerDetails = widgetConfig?.include_tracker_details === true;
        const hasAlarmDetails = widgetConfig?.include_alarm_details === true;
        const hasProgressDetails = widgetConfig?.include_progress_details === true;

        // Check if milestone is coming up in 7 days
        const milestones = Array.isArray(widgetConfig?.milestones) ? widgetConfig.milestones : [];
        const hasUpcomingMilestone = hasProgressDetails &&
          milestones.some((milestone: any) => {
            if (!milestone?.due_date) return false;
            try {
              const milestoneDate = new Date(milestone.due_date);
              const today = new Date();
              const sevenDaysFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
              return milestoneDate >= today && milestoneDate <= sevenDaysFromNow;
            } catch (err) {
              console.warn('Invalid milestone date:', milestone.due_date);
              return false;
            }
          });

        console.log(`Widget "${widget.title}":`, {
          hasTrackerDetails,
          hasAlarmDetails,
          hasProgressDetails,
          hasUpcomingMilestone,
          milestones
        });

        // Determine widget type based on criteria
        if (hasTrackerDetails || hasAlarmDetails || hasUpcomingMilestone) {
          console.log(`Creating advanced single task widget for: ${widget.title}`);
          // Create advanced single task widget
          const config = getWidgetConfig('advancedsingletask');
          const position = findOptimalPosition('advancedsingletask', uiWidgets);

          const advancedWidget: DailyWidget = {
            ...widget,
            id: `advanced-single-task-${widget.daily_widget_id}`,
            daily_widget_id: widget.daily_widget_id,
            widget_type: 'advancedsingletask',
            title: `Advanced: ${widget.title}`,
            priority: widget.importance >= 0.7 ? 'HIGH' : 'LOW',
            reasoning: 'Advanced single task widget with tracker, alarm, and progress details',
            date: new Date().toISOString().split('T')[0],
            created_at: widget.created_at,
            layout: {
              i: `advanced-single-task-${widget.daily_widget_id}`,
              x: position.x,
              y: position.y,
              w: config?.defaultSize?.w || 12,
              h: config?.defaultSize?.h || 14,
              minW: config?.minSize?.w || 8,
              minH: config?.minSize?.h || 6,
              maxW: config?.maxSize?.w || 18,
              maxH: config?.maxSize?.h || 20,
            }
          };

          advancedSingleTaskWidgets.push(advancedWidget);
        } else if (trackerWidgetTypes.includes(widget.widget_type)) {
          console.log(`Adding to tracker widget list: ${widget.title}`);
          // Add to tracker widget list
          const config = getWidgetConfig(widget.widget_type);
          const position = findOptimalPosition(widget.widget_type, uiWidgets);

          const trackerWidget: DailyWidget = {
            ...widget,
            id: `tracker-${widget.daily_widget_id}`,
            daily_widget_id: widget.daily_widget_id,
            widget_type: widget.widget_type,
            title: `Tracker: ${widget.title}`,
            priority: widget.importance >= 0.7 ? 'HIGH' : 'LOW',
            reasoning: 'Tracker widget for ' + widget.title,
            date: new Date().toISOString().split('T')[0],
            created_at: widget.created_at,
            layout: {
              i: `tracker-${widget.daily_widget_id}`,
              x: position.x,
              y: position.y,
              w: config?.defaultSize?.w || 12,
              h: config?.defaultSize?.h || 14,
              minW: config?.minSize?.w || 8,
              minH: config?.minSize?.h || 6,
              maxW: config?.maxSize?.w || 18,
              maxH: config?.maxSize?.h || 20,
            }
          }
          individualTrackerWidgets.push(trackerWidget);
        }
        else {
          console.log(`Adding to regular task list: ${widget.title}`);
          // Add to regular task list
          regularTaskWidgets.push(widget);
        }

        // Check if web search widget should be added
        if (widgetConfig?.include_websearch_details === true) {
          console.log(`Creating web search widget for: ${widget.title}`);
          const config = getWidgetConfig('websearch');
          if (!config) {
            console.warn('Web search widget config not found');
            return;
          }
          const position = findOptimalPosition('websearch', uiWidgets);

          const webSearchWidget: DailyWidget = {
            id: `websearch-${widget.daily_widget_id}`,
            daily_widget_id: `${widget.daily_widget_id}`,
            widget_id: widget.widget_id,
            widget_type: 'websearch',
            title: `Web Search: ${widget.title}`,
            frequency: 'daily',
            importance: widget.importance,
            category: 'information',
            description: `Web search for ${widget.title}`,
            is_permanent: false,
            priority: widget.importance >= 0.7 ? 'HIGH' : 'LOW',
            reasoning: 'Web search widget for task information',
            date: new Date().toISOString().split('T')[0],
            created_at: widget.created_at,
            widget_config: widgetConfig,
            layout: {
              i: `websearch-${widget.daily_widget_id}`,
              x: position.x,
              y: position.y,
              w: config?.defaultSize?.w || 11,
              h: config?.defaultSize?.h || 14,
              minW: config?.minSize?.w || 8,
              minH: config?.minSize?.h || 8,
              maxW: config?.maxSize?.w || 20,
              maxH: config?.maxSize?.h || 24,
            }
          };

          webSearchWidgets.push(webSearchWidget);
        }
      });

      // Step 3: Add advanced single task widgets
      console.log(`Adding ${advancedSingleTaskWidgets.length} advanced single task widgets`);
      uiWidgets.push(...advancedSingleTaskWidgets);

      // Step 4: Create single task list widget if there are regular tasks
      console.log(`Creating combined task list with ${regularTaskWidgets.length} regular tasks`);
      if (regularTaskWidgets.length > 0) {
        const config = getWidgetConfig('todo-task');
        const position = findOptimalPosition('todo-task', uiWidgets);

        const taskListWidget: DailyWidget = {
          id: 'task-list-combined',
          daily_widget_id: 'task-list-combined',
          widget_id: 'task-list-combined',
          widget_type: 'todo-task',
          title: 'Task List',
          frequency: 'daily',
          importance: 0.5,
          category: 'productivity',
          description: 'Combined task list for regular tasks',
          is_permanent: false,
          priority: 'LOW',
          reasoning: 'Combined task list widget for regular tasks',
          date: new Date().toISOString().split('T')[0],
          created_at: new Date().toISOString(),
          widget_config: {
            combined_tasks: regularTaskWidgets.map(w => ({
              id: w.daily_widget_id,
              widget_id: w.widget_id,
              title: w.title,
              description: w.description,
              importance: w.importance,
              category: w.category,
              widget_config: w.widget_config
            }))
          },
          layout: {
            i: 'task-list-combined',
            x: position.x,
            y: position.y,
            w: config?.defaultSize?.w || 12,
            h: config?.defaultSize?.h || 15,
            minW: config?.minSize?.w || 8,
            minH: config?.minSize?.h || 8,
            maxW: config?.maxSize?.w || 30,
            maxH: config?.maxSize?.h || 36,
          }
        };

        uiWidgets.push(taskListWidget);
      }

      if (individualTrackerWidgets.length > 0) {
        individualTrackerWidgets.forEach((widget: DailyWidget) => {
          uiWidgets.push(widget);
        });
      }

      // Step 5: Add web search widgets
      console.log(`Adding ${webSearchWidgets.length} web search widgets`);
      uiWidgets.push(...webSearchWidgets);

      setWidgets(uiWidgets);
    } catch (err) {
      console.error('Failed to fetch widgets:', err)
      setDashboardError('Failed to load dashboard configuration')
    } finally {
      setDashboardLoading(false)
    }
  }

  // Fetch today's widgets on component mount
  useEffect(() => {
    fetchTodayWidgets()
  }, [])

  // Handle window resize to update constraints
  useEffect(() => {
    const handleResize = () => {
      // Re-constrain all widgets when window is resized
      setWidgets((prev: DailyWidget[]) =>
        prev.map((widget: DailyWidget) => ({
          ...widget,
          layout: constrainLayout(widget.layout)
        }))
      )
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Simple layout constraint function
  const constrainLayout = (layout: Layout): Layout => {
    const gridCols = GRID_CONFIG.cols.lg;
    const maxHeight = 50; // Maximum grid height

    return {
      ...layout,
      x: Math.max(0, Math.min(layout.x, gridCols - layout.w)),
      y: Math.max(0, Math.min(layout.y, maxHeight - layout.h)),
      w: Math.max(layout.minW || 1, Math.min(layout.w, layout.maxW || gridCols)),
      h: Math.max(layout.minH || 1, Math.min(layout.h, layout.maxH || maxHeight))
    };
  }

  // Create layouts object for react-grid-layout
  const layouts = {
    lg: widgets.map(widget => widget.layout)
  };

  const onLayoutChange = (layout: Layout[]) => {
    // Update widget layouts
    setWidgets((prev: DailyWidget[]) =>
      prev.map((widget: DailyWidget) => {
        const newLayout = layout.find(l => l.i === widget.daily_widget_id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
  }

  const onDragStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes dragging
    applyConstraints(layout)
  }

  const onResizeStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes resizing
    applyConstraints(layout)
  }

  const applyConstraints = (layout: Layout[]) => {
    const constrainedLayout = layout.map(l => constrainLayout(l));

    const updatedWidgets = widgets.map((widget: DailyWidget) => {
      const newLayout = constrainedLayout.find(l => l.i === widget.daily_widget_id)
      return newLayout ? { ...widget, layout: newLayout } : widget
    });

    setWidgets(updatedWidgets)

    // Add visual feedback
    const constrainedElements = document.querySelectorAll('.widget-container')
    constrainedElements.forEach((element) => {
      element.classList.add('constrained')
      setTimeout(() => {
        element.classList.remove('constrained')
      }, 500)
    })
  }

  // Add new widget using addNewWidget API
  const addWidget = async (widgetId: string) => {
    // Handle refresh case
    if (widgetId === 'refresh') {
      await fetchTodayWidgets();
      return;
    }

    const config = getWidgetConfig(widgetId);

    if (!config) {
      alert('Widget configuration not found.')
      return
    }

    try {
      // Call the API to add a new widget
      const response = await dashboardService.createWidget({
        widget_type: config.apiWidgetType as ApiWidgetType,
        frequency: 'daily' as ApiFrequency, // Default to daily
        importance: 0.5, // Default importance
        title: config.title,
        category: config.category as ApiCategory
      });

      console.log('Widget added successfully:', response);

      // Refresh the dashboard to show the new widget
      await fetchTodayWidgets();

    } catch (error) {
      console.error('Failed to add widget:', error);

    }
  }

  const removeWidget = async (dailyWidgetId: string) => {
    const widget = widgets.find(w => w.daily_widget_id === dailyWidgetId)
    const widgetType = widget?.widget_type || 'widget'

    // Prevent removal of view widgets - they should be managed through the Views dropdown
    if (widget?.widget_type === 'allSchedules' || widget?.widget_type === 'aiChat' || widget?.widget_type === 'moodTracker' || widget?.widget_type === 'weatherWidget' || widget?.widget_type === 'simpleClock') {
      alert('View widgets cannot be removed directly. Use the Views dropdown to toggle their visibility.');
      return;
    }

    // Prevent removal of the automatically included view widgets
    if (dailyWidgetId === 'auto-all-schedules' || dailyWidgetId === 'auto-moodTracker' || dailyWidgetId === 'auto-aiChat' || dailyWidgetId === 'auto-weatherWidget' || dailyWidgetId === 'auto-simpleClock') {
      alert('This view widget is managed via the Views dropdown and cannot be removed directly.');
      return;
    }

    // Handle combined task list widget removal
    if (dailyWidgetId === 'task-list-combined') {
      alert('The combined task list widget cannot be removed directly. Individual tasks are managed through the task creation process.');
      return;
    }

    // Handle web search widgets (they are automatically generated)
    if (dailyWidgetId.startsWith('websearch-')) {
      alert('Web search widgets are automatically generated and cannot be removed directly.');
      return;
    }

    // Handle advanced single task widgets
    if (widget?.title?.startsWith('Advanced: ')) {
      if (confirm(`Are you sure you want to remove this advanced single task widget? This will also remove the associated web search widget if it exists.`)) {
        try {
          // Remove the main widget
          await apiService.removeWidgetFromToday(dailyWidgetId);

          // Also remove associated web search widget if it exists
          const webSearchWidgetId = `websearch-${widget.id}`;
          const webSearchWidget = widgets.find(w => w.daily_widget_id === webSearchWidgetId);
          if (webSearchWidget) {
            try {
              await apiService.removeWidgetFromToday(webSearchWidgetId);
            } catch (webSearchError) {
              console.warn('Failed to remove associated web search widget:', webSearchError);
            }
          }

          // Refresh the dashboard to update all widgets
          await fetchTodayWidgets();
        } catch (error) {
          alert('Failed to remove widget from dashboard. Please try again.');
          console.error('Failed to remove advanced single task widget:', error);
        }
      }
      return;
    }

    if (confirm(`Are you sure you want to remove this ${widgetType} widget?`)) {
      try {
        // Call API to set is_active = 0
        await apiService.removeWidgetFromToday(dailyWidgetId);
        const updatedWidgets = widgets.filter((widget: DailyWidget) => widget.daily_widget_id !== dailyWidgetId);
        setWidgets(updatedWidgets)
      } catch (error) {
        alert('Failed to remove widget from dashboard. Please try again.');
        console.error('Failed to update is_active for DailyWidget:', error);
      }
    }
  }

  const renderWidget = (widget: DailyWidget) => {
    switch (widget.widget_type) {
      case 'websearch':
        return (
          <WebSearchWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-task':
        // Check if this is a combined task list widget
        if (widget.widget_config?.combined_tasks) {
          return (
            <TaskListWidget
              widget={{
                ...widget,
                title: 'Task List',
                description: `Combined task list with ${widget.widget_config.combined_tasks.length} tasks`
              }}
              onRemove={() => removeWidget(widget.daily_widget_id)}
            />
          );
        }
        // Fall through to default case for regular todo-task widgets
        break;
      case 'advancedsingletask':
        return (
          <AdvancedSingleTaskWidget
            widget={{
              ...widget,
              title: widget.title.replace('Advanced: ', ''),
              description: 'Advanced single task with tracker, alarm, and progress details'
            }}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'aiChat':
        return (
          <AiChatWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'moodTracker':
        return (
          <MoodTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
            onWidgetAddedToToday={() => fetchTodayWidgets()}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'simpleClock':
        return (
          <SimpleClockWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      default:
        // For unimplemented widgets, show BaseWidget with placeholder content
        const config = getWidgetConfig(widget.widget_type);

        return (
          <BaseWidget
            title={config?.title || widget.widget_type}
            icon={config?.icon}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          >
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="text-4xl mb-2">{config?.icon || '🚧'}</div>
              <h3 className="font-medium mb-2">{config?.title || widget.widget_type}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {config?.description || 'This widget is coming soon!'}
              </p>
              <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                Under Development
              </div>
            </div>
          </BaseWidget>
        )
    }
  }

  // Show loading state while fetching dashboard configuration
  if (dashboardLoading) {
    return (
      <div className="h-full w-full flex flex-col">
        <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-foreground">
                🧠 Brainboard
              </h1>
              <p className="text-xs text-muted-foreground">
                AI-Powered Dashboard with Smart Widgets
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h2 className="text-lg font-semibold mb-2">Loading Dashboard</h2>
            <p className="text-muted-foreground">Fetching today's widget configuration...</p>
          </div>
        </div>
      </div>
    )
  }

  // Show error state if dashboard loading failed
  if (dashboardError) {
    return (
      <div className="h-full w-full flex flex-col">
        <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-foreground">
                🧠 Brainboard
              </h1>
              <p className="text-xs text-muted-foreground">
                AI-Powered Dashboard with Smart Widgets
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchTodayWidgets}
              className="px-3 py-1 text-sm rounded bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-4">⚠️</div>
            <h2 className="text-lg font-semibold mb-2">Failed to Load Dashboard</h2>
            <p className="text-muted-foreground mb-4">{dashboardError}</p>
            <button
              onClick={fetchTodayWidgets}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full flex flex-col bg-yellow-100">
      <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <h1 className="text-xl font-bold text-foreground">
              🧠 Brainboard
            </h1>
            <p className="text-xs text-muted-foreground">
              AI-Powered Dashboard with Smart Widgets
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowGridLines(!showGridLines)}
            className={`px-3 py-1 text-sm rounded transition-colors ${showGridLines
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
          >
            {showGridLines ? 'Hide Grid' : 'Show Grid'}
          </button>
          <AddWidgetButton
            onAddWidget={addWidget}
            existingViewWidgets={viewWidgetStates}
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <ResponsiveGridLayout
          className={`layout min-h-full ${showGridLines ? 'show-grid-lines' : ''}`}
          layouts={layouts}
          breakpoints={GRID_CONFIG.breakpoints}
          cols={GRID_CONFIG.cols}
          rowHeight={GRID_CONFIG.rowHeight}
          margin={GRID_CONFIG.margin}
          containerPadding={GRID_CONFIG.containerPadding}
          isDraggable={true}
          isResizable={true}
          preventCollision={true}
          compactType={null}
          useCSSTransforms={false}
          draggableHandle=".widget-drag-handle"
          onLayoutChange={onLayoutChange}
          onDragStop={onDragStop}
          onResizeStop={onResizeStop}
        >
          {widgets.map((widget: DailyWidget) => (
            <div key={widget.id} className="widget-container">
              {renderWidget(widget)}
            </div>
          ))}
        </ResponsiveGridLayout>
      </div>
    </div>
  )
}

export default Dashboard
