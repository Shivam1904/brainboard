import { useState, useEffect, useMemo } from 'react'
import { Responsive, WidthProvider } from 'react-grid-layout'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import BaseWidget from './widgets/BaseWidget'
import CalendarWidget from './widgets/CalendarWidget'
import AdvancedSingleTaskWidget from './widgets/AdvancedSingleTaskWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
import { dashboardService } from '../services/dashboard'
// import { getDummyTodayWidgets } from '../data/widgetDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import AiChatWidget from './widgets/AiChatWidget';
import MoodTrackerWidget from './widgets/MoodTrackerWidget';
import SimpleClockWidget from './widgets/SimpleClockWidget';
import WeatherWidget from './widgets/WeatherWidget';
import { apiService, DailyWidget } from '../services/api';
import { ApiCategory, ApiFrequency, ApiWidgetType } from '@/types/widgets';
import YearCalendarWidget from './widgets/YearCalendarWidget';

const ResponsiveGridLayout = WidthProvider(Responsive)


const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  const [widgets, setWidgets] = useState<DailyWidget[]>([])
  const [viewWidgetStates, setViewWidgetStates] = useState<DailyWidget[]>([])
  const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0])
  // Centralized layout: track per-widget size overrides (e.g., dynamic height changes)
  const [sizeOverrides, setSizeOverrides] = useState<Record<string, { w?: number; h?: number }>>({})
  // Apply grid CSS properties on component mount
  useEffect(() => {
    const cssProperties = getGridCSSProperties()
    Object.entries(cssProperties).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value)
    })
  }, [])

  useEffect(() => {
    fetchTodayWidgets()
  }, [currentDate])
  // No manual data-grid; rely on library defaults

  // Helper to build a minimal placeholder layout to satisfy type; actual layout is centralized
  const buildPlaceholderLayout = (id: string) => ({ i: id, x: 0, y: 0, w: 1, h: 1 })

  // Fetch all widgets and today's widgets
  const fetchTodayWidgets = async () => {
    try {
      setDashboardLoading(true);
      setDashboardError(null);
    
      const viewWidgetTypes = ['allSchedules', 'aiChat', 'moodTracker', 'weatherWidget', 'simpleClock'];
      const trackerWidgetTypes = ['calendar', 'weekchart', 'yearCalendar'];
    
      const makeWidget = (base: Partial<DailyWidget>, overrides: Partial<DailyWidget> = {}): DailyWidget => ({
        id: base.id || '',
        daily_widget_id: base.daily_widget_id || '',
        widget_id: base.widget_id || '',
        widget_type: base.widget_type || '',
        title: base.title || '',
        description: base.description || '',
        frequency: 'daily',
        importance: 0.5,
        category: 'utilities',
        is_permanent: false,
        priority: 'LOW',
        date: new Date().toISOString().split('T')[0],
        created_at: new Date().toISOString(),
        layout: buildPlaceholderLayout(base.id || ''),
        ...base,
        ...overrides
      });
    
      const isValidWidget = (w: DailyWidget) =>
        w && w.daily_widget_id && w.widget_id && w.widget_type;
    
      const hasUpcomingMilestone = (milestones: any[]) => {
        const today = new Date();
        const weekAhead = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        return milestones.some(m => {
          if (!m?.due_date) return false;
          const date = new Date(m.due_date);
          return date >= today && date <= weekAhead;
        });
      };
    
      // --- Fetch data ---
      let allWidgetsData: any[] = [];
      let todayWidgetsData: DailyWidget[] = [];
      try {
        allWidgetsData = await dashboardService.getAllWidgets();
        todayWidgetsData = await dashboardService.getTodayWidgets(currentDate);
      } catch (apiError) {
        console.warn('API call failed, falling back to dummy data:', apiError);
      }
    
      setViewWidgetStates(allWidgetsData.filter(w => viewWidgetTypes.includes(w.widget_type)));
    
      // --- Prepare widget lists ---
      const uiWidgets: DailyWidget[] = [];
      const advancedWidgets: DailyWidget[] = [];
      const regularWidgets: DailyWidget[] = [];
      const trackerWidgets: DailyWidget[] = [];
      const webSearchWidgets: DailyWidget[] = [];
    
      // Step 1: Add permanent view widgets
      viewWidgetTypes.forEach(type => {
        const w = allWidgetsData.find(x => x.widget_type === type);
        if (w?.widget_config?.visibility) {
          const config = getWidgetConfig(type);
          if (config) {
            uiWidgets.push(makeWidget({
              id: `auto-${type}`,
              daily_widget_id: `auto-${type}`,
              widget_id: w.id || '',
              widget_type: type,
              title: config.title,
              description: config.description,
              is_permanent: true,
              widget_config: w.widget_config
            }));
          }
        }
      });
    
      // Step 2: Process today's widgets
      const validWidgets = todayWidgetsData.filter(isValidWidget);
    
      validWidgets.forEach(widget => {
        if (viewWidgetTypes.includes(widget.widget_type)) return;
    
        const cfg = widget.widget_config || {};
        const milestones = Array.isArray(cfg.milestones) ? cfg.milestones : [];
    
        const advCondition = cfg.include_tracker_details || cfg.include_alarm_details ||
                              (cfg.include_progress_details && hasUpcomingMilestone(milestones));
    
        if (advCondition) {
          advancedWidgets.push(makeWidget(widget, {
            id: `advanced-${widget.daily_widget_id}`,
            widget_type: 'advancedsingletask',
            title: `Advanced: ${widget.title}`,
            reasoning: 'Advanced single task widget with tracker/alarm/progress'
          }));
        } else if (trackerWidgetTypes.includes(widget.widget_type)) {
          trackerWidgets.push(makeWidget(widget, {
            id: `tracker-${widget.daily_widget_id}`,
            title: `Tracker: ${widget.title}`,
            reasoning: 'Tracker widget'
          }));
        } else {
          regularWidgets.push(widget);
        }
    
        if (cfg.include_websearch_details) {
          const config = getWidgetConfig('websearch');
          if (config) {
            webSearchWidgets.push(makeWidget(widget, {
              id: `websearch-${widget.daily_widget_id}`,
              widget_type: 'websearch',
              title: `Web Search: ${widget.title}`,
              category: 'information',
              description: `Web search for ${widget.title}`,
              reasoning: 'Web search widget for task'
            }));
          }
        }
      });
    
      // Step 3: Assemble final list
      uiWidgets.push(...advancedWidgets);
    
      if (regularWidgets.length) {
        uiWidgets.push(makeWidget({
          id: 'task-list-combined',
          daily_widget_id: 'task-list-combined',
          widget_id: 'task-list-combined',
          widget_type: 'todo-task',
          title: 'Task List',
          category: 'productivity',
          description: 'Combined task list',
          widget_config: {
            combined_tasks: regularWidgets.map(w => ({
              id: w.daily_widget_id,
              widget_id: w.widget_id,
              title: w.title,
              description: w.description,
              importance: w.importance,
              category: w.category,
              widget_config: w.widget_config
            }))
          }
        }));
      }
    
      uiWidgets.push(...trackerWidgets, ...webSearchWidgets);
    
      setWidgets(uiWidgets);
    } catch (err) {
      console.error('Failed to fetch widgets:', err);
      setDashboardError('Failed to load dashboard configuration');
    } finally {
      setDashboardLoading(false);
    }
    
  }

  // Fetch today's widgets on component mount
  useEffect(() => {
    fetchTodayWidgets()
  }, [])

  // No explicit layouts or handlers; let library manage placement

  // Compute initial row-wise positions so items are spread across the row before wrapping
  const computeRowWiseLayout = (
    items: Array<{ id: string; w: number; h: number }>
  ) => {
    const cols = GRID_CONFIG.cols.lg
    let currentX = 0
    let currentY = 0
    let currentRowHeight = 0
    const positions = new Map<string, { x: number; y: number }>()

    for (const item of items) {
      const width = Math.min(item.w, cols)
      if (currentX + width > cols) {
        currentX = 0
        currentY += currentRowHeight
        currentRowHeight = 0
      }
      positions.set(item.id, { x: currentX, y: currentY })
      currentX += width
      currentRowHeight = Math.max(currentRowHeight, item.h)
    }

    return positions
  }

  const computedPositions = useMemo(() => {
    const layoutItems = widgets.map((w) => {
      const config = getWidgetConfig(w.widget_type)
      const override = sizeOverrides[w.daily_widget_id] || sizeOverrides[String(w.id)] || {}
      const width = override.w ?? (config?.defaultSize?.w ?? 12)
      const height = override.h ?? (config?.defaultSize?.h ?? 8)
      return { id: String(w.id), w: width, h: height }
    })
    return computeRowWiseLayout(layoutItems)
  }, [widgets, sizeOverrides])

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

  const onHeightChange = (dailyWidgetId: string, newHeight: number) => {
    console.log('Widget height changed:', dailyWidgetId, newHeight)
    setSizeOverrides((prev) => ({
      ...prev,
      [dailyWidgetId]: { ...(prev[dailyWidgetId] || {}), h: newHeight },
    }))
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
              targetDate={currentDate}
              onHeightChange={onHeightChange}
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
            onHeightChange={onHeightChange}
          />
        );
      case 'yearCalendar':
        return (
          <YearCalendarWidget
            targetDate={currentDate}
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            targetDate={currentDate}
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
            targetDate={currentDate}
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
            targetDate={currentDate}
            widget={widget}
            onHeightChange={onHeightChange}
            onWidgetAddedToToday={() => fetchTodayWidgets()}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'simpleClock':
        return (
          <SimpleClockWidget
            targetDate={currentDate}
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'weatherWidget':
        return (
          <WeatherWidget
            targetDate={currentDate}
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
    <div className={`flex flex-col h-full w-full  bg-gradient-to-br from-yellow-100 via-sky-100 to-white text-gray-800 dark:from-indigo-900 dark:via-slate-900 dark:to-black dark:text-slate-100`}>
      <div className="px-4 py-3 flex justify-between items-center border-b  shrink-0">
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
        <div className="flex-1">
          <div className="flex items-center justify-center gap-3">
            <div className="flex flex-row">
                <button className="text-sm text-muted-foreground" onClick={() => setCurrentDate(new Date(new Date(currentDate).setDate(new Date(currentDate).getDate() - 1)).toISOString().split('T')[0])}>
                {'<<<'}
                </button>
                <span className="text-sm text-muted-foreground">
                  {currentDate}
                </span>
                <button className="text-sm text-muted-foreground" onClick={() => setCurrentDate(new Date(new Date(currentDate).setDate(new Date(currentDate).getDate() + 1)).toISOString().split('T')[0])}>
                  {'>>>'}
                </button>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <AddWidgetButton
            onAddWidget={addWidget}
            existingViewWidgets={viewWidgetStates}
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <ResponsiveGridLayout
          className={`layout min-h-full ${true ? 'show-grid-lines' : ''}`}
          breakpoints={GRID_CONFIG.breakpoints}
          cols={GRID_CONFIG.cols}
          rowHeight={GRID_CONFIG.rowHeight}
          margin={GRID_CONFIG.margin}
          containerPadding={GRID_CONFIG.containerPadding}
          draggableHandle=".widget-drag-handle"
          compactType="vertical"
        >
          {widgets.map((widget: DailyWidget) => {
            const config = getWidgetConfig(widget.widget_type);
            const override = sizeOverrides[widget.daily_widget_id] || sizeOverrides[String(widget.id)] || {};
            const baseW = config?.defaultSize?.w ?? 12;
            const baseH = config?.defaultSize?.h ?? 8;
            const w = override.w ?? baseW;
            const h = override.h ?? baseH;
            const pos = computedPositions.get(String(widget.id));
            const x = pos?.x ?? 0;
            const y = pos?.y ?? (Infinity as number);
            const dataGrid = { i: String(widget.id), x, y, w, h } as const;
            return (
              <div key={widget.id} className="widget-container" data-grid={dataGrid}>
                {renderWidget(widget)}
              </div>
            );
          })}
        </ResponsiveGridLayout>
      </div>
    </div>
  )
}

export default Dashboard
