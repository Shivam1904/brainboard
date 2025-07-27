import { ReactNode } from 'react'
import { Trash2 } from 'lucide-react'

interface BaseWidgetProps {
  title: string
  icon?: string
  onRemove: () => void
  children: ReactNode
  className?: string
}

const BaseWidget = ({ 
  title, 
  icon, 
  onRemove, 
  children, 
  className = "" 
}: BaseWidgetProps) => {
  return (
    <div className={`h-full bg-card border border-border rounded-lg shadow-sm flex flex-col ${className}`}>
      {/* Header with title and delete button */}
      <div className="flex items-center px-4 py-3 border-b border-border bg-card/50 rounded-t-lg">
        <h3 className="text-lg font-semibold text-card-foreground flex items-center gap-2">
          {icon && <span>{icon}</span>}
          {title}
        </h3>
        
        {/* Drag handle - ONLY this area is draggable */}
        <div 
          className="widget-drag-handle flex-1 min-h-[24px] cursor-move mx-4 flex items-center justify-center text-muted-foreground/50 hover:text-muted-foreground/80 transition-colors" 
          title="Drag to move widget"
        >
          <span className="text-xs select-none">⋮⋮</span>
        </div>
        
        <button
          onClick={onRemove}
          className="text-muted-foreground hover:text-destructive transition-colors p-2 rounded hover:bg-destructive/10 -m-1"
          title="Remove widget"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full p-4">
          {children}
        </div>
      </div>
    </div>
  )
}

export default BaseWidget
