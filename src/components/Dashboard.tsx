import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import ReminderWidget from './widgets/ReminderWidget'
import WebSummaryWidget from './widgets/WebSummaryWidget'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import CalendarWidget from './widgets/CalendarWidget'
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
import { dashboardService } from '../services/api'
import { 
  TodayWidgetsResponse, 
  BaseWidget as WidgetData, 
  WidgetType
} from '../types'
import { getDummyTodayWidgets } from '../data/dashboardDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget';

const ResponsiveGridLayout = WidthProvider(Responsive)

interface Widget {
  id: string
  type: WidgetType
  layout: Layout
  config?: Record<string, any>
  priority?: number
  enabled?: boolean
  widgetData: WidgetData
}

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
      
      // Convert API widget data to internal widget format
      const newWidgets: Widget[] = [];
      // data.widgets = data.widgets.slice(0,2);
      data.widgets.push( dummyData.widgets[3] );
      
      for (const widgetData of data.widgets) {
        // Map API widget types to config widget IDs
        const getConfigWidgetId = (apiType: string): string => {
          const typeMapping: Record<string, string> = {
            'todo': 'everydayTaskList',
            'habittracker': 'habitListTracker',
            'websearch': 'webSearch',
            'websummary': 'webSearch', // Map to webSearch for now
            'calendar': 'calendar',
            'reminder': 'reminders',
            'allSchedules': 'allSchedules'
          };
          return typeMapping[apiType] || apiType;
        };

        const configWidgetId = getConfigWidgetId(widgetData.type);
        const defaultConfig = getWidgetConfig(configWidgetId);
        
        if (!defaultConfig) {
          console.warn(`No widget config found for type: ${widgetData.type} (mapped to: ${configWidgetId})`);
          continue; // Skip widgets without config
        }

        // Find empty position for this widget (considering already placed widgets)
        const position = findEmptyPosition(configWidgetId, newWidgets);

        console.log(`Placing widget ${widgetData.title} at position (${position.x}, ${position.y}) with size (${defaultConfig.defaultSize.w}, ${defaultConfig.defaultSize.h})`);

        const layout: Layout = {
          i: widgetData.id,
          x: position.x,
          y: position.y,
          w: defaultConfig.defaultSize.w,
          h: defaultConfig.defaultSize.h,
          minW: defaultConfig.minSize.w,
          minH: defaultConfig.minSize.h,
          maxW: defaultConfig.maxSize.w,
          maxH: defaultConfig.maxSize.h
        };

        newWidgets.push({
          id: widgetData.id,
          type: widgetData.type,
          layout,
          config: widgetData.settings,
          priority: widgetData.importance || undefined,
          enabled: true, // All widgets from API are enabled by default
          widgetData
        });
      }
      setWidgets(newWidgets)
    } catch (err) {
      console.error('Failed to fetch today\'s widgets:', err)
      setDashboardError('Failed to load dashboard configuration')
      // Fallback to default widgets
      setWidgets([
        {
          id: 'todo-1',
          type: 'todo',
          layout: { 
            i: 'todo-1', 
            x: 0, y: 0, 
            w: getWidgetConfig('todo')?.defaultSize.w || 6, 
            h: getWidgetConfig('todo')?.defaultSize.h || 4,
            minW: getWidgetConfig('todo')?.minSize.w || 1,
            minH: getWidgetConfig('todo')?.minSize.h || 1,
            maxW: getWidgetConfig('todo')?.maxSize.w || 12,
            maxH: getWidgetConfig('todo')?.maxSize.h || 10
          },
          config: {},
          priority: undefined,
          enabled: true,
          widgetData: {
            id: 'todo-1',
            type: 'todo',
            title: 'Default Todo Widget',
            size: 'medium',
            category: 'productivity',
            importance: 3,
            frequency: 'daily',
            settings: {},
            data: {
              tasks: [],
              stats: {
                total_tasks: 0,
                completed_tasks: 0,
                pending_tasks: 0,
                completion_rate: 0
              }
            }
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

  // Find empty space for new widget - fills rows horizontally first, then moves to next row
  const findEmptyPosition = (widgetId: string, existingWidgets: Widget[] = widgets): { x: number; y: number } => {
    const config = getWidgetConfig(widgetId)
    if (!config) return { x: 0, y: 0 } // Fallback position
    
    const widgetWidth = config.defaultSize.w
    const widgetHeight = config.defaultSize.h
    const gridCols = GRID_CONFIG.cols.lg
    
    // Create a grid to track occupied spaces
    const occupiedSpaces = new Set<string>()
    existingWidgets.forEach((widget: Widget) => {
      for (let x = widget.layout.x; x < widget.layout.x + widget.layout.w; x++) {
        for (let y = widget.layout.y; y < widget.layout.y + widget.layout.h; y++) {
          occupiedSpaces.add(`${x},${y}`)
        }
      }
    })

    console.log(`Finding position for widget ${widgetId} (${widgetWidth}x${widgetHeight}), existing widgets: ${existingWidgets.length}, occupied spaces: ${occupiedSpaces.size}`);

    // Find the highest Y position of any existing widget
    const maxExistingY = existingWidgets.length > 0 
      ? Math.max(...existingWidgets.map(w => w.layout.y + w.layout.h))
      : 0
    
    // Start from row 0 and work our way down systematically
    let currentRow = 0
    const maxSearchRows = Math.max(maxExistingY + 50, 100) // Search at least 100 rows or 50 rows past existing widgets
    
    while (currentRow < maxSearchRows) {
      // Try to place the widget in the current row, starting from x=0
      for (let x = 0; x <= gridCols - widgetWidth; x++) {
        let canPlace = true
        
        // Check if the widget can fit at this position
        for (let checkX = x; checkX < x + widgetWidth && canPlace; checkX++) {
          for (let checkY = currentRow; checkY < currentRow + widgetHeight && canPlace; checkY++) {
            if (occupiedSpaces.has(`${checkX},${checkY}`)) {
              canPlace = false
              break
            }
          }
        }
        
        if (canPlace) {
          console.log(`Found position for widget ${widgetId} at (${x}, ${currentRow})`);
          return { x, y: currentRow }
        }
      }
      
      // If we can't place the widget in this row, move to the next row
      currentRow++
    }
    
    // If we've searched all rows and still can't find a place, place it at the end
    // This should never happen with unlimited vertical space, but just in case
    console.log(`No empty space found after searching ${maxSearchRows} rows, placing widget at (0, ${maxSearchRows})`);
    return { x: 0, y: maxSearchRows }
  }

  // Use the utility function from grid config for constraining layouts
  const constrainLayout = (layout: Layout): Layout => {
    // Constrain the layout horizontally only - allow unlimited vertical placement
    const maxCols = GRID_CONFIG.cols.lg
    
    // Constrain x position (left/right boundaries)
    const constrainedX = Math.max(0, Math.min(layout.x, maxCols - layout.w))
    
    // Don't constrain y position - allow unlimited vertical placement
    const constrainedY = Math.max(0, layout.y) // Only ensure y is not negative
    
    // Constrain width
    const maxWidth = maxCols - constrainedX
    const constrainedW = Math.max(1, Math.min(layout.w, maxWidth))
    
    // Don't constrain height - allow widgets to be as tall as needed
    const constrainedH = Math.max(1, layout.h)
    
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

  // Save dashboard layout to API
  const saveDashboardLayout = async (widgets: Widget[]) => {
    try {
      const dashboardLayout = {
        widgets: widgets.map(widget => ({
          id: widget.id,
          type: widget.type,
          layout: {
            x: widget.layout.x,
            y: widget.layout.y,
            w: widget.layout.w,
            h: widget.layout.h,
            minW: widget.layout.minW,
            minH: widget.layout.minH,
            maxW: widget.layout.maxW,
            maxH: widget.layout.maxH
          },
          config: widget.config,
          priority: widget.priority,
          enabled: widget.enabled
        })),
        layout_version: '1.0',
        last_updated: new Date().toISOString()
      };

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
    const constrainedLayout = layout.map(constrainLayout)
    
    // Debug: Log the constraint calculations (horizontal only now)
    console.log('Boundary Debug:', {
      maxCols: GRID_CONFIG.cols.lg,
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
    // Map config widget IDs to API widget types for new widgets
    const getApiWidgetType = (configId: string): WidgetType => {
      const reverseMapping: Record<string, WidgetType> = {
        'everydayTaskList': 'todo',
        'habitListTracker': 'habittracker',
        'webSearch': 'websearch',
        'calendar': 'calendar',
        'reminders': 'reminder',
        'allSchedules': 'allSchedules'
      };
      return reverseMapping[configId] || 'todo';
    };

    const config = getWidgetConfig(widgetId)
    
    if (!config) {
      alert('Widget configuration not found.')
      return
    }
    
    const position = findEmptyPosition(widgetId)

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

    // Create default widget data based on type
    const apiWidgetType = getApiWidgetType(widgetId);
    const defaultWidgetData: WidgetData = {
      id: `${widgetId}-${Date.now()}`,
      type: apiWidgetType,
      title: config.title || widgetId,
      size: 'medium',
      category: 'productivity',
      importance: 3,
      frequency: 'daily',
      settings: {},
      data: {
        tasks: [],
        stats: {
          total_tasks: 0,
          completed_tasks: 0,
          pending_tasks: 0,
          completion_rate: 0
        }
      }
    }

    const newWidget: Widget = {
      id: `${widgetId}-${Date.now()}`,
      type: apiWidgetType,
      layout: constrainedLayout,
      config: {},
      priority: undefined,
      enabled: true,
      widgetData: defaultWidgetData
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
    // Map API widget types to config widget IDs
    const getConfigWidgetId = (apiType: string): string => {
      const typeMapping: Record<string, string> = {
        'todo': 'everydayTaskList',
        'habittracker': 'habitListTracker',
        'websearch': 'webSearch',
        'websummary': 'webSearch', // Map to webSearch for now
        'calendar': 'calendar',
        'reminder': 'reminders',
        'allSchedules': 'allSchedules'
      };
      return typeMapping[apiType] || apiType;
    };

    const configWidgetId = getConfigWidgetId(widget.type);
    const config = getWidgetConfig(configWidgetId)
    
    switch (widget.type) {
      case 'reminder':
        return (
          <ReminderWidget 
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'websummary':
        return (
          <WebSummaryWidget
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'websearch':
        return (
          <WebSearchWidget
            onRemove={() => removeWidget(widget.id)}
            config={widget.config}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            onRemove={() => removeWidget(widget.id)}
            config={widget.config}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
            onRemove={() => removeWidget(widget.id)}
            config={widget.config}
          />
        );
      case 'todo':
        return (
          <TaskListWidget
            onRemove={() => removeWidget(widget.id)}
            config={widget.config}
          />
        );
      case 'habittracker':
        return (
          <BaseWidget
            title={config?.title || "Habit Tracker"}
            icon={config?.icon || "📊"}
            onRemove={() => removeWidget(widget.id)}
          >
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="text-4xl mb-2">{config?.icon || '📊'}</div>
              <h3 className="font-medium mb-2">{config?.title || 'Habit Tracker'}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {config?.description || 'Track your daily habits and build streaks'}
              </p>
              <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                Coming Soon
              </div>
            </div>
          </BaseWidget>
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
