import { useState } from 'react'
import { Target, BarChart3 } from 'lucide-react'
import { getAllWidgets, getImplementedWidgets, WidgetConfig } from '../config/widgets'
import AddWidgetForm from './AddWidgetForm'

interface AddWidgetButtonProps {
  onAddWidget: (widgetId: string) => void
  canAddWidget?: boolean
  existingViewWidgets?: Array<any>
  refreshAllWidgets?: () => void
}

const AddWidgetButton = ({ onAddWidget }: AddWidgetButtonProps) => {
  const [isTrackerOpen, setIsTrackerOpen] = useState(false)
  const [selectedWidgetId, setSelectedWidgetId] = useState<string | null>(null)

  // Get all widgets
  const allWidgets = getAllWidgets()
  const implementedWidgets = getImplementedWidgets()

  const isImplemented = (widgetId: string) =>
    implementedWidgets.some(widget => widget.id === widgetId)

  // Tracker widgets (calendar, weekchart) - permanent widgets
  const trackerWidgets = allWidgets.filter(widget =>
    ['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker'].includes(widget.id) && isImplemented(widget.id)
  )

  const handleAddMission = () => {
    setSelectedWidgetId('todo-task')
  }

  const handleTrackerSelect = (widgetId: string) => {
    setSelectedWidgetId(widgetId)
    setIsTrackerOpen(false)
  }

  const handleFormClose = () => {
    setSelectedWidgetId(null)
  }

  const handleFormSuccess = () => {
    onAddWidget('refresh')
    setSelectedWidgetId(null)
  }

  const renderTrackerWidget = (widget: WidgetConfig) => {
    return (
      <button
        key={widget.id}
        onClick={() => handleTrackerSelect(widget.id)}
        className="w-full text-left px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground cursor-pointer"
        title={`Add ${widget.title}`}
      >
        <div className="flex items-start gap-2">
          <span className="text-base">{widget.icon}</span>
          <div className="flex-1">
            <div className="font-medium">{widget.title}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {widget.description}
            </div>
          </div>
        </div>
      </button>
    )
  }

  return (
    <>
      <div className="flex gap-2">
        {/* Add Mission Button */}
        <button
          onClick={handleAddMission}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          <Target size={16} />
          Add Mission
        </button>

        {/* Add Tracker Button */}
        <div className="relative">
          <button
            onClick={() => setIsTrackerOpen(!isTrackerOpen)}
            className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
          >
            <BarChart3 size={16} />
            Add Tracker
          </button>

          {isTrackerOpen && (
            <div className="absolute right-0 top-full mt-2 bg-card border rounded-md shadow-lg min-w-[200px] max-h-[400px] overflow-y-auto z-10">
              <div className="py-1">
                {trackerWidgets.map(widget => renderTrackerWidget(widget))}
              </div>
            </div>
          )}

          {isTrackerOpen && (
            <div
              className="fixed inset-0 z-0"
              onClick={() => setIsTrackerOpen(false)}
            />
          )}
        </div>
      </div>

      {/* Add Widget Form Modal */}
      {selectedWidgetId && (
        <AddWidgetForm
          widgetId={selectedWidgetId}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </>
  )
}

export default AddWidgetButton
