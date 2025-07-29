import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import SingleItemTrackerWidget from './widgets/SingleItemTrackerWidget'
import AlarmWidget from './widgets/AlarmWidget'
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
import { dashboardService } from '../services/dashboard'
import { 
  TodayWidgetsResponse,
  DailyWidget
} from '../types'
import { getDummyTodayWidgets } from '../data/widgetDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'

const ResponsiveGridLayout = WidthProvider(Responsive)

// Simple widget interface for UI layout
interface UIWidget {
  id: string;
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

  // Fetch today's widget configuration
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
      
      // Convert API widgets to UI widgets with layout
      const uiWidgets: UIWidget[] = data.widgets.map((widget: DailyWidget, index: number) => {
        const config = getWidgetConfig(widget.widget_type);
        const defaultSize = config?.defaultSize || { w: 10, h: 10 };
        
        return {
          ...widget,
          layout: {
            i: widget.daily_widget_id,
            x: (index * 2) % 12, // Simple grid positioning
            y: Math.floor(index / 6) * 2,
            w: defaultSize.w,
            h: defaultSize.h,
            minW: config?.minSize?.w || 4,
            minH: config?.minSize?.h || 4,
            maxW: config?.maxSize?.w || 20,
            maxH: config?.maxSize?.h || 20,
          }
        };
      });
      
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

  const addWidget = (widgetId: string) => {
    const config = getWidgetConfig(widgetId);
    
    if (!config) {
      alert('Widget configuration not found.')
      return
    }
    
    const newWidget: UIWidget = {
      id: `new-${Date.now()}`,
      daily_widget_id: `daily-${widgetId}-${Date.now()}`,
      widget_ids: [],
      widget_type: widgetId,
      priority: 'LOW',
      reasoning: 'Manually added widget',
      date: new Date().toISOString().split('T')[0],
      created_at: new Date().toISOString(),
      layout: {
        i: `daily-${widgetId}-${Date.now()}`,
        x: (widgets.length * 2) % 12,
        y: Math.floor(widgets.length / 6) * 2,
        w: config.defaultSize.w,
        h: config.defaultSize.h,
        minW: config.minSize.w,
        minH: config.minSize.h,
        maxW: config.maxSize.w,
        maxH: config.maxSize.h,
      }
    };
    
    setWidgets([...widgets, newWidget]);
  }

  const removeWidget = (dailyWidgetId: string) => {
    const widget = widgets.find(w => w.daily_widget_id === dailyWidgetId)
    const widgetType = widget?.widget_type || 'widget'
    
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
      case 'todo':
        return (
          <TaskListWidget
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
