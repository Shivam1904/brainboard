import { useState } from 'react'
import { Plus } from 'lucide-react'

interface AddWidgetButtonProps {
  onAddWidget: (type: 'reminder' | 'summary') => void
}

const AddWidgetButton = ({ onAddWidget }: AddWidgetButtonProps) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleAddWidget = (type: 'reminder' | 'summary') => {
    onAddWidget(type)
    setIsOpen(false)
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
        <div className="absolute right-0 top-full mt-2 bg-card border rounded-md shadow-lg min-w-[160px] z-10">
          <div className="py-1">
            <button
              onClick={() => handleAddWidget('reminder')}
              className="w-full text-left px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              📝 Reminder Widget
            </button>
            <button
              onClick={() => handleAddWidget('summary')}
              className="w-full text-left px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              🔍 Web Summary Widget
            </button>
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
