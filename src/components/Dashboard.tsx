import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import ReminderWidget from './widgets/ReminderWidget'
import WebSummaryWidget from './widgets/WebSummaryWidget'
import WebSearchWidget from './widgets/WebSearchWidget';
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
// import { buildApiUrl, apiCall } from '../config/api' // Uncomment when API is ready
// import { TodayWidgetsResponse } from '../types/dashboard' // Uncomment when API is ready
import { getDummyTodayWidgets } from '../data/dashboardDummyData'

const ResponsiveGridLayout = WidthProvider(Responsive)

interface Widget {
  id: string
  type: string
  layout: Layout
  config?: Record<string, any>
  priority?: number
  enabled?: boolean
  scheduledItem?: {
    id: string;
    title: string;
    type: string;
    frequency: string;
    category?: string;
    importance?: 'High' | 'Medium' | 'Low';
    alarm?: string;
    searchQuery?: string;
  };
}

const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  
  // Helper function to get actual header height
  const getHeaderHeight = (): number => {
    const header = document.querySelector('header')
    return header ? header.clientHeight : 80
  }

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
      
      // In development, use dummy data
      // const url = buildApiUrl(API_CONFIG.dashboard.getTodayWidgets, {
      //   date: new Date().toISOString().split('T')[0]
      // });
      // const data = await apiCall<TodayWidgetsResponse>(url);
      
      // For now, use dummy data
      const data = getDummyTodayWidgets()
      
      // Convert dashboard widget config to internal widget format
      const newWidgets: Widget[] = data.widgets
        .filter(widget => widget.enabled !== false)
        .map(dashboardWidget => ({
          id: dashboardWidget.id,
          type: dashboardWidget.type,
          layout: {
            i: dashboardWidget.id,
            x: dashboardWidget.layout.x,
            y: dashboardWidget.layout.y,
            w: dashboardWidget.layout.w,
            h: dashboardWidget.layout.h,
            minW: dashboardWidget.layout.minW || getWidgetConfig(dashboardWidget.type)?.minSize.w || 1,
            minH: dashboardWidget.layout.minH || getWidgetConfig(dashboardWidget.type)?.minSize.h || 1,
            maxW: dashboardWidget.layout.maxW || getWidgetConfig(dashboardWidget.type)?.maxSize.w || 12,
            maxH: dashboardWidget.layout.maxH || getWidgetConfig(dashboardWidget.type)?.maxSize.h || 10
          },
          config: dashboardWidget.config,
          priority: dashboardWidget.priority,
          enabled: dashboardWidget.enabled
        }))
      
      setWidgets(newWidgets)
    } catch (err) {
      console.error('Failed to fetch today\'s widgets:', err)
      setDashboardError('Failed to load dashboard configuration')
      // Fallback to default widgets
      setWidgets([
        {
          id: 'everydayTaskList-1',
          type: 'everydayTaskList',
          layout: { 
            i: 'everydayTaskList-1', 
            x: 0, y: 0, 
            w: getWidgetConfig('everydayTaskList')?.defaultSize.w || 10, 
            h: getWidgetConfig('everydayTaskList')?.defaultSize.h || 8,
            minW: getWidgetConfig('everydayTaskList')?.minSize.w || 8,
            minH: getWidgetConfig('everydayTaskList')?.minSize.h || 8,
            maxW: getWidgetConfig('everydayTaskList')?.maxSize.w || 12,
            maxH: getWidgetConfig('everydayTaskList')?.maxSize.h || 10
          }
        }
      ])
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

  const layouts = widgets.reduce((acc: Record<string, Layout>, widget: Widget) => {
    acc[widget.id] = widget.layout
    return acc
  }, {} as Record<string, Layout>)

  // Find empty space for new widget
  const findEmptyPosition = (widgetId: string): { x: number; y: number } | null => {
    const config = getWidgetConfig(widgetId)
    if (!config) return null
    
    const widgetWidth = config.defaultSize.w
    const widgetHeight = config.defaultSize.h
    const gridCols = GRID_CONFIG.cols.lg
    const viewportHeight = window.innerHeight
    const headerHeight = getHeaderHeight()
    const padding = GRID_CONFIG.containerPadding[0] * 2
    const availableHeight = viewportHeight - headerHeight - padding
    const maxRows = Math.floor(availableHeight / GRID_CONFIG.rowHeight)
    
    // Create a grid to track occupied spaces
    const occupiedSpaces = new Set<string>()
    widgets.forEach((widget: Widget) => {
      for (let x = widget.layout.x; x < widget.layout.x + widget.layout.w; x++) {
        for (let y = widget.layout.y; y < widget.layout.y + widget.layout.h; y++) {
          occupiedSpaces.add(`${x},${y}`)
        }
      }
    })

    // Try to find an empty space within boundaries
    for (let y = 0; y < Math.min(GRID_CONFIG.maxSearchDepth, maxRows - widgetHeight); y++) {
      for (let x = 0; x <= gridCols - widgetWidth; x++) {
        let canPlace = true
        for (let checkX = x; checkX < x + widgetWidth && canPlace; checkX++) {
          for (let checkY = y; checkY < y + widgetHeight && canPlace; checkY++) {
            if (occupiedSpaces.has(`${checkX},${checkY}`)) {
              canPlace = false
            }
          }
        }
        if (canPlace) {
          return { x, y }
        }
      }
    }
    return null
  }

  // Use the utility function from grid config for constraining layouts
  const constrainLayout = (layout: Layout): Layout => {
    // Calculate max rows based on viewport height minus header and padding
    const viewportHeight = window.innerHeight
    const headerHeight = getHeaderHeight()
    const padding = GRID_CONFIG.containerPadding[0] * 2
    const availableHeight = viewportHeight - headerHeight - padding
    const maxRows = Math.floor(availableHeight / GRID_CONFIG.rowHeight)
    
    // Constrain the layout
    const maxCols = GRID_CONFIG.cols.lg
    
    // Constrain x position (left/right boundaries)
    const constrainedX = Math.max(0, Math.min(layout.x, maxCols - layout.w))
    
    // Constrain y position (top/bottom boundaries)
    const constrainedY = Math.max(0, Math.min(layout.y, maxRows - layout.h))
    
    // Constrain width
    const maxWidth = maxCols - constrainedX
    const constrainedW = Math.max(1, Math.min(layout.w, maxWidth))
    
    // Constrain height
    const maxHeight = maxRows - constrainedY
    const constrainedH = Math.max(1, Math.min(layout.h, maxHeight))
    
    return {
      ...layout,
      x: constrainedX,
      y: constrainedY,
      w: constrainedW,
      h: constrainedH
    }
  }

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

  const onDragStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes dragging
    applyConstraints(layout)
  }

  const onResizeStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes resizing
    applyConstraints(layout)
  }

  const applyConstraints = (layout: Layout[]) => {
    const constrainedLayout = layout.map(constrainLayout)
    
    // Debug: Log the constraint calculations
    const viewportHeight = window.innerHeight
    const headerHeight = getHeaderHeight()
    const padding = GRID_CONFIG.containerPadding[0] * 2
    const availableHeight = viewportHeight - headerHeight - padding
    const maxRows = Math.floor(availableHeight / GRID_CONFIG.rowHeight)
    
    console.log('Boundary Debug:', {
      viewportHeight,
      headerHeight,
      padding,
      availableHeight,
      rowHeight: GRID_CONFIG.rowHeight,
      maxRows,
      layouts: layout.map(l => ({ id: l.i, x: l.x, y: l.y, w: l.w, h: l.h }))
    })
    
    // Check if any layout was constrained (position or size changed)
    const wasConstrained = layout.some((original, index) => {
      const constrained = constrainedLayout[index]
      return original.x !== constrained.x || 
             original.y !== constrained.y || 
             original.w !== constrained.w || 
             original.h !== constrained.h
    })
    
    setWidgets((prev: Widget[]) => 
      prev.map((widget: Widget) => {
        const newLayout = constrainedLayout.find(l => l.i === widget.id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
    
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
    const config = getWidgetConfig(widgetId)
    
    if (!config) {
      alert('Widget configuration not found.')
      return
    }
    
    const position = findEmptyPosition(widgetId)
    
    if (!position) {
      alert('No space available for new widget. Please remove or resize existing widgets.')
      return
    }

    const newLayout = {
      i: `${widgetId}-${Date.now()}`,
      x: position.x,
      y: position.y,
      w: config.defaultSize.w,
      h: config.defaultSize.h,
      minW: config.minSize.w,
      minH: config.minSize.h,
      maxW: config.maxSize.w,
      maxH: config.maxSize.h
    }

    // Apply constraints to the new widget layout
    const constrainedLayout = constrainLayout(newLayout)

    const newWidget: Widget = {
      id: `${widgetId}-${Date.now()}`,
      type: widgetId,
      layout: constrainedLayout
    }
    setWidgets((prev: Widget[]) => [...prev, newWidget])
  }

  const removeWidget = (id: string) => {
    const widget = widgets.find(w => w.id === id)
    const widgetType = widget?.type || 'widget'
    
    if (confirm(`Are you sure you want to remove this ${widgetType} widget?`)) {
      setWidgets((prev: Widget[]) => prev.filter((widget: Widget) => widget.id !== id))
    }
  }

  const renderWidget = (widget: Widget) => {
    const config = getWidgetConfig(widget.type)
    
    switch (widget.type) {
      case 'reminder':
        return (
          <ReminderWidget 
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'webSummary':
      case 'summary': // Keep backward compatibility
        return (
          <WebSummaryWidget
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'webSearch':
        return (
          <WebSearchWidget
            onRemove={() => removeWidget(widget.id)}
            config={widget.config}
            scheduledItem={widget.scheduledItem}
          />
        );
      default:
        // For unimplemented widgets, show BaseWidget with placeholder content
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
      
      <div className="flex-1 overflow-hidden">
        <ResponsiveGridLayout
          className={`layout h-full ${showGridLines ? 'show-grid-lines' : ''}`}
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
