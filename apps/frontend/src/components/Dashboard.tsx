import { useState } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import ReminderWidget from './widgets/ReminderWidget'
import WebSummaryWidget from './widgets/WebSummaryWidget'
import BaseWidget from './widgets/BaseWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'

const ResponsiveGridLayout = WidthProvider(Responsive)

interface Widget {
  id: string
  type: string
  layout: Layout
}

const Dashboard = () => {
  const [widgets, setWidgets] = useState<Widget[]>([
    {
      id: 'reminder-1',
      type: 'reminder',
      layout: { 
        i: 'reminder-1', 
        x: 0, y: 0, 
        w: getWidgetConfig('reminder')?.defaultSize.w || 3, 
        h: getWidgetConfig('reminder')?.defaultSize.h || 4,
        minW: getWidgetConfig('reminder')?.minSize.w || 2,
        minH: getWidgetConfig('reminder')?.minSize.h || 3,
        maxW: getWidgetConfig('reminder')?.maxSize.w || 6,
        maxH: getWidgetConfig('reminder')?.maxSize.h || 8
      }
    },
    {
      id: 'summary-1', 
      type: 'webSummary',
      layout: { 
        i: 'summary-1', 
        x: 4, y: 0, 
        w: getWidgetConfig('webSummary')?.defaultSize.w || 4, 
        h: getWidgetConfig('webSummary')?.defaultSize.h || 4,
        minW: getWidgetConfig('webSummary')?.minSize.w || 3,
        minH: getWidgetConfig('webSummary')?.minSize.h || 3,
        maxW: getWidgetConfig('webSummary')?.maxSize.w || 8,
        maxH: getWidgetConfig('webSummary')?.maxSize.h || 6
      }
    }
  ])

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
    const gridCols = 12
    
    // Create a grid to track occupied spaces
    const occupiedSpaces = new Set<string>()
    widgets.forEach((widget: Widget) => {
      for (let x = widget.layout.x; x < widget.layout.x + widget.layout.w; x++) {
        for (let y = widget.layout.y; y < widget.layout.y + widget.layout.h; y++) {
          occupiedSpaces.add(`${x},${y}`)
        }
      }
    })

    // Try to find an empty space
    for (let y = 0; y < 20; y++) { // Limit search depth
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

  const onLayoutChange = (layout: Layout[]) => {
    setWidgets((prev: Widget[]) => 
      prev.map((widget: Widget) => {
        const newLayout = layout.find(l => l.i === widget.id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
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

    const newWidget: Widget = {
      id: `${widgetId}-${Date.now()}`,
      type: widgetId,
      layout: {
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

  return (
    <div className="w-full">
      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold">Your Dashboard</h2>
        <AddWidgetButton onAddWidget={addWidget} />
      </div>
      
      <ResponsiveGridLayout
        className="layout"
        layouts={{ lg: Object.values(layouts) }}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={80}
        margin={[16, 16]}
        containerPadding={[0, 0]}
        isDraggable={true}
        isResizable={true}
        preventCollision={false}
        compactType="vertical"
        useCSSTransforms={true}
        draggableHandle=".widget-drag-handle"
        onLayoutChange={onLayoutChange}
      >
        {widgets.map((widget: Widget) => (
          <div key={widget.layout.i} className="widget-container">
            {renderWidget(widget)}
          </div>
        ))}
      </ResponsiveGridLayout>
    </div>
  )
}

export default Dashboard
