import { useState } from 'react'
import { Plus } from 'lucide-react'
import { getAllWidgets, getImplementedWidgets, WidgetConfig } from '../config/widgets'

interface AddWidgetButtonProps {
  onAddWidget: (widgetId: string) => void
  canAddWidget?: boolean
}

const AddWidgetButton = ({ onAddWidget }: AddWidgetButtonProps) => {
  const [isOpen, setIsOpen] = useState(false)
  
  // Get all widgets except "All Schedules" since it's automatically included
  const allWidgets = getAllWidgets().filter(widget => widget.id !== 'allSchedules')
  const implementedWidgets = getImplementedWidgets().filter(widget => widget.id !== 'allSchedules')
  
  const isImplemented = (widgetId: string) => 
    implementedWidgets.some(widget => widget.id === widgetId)

  const handleAddWidget = (widgetId: string) => {
    onAddWidget(widgetId)
    setIsOpen(false)
  }

  const renderWidget = (widget: WidgetConfig) => {
    const implemented = isImplemented(widget.id)
    
    return (
      <button
        key={widget.id}
        onClick={() => handleAddWidget(widget.id)}
        className={`w-full text-left px-3 py-2 text-sm transition-colors ${
          implemented 
            ? 'hover:bg-accent hover:text-accent-foreground cursor-pointer' 
            : 'hover:bg-muted/50 cursor-pointer opacity-75'
        }`}
        title={implemented ? `Add ${widget.title}` : `Add ${widget.title} (Coming soon)`}
      >
        <div className="flex items-start gap-2">
          <span className="text-base">{widget.icon}</span>
          <div className="flex-1">
            <div className="font-medium">{widget.title}</div>
            {!implemented && (
              <div className="text-xs text-muted-foreground mt-1">
                Coming soon - {widget.description}
              </div>
            )}
          </div>
        </div>
      </button>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        <Plus size={16} />
        Add Widget
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 bg-card border rounded-md shadow-lg min-w-[200px] max-h-[400px] overflow-y-auto z-10">
          <div className="py-1">
            {allWidgets.map(widget => renderWidget(widget))}
          </div>
        </div>
      )}

      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}

export default AddWidgetButton
