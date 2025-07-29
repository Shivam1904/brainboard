import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import SingleItemTrackerWidget from './widgets/SingleItemTrackerWidget'
import AlarmWidget from './widgets/AlarmWidget'
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties, findEmptyPosition } from '../config/grid'
import { dashboardService } from '../services/dashboard'
import { 
  TodayWidgetsResponse,
  DailyWidget,
  ApiWidgetType,
  ApiFrequency,
  ApiCategory
} from '../types'
import { getDummyTodayWidgets } from '../data/widgetDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import HabitListWidget from './widgets/HabitListWidget';
import EventTrackerWidget from './widgets/EventTrackerWidget';

const ResponsiveGridLayout = WidthProvider(Responsive)

// Simple widget interface for UI layout
interface UIWidget {
  daily_widget_id: string;
  widget_ids: string[];
  widget_type: string;
  priority: string;
  reasoning: string;
  date: string;
  created_at: string;
  layout: Layout;
}

const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  const [widgets, setWidgets] = useState<UIWidget[]>([])

  // Apply grid CSS properties on component mount
  useEffect(() => {
    const cssProperties = getGridCSSProperties()
    Object.entries(cssProperties).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value)
    })
  }, [])

  // Find optimal position for a new widget
  const findOptimalPosition = (widgetType: string, existingWidgets: UIWidget[]): { x: number; y: number } => {
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

  // Fetch today's widget configuration using getTodayWidgetList
  const fetchTodayWidgets = async () => {
    try {
      setDashboardLoading(true)
      setDashboardError(null)
      
      // Try to fetch from API first
      let data: TodayWidgetsResponse;
      let dummyData: TodayWidgetsResponse;
      dummyData = getDummyTodayWidgets();
      
      try {
        data = await dashboardService.getTodayWidgets();
        console.log('Successfully fetched today\'s widgets from API:', data);
      } catch (apiError) {
        console.warn('API call failed, falling back to dummy data:', apiError);
        // Fallback to dummy data if API is not available
        data = dummyData;
        
        // Show a subtle notification that we're using fallback data
        if (process.env.NODE_ENV === 'development') {
          console.log('Using fallback data - API server may not be running');
        }
      }
      
      // Convert API widgets to UI widgets with proper placement
      const uiWidgets: UIWidget[] = [];
      
      data.widgets.forEach((widget: DailyWidget) => {
        const config = getWidgetConfig(widget.widget_type);
        const defaultSize = config?.defaultSize || { w: 10, h: 10 };
        
        // Find optimal position for this widget
        const position = findOptimalPosition(widget.widget_type, uiWidgets);
        
        const uiWidget: UIWidget = {
          ...widget,
          layout: {
            i: widget.daily_widget_id,
            x: position.x,
            y: position.y,
            w: defaultSize.w,
            h: defaultSize.h,
            minW: config?.minSize?.w || 4,
            minH: config?.minSize?.h || 4,
            maxW: config?.maxSize?.w || 20,
            maxH: config?.maxSize?.h || 20,
          }
        };
        
        uiWidgets.push(uiWidget);
      });
      
      // Automatically add the "All Schedules" widget
      const allSchedulesConfig = getWidgetConfig('allSchedules');
      if (allSchedulesConfig) {
        const position = findOptimalPosition('allSchedules', uiWidgets);
        const allSchedulesWidget: UIWidget = {
          daily_widget_id: 'auto-all-schedules',
          widget_ids: [],
          widget_type: 'allSchedules',
          priority: 'LOW',
          reasoning: 'Automatically included for widget management',
          date: new Date().toISOString().split('T')[0],
          created_at: new Date().toISOString(),
          layout: {
            i: 'auto-all-schedules',
            x: position.x,
            y: position.y,
            w: allSchedulesConfig.defaultSize.w,
            h: allSchedulesConfig.defaultSize.h,
            minW: allSchedulesConfig.minSize.w,
            minH: allSchedulesConfig.minSize.h,
            maxW: allSchedulesConfig.maxSize.w,
            maxH: allSchedulesConfig.maxSize.h,
          }
        };
        
        uiWidgets.push(allSchedulesWidget);
      }
      
      setWidgets(uiWidgets);
    } catch (err) {
      console.error('Failed to fetch today\'s widgets:', err)
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
      setWidgets((prev: UIWidget[]) => 
        prev.map((widget: UIWidget) => ({
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
    setWidgets((prev: UIWidget[]) => 
      prev.map((widget: UIWidget) => {
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
    
    const updatedWidgets = widgets.map((widget: UIWidget) => {
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
    const config = getWidgetConfig(widgetId);
    
    if (!config) {
      alert('Widget configuration not found.')
      return
    }
    
    try {
      // Call the API to add a new widget
      const response = await dashboardService.addNewWidget({
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
      
      // Add widget locally even if API fails
      const position = findOptimalPosition(widgetId, widgets);
      const newWidget: UIWidget = {
        daily_widget_id: `temp-${Date.now()}`,
        widget_ids: [],
        widget_type: widgetId,
        priority: 'LOW',
        reasoning: 'Manually added widget',
        date: new Date().toISOString().split('T')[0],
        created_at: new Date().toISOString(),
        layout: {
          i: `temp-${Date.now()}`,
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
      
      setWidgets(prev => [...prev, newWidget]);
      
      // Show a subtle notification that we're using local data
      if (process.env.NODE_ENV === 'development') {
        console.log('Widget added locally - API server may not be running');
      }
    }
  }

  const removeWidget = (dailyWidgetId: string) => {
    const widget = widgets.find(w => w.daily_widget_id === dailyWidgetId)
    const widgetType = widget?.widget_type || 'widget'
    
    // Prevent removal of the automatically included "All Schedules" widget
    if (dailyWidgetId === 'auto-all-schedules') {
      alert('The "All Schedules" widget cannot be removed as it is automatically included for widget management.');
      return;
    }
    
    if (confirm(`Are you sure you want to remove this ${widgetType} widget?`)) {
      const updatedWidgets = widgets.filter((widget: UIWidget) => widget.daily_widget_id !== dailyWidgetId);
      setWidgets(updatedWidgets)
    }
  }

  const renderWidget = (widget: UIWidget) => {
    switch (widget.widget_type) {
      case 'alarm':
        return (
          <AlarmWidget 
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        )
      case 'websearch':
        return (
          <WebSearchWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-task':
        return (
          <TaskListWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-event':
        return (
          <EventTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
          );
      case 'todo-habit':
        return (
          <HabitListWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'singleitemtracker':
        return (
          <SingleItemTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
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
            onClick={() => setShowGridLines(!showGridLines)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showGridLines 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            {showGridLines ? 'Hide Grid' : 'Show Grid'}
          </button>
          <AddWidgetButton onAddWidget={addWidget} />
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
        {widgets.map((widget: UIWidget) => (
          <div key={widget.layout.i} className="widget-container">
            {renderWidget(widget)}
          </div>
        ))}
      </ResponsiveGridLayout>
      </div>
    </div>
  )
}

export default Dashboard
