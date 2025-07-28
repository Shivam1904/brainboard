// Grid configuration that can be shared between TypeScript and CSS
export const GRID_CONFIG = {
  // Grid layout settings
  cols: {
    lg: 40, // Number of columns for large screens
  },
  rowHeight: 40, // Height of each grid row in pixels
  margin: [0, 0] as [number, number], // Margin between grid items [vertical, horizontal]
  containerPadding: [8, 8] as [number, number], // Padding around the grid container
  
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