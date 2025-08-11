import { useState } from 'react'
import { Plus, Target, BarChart3, Eye } from 'lucide-react'
import { getAllWidgets, getImplementedWidgets, WidgetConfig } from '../config/widgets'
import AddWidgetForm from './AddWidgetForm'
import { dashboardService } from '../services/dashboard'

interface AddWidgetButtonProps {
  onAddWidget: (widgetId: string) => void
  canAddWidget?: boolean
  existingViewWidgets?: Array<any>
  refreshAllWidgets?: () => void
}

const AddWidgetButton = ({ onAddWidget,  existingViewWidgets = [], refreshAllWidgets }: AddWidgetButtonProps) => {
  const [isTrackerOpen, setIsTrackerOpen] = useState(false)
  const [isViewsOpen, setIsViewsOpen] = useState(false)
  const [selectedWidgetId, setSelectedWidgetId] = useState<string | null>(null)
  const [loading, setLoading] = useState<string | null>(null)
  
  // Get all widgets
  const allWidgets = getAllWidgets()
  const implementedWidgets = getImplementedWidgets()
  
  const isImplemented = (widgetId: string) => 
    implementedWidgets.some(widget => widget.id === widgetId)

  // Tracker widgets (calendar, weekchart) - permanent widgets
  const trackerWidgets = allWidgets.filter(widget => 
    ['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker'].includes(widget.id) && isImplemented(widget.id)
  )

  // View widgets (aiChat, allSchedules, moodTracker, notes, weatherWidget, simpleClock)
  const viewWidgets = allWidgets.filter(widget => 
    ['aiChat', 'allSchedules', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock'].includes(widget.id) && isImplemented(widget.id)
  )

  const handleAddMission = () => {
    setSelectedWidgetId('todo-task')
  }

  const handleTrackerSelect = (widgetId: string) => {
    setSelectedWidgetId(widgetId)
    setIsTrackerOpen(false)
  }

    const handleViewToggle = async (widgetId: string, isEnabled: boolean) => {
    setLoading(widgetId)
    try {
      const widgetConfig = allWidgets.find(w => w.id === widgetId)
      if (widgetConfig) {
        // Find existing widget of this type
        const existingWidget = existingViewWidgets.find(w => w.widget_type === widgetConfig.apiWidgetType)
        
        if (existingWidget) {
          // Update existing widget - only send the necessary fields
          await dashboardService.updateWidget(existingWidget.id, {
            widget_config: { 
              ...existingWidget.widget_config, // Preserve existing config
              visibility: isEnabled 
            }
          })
        } else if (isEnabled) {
          // Create new widget with visibility: true (first time creation)
          await dashboardService.createWidget({
            widget_type: widgetConfig.apiWidgetType,
            title: widgetConfig.title,
            description: widgetConfig.description,
            frequency: 'daily',
            importance: 0.7,
            category: 'utilities',
            is_permanent: true,
            widget_config: { visibility: true }
          })
        }
        
        // Force a refresh to get updated data
        onAddWidget('refresh')
      }
    } catch (err) {
      console.error('Failed to toggle view widget:', err)
      // Revert the checkbox state on error
      onAddWidget('refresh')
    } finally {
      setLoading(null)
    }
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

  const renderViewWidget = (widget: WidgetConfig) => {
    const isLoading = loading === widget.id
    // Check if widget exists and is visible - ensure proper boolean handling
    const existingWidget = existingViewWidgets.find(w => w.widget_type === widget.apiWidgetType)
    const isVisible = existingWidget?.widget_config?.visibility === true
    
    return (
      <div
        key={widget.id}
        className="flex items-center justify-between px-3 py-2 text-sm"
      >
        <div className="flex items-start gap-2 flex-1">
          <span className="text-base">{widget.icon}</span>
          <div className="flex-1">
            <div className="font-medium">{widget.title}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {widget.description}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isLoading && (
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          )}
          <input
            type="checkbox"
            checked={isVisible}
            onChange={(e) => handleViewToggle(widget.id, e.target.checked)}
            disabled={isLoading}
            className="rounded"
          />
        </div>
      </div>
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

        {/* Views Button */}
        <div className="relative">
          <button
            onClick={() => setIsViewsOpen(!isViewsOpen)}
            className="flex items-center gap-2 px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/90 transition-colors"
          >
            <Eye size={16} />
            Views
          </button>

          {isViewsOpen && (
            <div className="absolute right-0 top-full mt-2 bg-card border rounded-md shadow-lg min-w-[250px] max-h-[400px] overflow-y-auto z-10">
              <div className="py-1">
                {viewWidgets.map(widget => renderViewWidget(widget))}
              </div>
            </div>
          )}

          {isViewsOpen && (
            <div
              className="fixed inset-0 z-0"
              onClick={() => setIsViewsOpen(false)}
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
