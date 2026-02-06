// Grid configuration that can be shared between TypeScript and CSS
export const GRID_CONFIG = {
  // Grid layout settings
  cols: {
    lg: 40, // Number of columns for large screens
  },
  rowHeight: 32, // Height of each grid row in pixels
  margin: [5, 5] as [number, number], // Margin between grid items [vertical, horizontal]
  containerPadding: [5, 5] as [number, number], // Padding around the grid container

  // Breakpoints (for responsive design)
  breakpoints: {
    lg: 0, // Large screens and up
  },

  // Grid lines configuration
  gridLines: {
    opacity: 0.4, // Opacity of grid lines when shown
    color: 'hsl(var(--border))', // Color of grid lines
  },

  // Widget positioning
  maxSearchDepth: 20, // Maximum rows to search when finding empty space for new widgets
} as const

// Helper function to get CSS custom properties for grid
export const getGridCSSProperties = () => {
  return {
    '--grid-cols': GRID_CONFIG.cols.lg.toString(),
    '--grid-row-height': `${GRID_CONFIG.rowHeight}px`,
    '--grid-margin-vertical': `${GRID_CONFIG.margin[0]}px`,
    '--grid-margin-horizontal': `${GRID_CONFIG.margin[1]}px`,
    '--grid-container-padding-vertical': `${GRID_CONFIG.containerPadding[0]}px`,
    '--grid-container-padding-horizontal': `${GRID_CONFIG.containerPadding[1]}px`,
    '--grid-lines-opacity': GRID_CONFIG.gridLines.opacity.toString(),
  }
}

// Type for grid configuration
export type GridConfig = typeof GRID_CONFIG

// Helper functions for grid calculations
export const gridUtils = {
  // Calculate the width of a grid item in pixels
  getItemWidth: (cols: number, containerWidth: number, margin: number = GRID_CONFIG.margin[1]) => {
    return (containerWidth - (GRID_CONFIG.cols.lg + 1) * margin) / GRID_CONFIG.cols.lg * cols + (cols - 1) * margin
  },

  // Calculate the height of a grid item in pixels
  getItemHeight: (rows: number, margin: number = GRID_CONFIG.margin[0]) => {
    return rows * GRID_CONFIG.rowHeight + (rows - 1) * margin
  },

  // Check if a position is valid for a widget
  isValidPosition: (x: number, y: number, w: number, _h: number, maxCols: number = GRID_CONFIG.cols.lg) => {
    return x >= 0 && y >= 0 && x + w <= maxCols
  },

  // Calculate maximum available rows based on container height
  getMaxRows: (containerHeight: number, headerHeight: number = 80) => {
    const availableHeight = containerHeight - headerHeight - (GRID_CONFIG.containerPadding[0] * 2)
    return Math.floor(availableHeight / GRID_CONFIG.rowHeight)
  },

  // Constrain layout to grid boundaries
  constrainLayout: (layout: any, maxCols: number = GRID_CONFIG.cols.lg, maxRows?: number) => {
    if (!maxRows) {
      // Calculate max rows using the same logic as getMaxRows but inline to avoid circular reference
      const headerHeight = 80
      const availableHeight = window.innerHeight - headerHeight - (GRID_CONFIG.containerPadding[0] * 2)
      maxRows = Math.floor(availableHeight / GRID_CONFIG.rowHeight)
    }

    const constrainedX = Math.max(0, Math.min(layout.x, maxCols - layout.w))
    const constrainedY = Math.max(0, Math.min(layout.y, maxRows - layout.h))
    const maxWidth = maxCols - constrainedX
    const constrainedW = Math.max(1, Math.min(layout.w, maxWidth))
    const maxHeight = maxRows - constrainedY
    const constrainedH = Math.max(1, Math.min(layout.h, maxHeight))

    return {
      ...layout,
      x: constrainedX,
      y: constrainedY,
      w: constrainedW,
      h: constrainedH
    }
  }
}

// Find empty space for a new widget given the current widgets and grid constraints
export function findEmptyPosition({
  widgetId,
  widgets,
  getWidgetConfig,
  gridCols = GRID_CONFIG.cols.lg,
  maxRows = 100,
}: {
  widgetId: string,
  widgets: Array<{ layout: { x: number; y: number; w: number; h: number } }>,
  getWidgetConfig: (id: string) => any,
  gridCols?: number,
  maxRows?: number,
}): { x: number; y: number } | null {
  const config = getWidgetConfig(widgetId)
  if (!config) return null

  const widgetWidth = config.defaultSize.w
  const widgetHeight = config.defaultSize.h

  // Create a grid to track occupied spaces
  const occupiedSpaces = new Set<string>()
  widgets.forEach((widget) => {
    for (let x = widget.layout.x; x < widget.layout.x + widget.layout.w; x++) {
      for (let y = widget.layout.y; y < widget.layout.y + widget.layout.h; y++) {
        occupiedSpaces.add(`${x},${y}`)
      }
    }
  })

  // Try to find an empty space within boundaries
  for (let y = 0; y < Math.min(GRID_CONFIG.maxSearchDepth, maxRows - widgetHeight); y++) {
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