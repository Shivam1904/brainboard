import { ReactNode, useState } from 'react'
import { Trash2, RefreshCw } from 'lucide-react'

interface BaseWidgetProps {
  title: string
  icon?: string
  onRemove: () => void
  onRefresh?: () => void
  loading?: boolean
  children: ReactNode
  className?: string
}

const BaseWidget = ({ 
  title, 
  icon, 
  onRemove, 
  onRefresh,
  loading = false,
  children, 
  className = "" 
}: BaseWidgetProps) => {
  const [hover, setHover] = useState(false);
  return (
    <div className={`h-full flex flex-col`}
     onMouseEnter={() => {
      setHover(true);
    }}
    onMouseLeave={() => {
      setHover(false);
    }}
    >
      <div className="relative flex h-full flex-col">
      {/* Header with title and delete button */}
      {hover && (<div className="absolute top-0 right-0 flex items-center px-2 py-1 bg-card/50 rounded-t-lg">
        <div className="widget-drag-handle items-center justify-end w-full">
          {/* Drag handle - ONLY this area is draggable */}
          {hover && (<div 
            className="flex-1 min-h-[24px] cursor-move mx-4 flex items-center justify-end text-muted-foreground/50 hover:text-muted-foreground/80 transition-colors" 
            title="Drag to move widget"
          >
            <span className="text-xs select-none">⋮⋮</span>
          </div>)}
        </div>
        <div className="flex items-center gap-1">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={loading}
              className="text-muted-foreground hover:text-primary transition-colors p-2 rounded hover:bg-primary/10 -m-1 disabled:opacity-50"
              title="Refresh data"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
          )}
            <button
              onClick={onRemove}
              className="text-muted-foreground hover:text-destructive transition-colors p-2 rounded hover:bg-destructive/10 -m-1"
              title="Remove widget"
            >
              <Trash2 size={16} />
            </button>
        </div>
      </div>)}

      {/* Content area */}
      <div className="flex-1 overflow-hidden min-h-0">
        <div className="flex h-full flex-col">
          {children}
        </div>
      </div>
      </div>
    </div>
  )
}

export default BaseWidget
