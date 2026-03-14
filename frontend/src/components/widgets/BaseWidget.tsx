import { ReactNode } from 'react'
import { Trash2, RefreshCw, ChevronUp, ChevronDown } from 'lucide-react'

interface BaseWidgetProps {
  title: string
  icon?: string
  onRemove: () => void
  onRefresh?: () => void
  loading?: boolean
  children: ReactNode
  isExpanded?: boolean
  onToggleExpand?: () => void
  hideTitle?: boolean
}

const BaseWidget = ({
  title,
  onRemove,
  onRefresh,
  loading = false,
  children,
  isExpanded = true,
  onToggleExpand,
  hideTitle = false
}: BaseWidgetProps) => {
  return (
    <div className={`h-full flex flex-col`}>
      <div className="flex h-full flex-col mt-6">
        {/* Header with title and drag handle - always visible */}
        <div className="absolute top-0 left-0 right-0 flex items-center justify-between z-10 px-2">
          {!hideTitle && <div className="text-sm font-medium text-muted-foreground truncate">{title}</div>}
          {hideTitle && <div />}
          <div className="flex items-center">
            <div className="widget-drag-handle items-center justify-end w-full">
              <div
                className="flex-1 min-h-[24px] cursor-move mx-4 flex items-center justify-end text-muted-foreground/50 hover:text-muted-foreground/80 transition-colors"
                title="Drag to move widget"
              >
                <span className="text-xs select-none">⋮⋮</span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {onToggleExpand && (
                <button
                  onClick={onToggleExpand}
                  className="text-muted-foreground hover:text-primary transition-colors p-2 rounded hover:bg-primary/10 -m-1"
                  title={isExpanded ? "Collapse" : "Expand"}
                >
                  {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
              )}
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
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-hidden min-h-0 mb-2">
          {isExpanded && (
            <div className="flex h-full flex-col">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default BaseWidget
