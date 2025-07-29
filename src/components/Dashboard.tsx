import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import WebSummaryWidget from './widgets/WebSummaryWidget'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import CalendarWidget from './widgets/CalendarWidget'
import SingleItemTrackerWidget from './widgets/SingleItemTrackerWidget'
import AlarmWidget from './widgets/AlarmWidget'
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
import { dashboardService } from '../services/api'
import { 
  TodayWidgetsResponse
} from '../types'
import { getDummyTodayWidgets } from '../data/dashboardDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import {
  Widget,
  constrainLayout,
  applyConstraintsToLayouts,
  convertApiWidgetsToInternal,
  createNewWidget,
  prepareDashboardLayoutForSave,
  getConfigWidgetId,
  createLayoutsFromWidgets
} from '../utils/dashboardUtils'

const ResponsiveGridLayout = WidthProvider(Responsive)

const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  


  // Apply grid CSS properties on component mount
  // This ensures CSS grid lines and other grid-related styles use the same values as the TypeScript config
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
      
      // Add dummy widget for testing
      data.widgets.push(dummyData.widgets[3]);
      
      // Convert API widget data to internal widget format using utility function
      const newWidgets = convertApiWidgetsToInternal(data);
      setWidgets(newWidgets)
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
      setWidgets((prev: Widget[]) => 
        prev.map((widget: Widget) => ({
          ...widget,
          layout: constrainLayout(widget.layout)
        }))
      )
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  
  const [widgets, setWidgets] = useState<Widget[]>([])

  const layouts = createLayoutsFromWidgets(widgets)

  const onLayoutChange = (layout: Layout[]) => {
    // During drag/resize, just update the layout without constraints
    // This allows smooth dragging and resizing
    setWidgets((prev: Widget[]) => 
      prev.map((widget: Widget) => {
        const newLayout = layout.find(l => l.i === widget.id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
  }

  // Save dashboard layout to API
  const saveDashboardLayout = async (widgets: Widget[]) => {
    try {
      const dashboardLayout = prepareDashboardLayoutForSave(widgets);

      // Note: saveDashboardLayout method doesn't exist in the new API service
      // For now, just log the layout data
      console.log('Dashboard layout to save:', dashboardLayout);
    } catch (error) {
      console.error('Failed to save dashboard layout:', error);
      // Don't show error to user for layout saves, just log it
    }
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
    const { constrainedLayout, wasConstrained } = applyConstraintsToLayouts(layout)
    
    const updatedWidgets = widgets.map((widget: Widget) => {
      const newLayout = constrainedLayout.find(l => l.i === widget.id)
      return newLayout ? { ...widget, layout: newLayout } : widget
    });
    
    setWidgets(updatedWidgets)
    
    // Save layout to API after constraints are applied
    saveDashboardLayout(updatedWidgets)
    
    // Add visual feedback if any widget was constrained
    if (wasConstrained) {
      const constrainedElements = document.querySelectorAll('.widget-container')
      constrainedElements.forEach((element) => {
        element.classList.add('constrained')
        setTimeout(() => {
          element.classList.remove('constrained')
        }, 500)
      })
    }
  }

  const addWidget = (widgetId: string) => {
    const newWidget = createNewWidget(widgetId)
    
    if (!newWidget) {
      alert('Widget configuration not found.')
      return
    }
    
    const updatedWidgets = [...widgets, newWidget];
    setWidgets(updatedWidgets)
    saveDashboardLayout(updatedWidgets)
  }

  const removeWidget = (id: string) => {
    const widget = widgets.find(w => w.id === id)
    const widgetType = widget?.type || 'widget'
    
    if (confirm(`Are you sure you want to remove this ${widgetType} widget?`)) {
      const updatedWidgets = widgets.filter((widget: Widget) => widget.id !== id);
      setWidgets(updatedWidgets)
      saveDashboardLayout(updatedWidgets)
    }
  }

  const renderWidget = (widget: Widget) => {

    switch (widget.type) {
      case 'alarm':
        return (
          <AlarmWidget 
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'websummary':
        return (
          <WebSummaryWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'websearch':
        return (
          <WebSearchWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        );
      case 'todo':
        return (
          <TaskListWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        );
      case 'singleitemtracker':
        return (
          <SingleItemTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.id)}
          />
        );
      default:
        // For unimplemented widgets, show BaseWidget with placeholder content
        {
          const configWidgetId = getConfigWidgetId(widget.type);
          const config = getWidgetConfig(configWidgetId);
    
          return (
          <BaseWidget
            title={config?.title || widget.type}
            icon={config?.icon}
            onRemove={() => removeWidget(widget.id)}
          >
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="text-4xl mb-2">{config?.icon || '🚧'}</div>
              <h3 className="font-medium mb-2">{config?.title || widget.type}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {config?.description || 'This widget is coming soon!'}
              </p>
              <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                Under Development
              </div>
            </div>
          </BaseWidget>
        )}
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
          layouts={{ lg: Object.values(layouts) }}
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
        {widgets.map((widget: Widget) => (
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
