import { useState } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import ReminderWidget from './widgets/ReminderWidget'
import WebSummaryWidget from './widgets/WebSummaryWidget'
import AddWidgetButton from './AddWidgetButton'

const ResponsiveGridLayout = WidthProvider(Responsive)

interface Widget {
  id: string
  type: 'reminder' | 'summary'
  layout: Layout
}

const Dashboard = () => {
  const [widgets, setWidgets] = useState<Widget[]>([
    {
      id: 'reminder-1',
      type: 'reminder',
      layout: { i: 'reminder-1', x: 0, y: 0, w: 6, h: 4, minW: 4, minH: 3 }
    },
    {
      id: 'summary-1', 
      type: 'summary',
      layout: { i: 'summary-1', x: 6, y: 0, w: 6, h: 4, minW: 4, minH: 3 }
    }
  ])

  const layouts = widgets.reduce((acc, widget) => {
    acc[widget.id] = widget.layout
    return acc
  }, {} as Record<string, Layout>)

  const onLayoutChange = (layout: Layout[]) => {
    setWidgets(prev => 
      prev.map(widget => {
        const newLayout = layout.find(l => l.i === widget.id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
  }

  const addWidget = (type: 'reminder' | 'summary') => {
    const newWidget: Widget = {
      id: `${type}-${Date.now()}`,
      type,
      layout: {
        i: `${type}-${Date.now()}`,
        x: 0,
        y: 0,
        w: 6,
        h: 4,
        minW: 4,
        minH: 3
      }
    }
    setWidgets(prev => [...prev, newWidget])
  }

  const removeWidget = (id: string) => {
    setWidgets(prev => prev.filter(widget => widget.id !== id))
  }

  const renderWidget = (widget: Widget) => {
    switch (widget.type) {
      case 'reminder':
        return (
          <ReminderWidget 
            key={widget.id}
            id={widget.id}
            onRemove={() => removeWidget(widget.id)}
          />
        )
      case 'summary':
        return (
          <WebSummaryWidget
            key={widget.id}
            id={widget.id}
            onRemove={() => removeWidget(widget.id)}
          />
        )
      default:
        return <div>Unknown widget type</div>
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
        rowHeight={60}
        onLayoutChange={onLayoutChange}
        isDraggable={true}
        isResizable={true}
        margin={[16, 16]}
      >
        {widgets.map(renderWidget)}
      </ResponsiveGridLayout>
    </div>
  )
}

export default Dashboard
