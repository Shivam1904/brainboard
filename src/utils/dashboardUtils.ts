import { Layout } from 'react-grid-layout'
import { getWidgetConfig, getApiTypeToConfigMapping, getConfigToApiTypeMapping } from '../config/widgets'
import { GRID_CONFIG } from '../config/grid'
import { 
  TodayWidgetsResponse, 
  BaseWidget as WidgetData, 
  WidgetType,
  WidgetSize,
  WidgetImportance,
  WidgetFrequency
} from '../types'

export interface Widget {
  id: string
  daily_widget_id: string
  type: WidgetType
  layout: Layout
  config?: Record<string, any>
  priority?: number
  enabled?: boolean
  widgetData: WidgetData
}

export interface Position {
  x: number
  y: number
}

/**
 * Creates a set of occupied grid spaces from existing widgets
 */
export const createOccupiedSpaces = (existingWidgets: Widget[]): Set<string> => {
  const occupiedSpaces = new Set<string>()
  existingWidgets.forEach((widget: Widget) => {
    for (let x = widget.layout.x; x < widget.layout.x + widget.layout.w; x++) {
      for (let y = widget.layout.y; y < widget.layout.y + widget.layout.h; y++) {
        occupiedSpaces.add(`${x},${y}`)
      }
    }
  })
  return occupiedSpaces
}

/**
 * Checks if a widget can be placed at a specific position
 */
export const canPlaceWidgetAt = (
  x: number, 
  y: number, 
  width: number, 
  height: number, 
  occupiedSpaces: Set<string>
): boolean => {
  for (let checkX = x; checkX < x + width; checkX++) {
    for (let checkY = y; checkY < y + height; checkY++) {
      if (occupiedSpaces.has(`${checkX},${checkY}`)) {
        return false
      }
    }
  }
  return true
}

/**
 * Finds the highest Y position of any existing widget
 */
export const getMaxExistingY = (existingWidgets: Widget[]): number => {
  return existingWidgets.length > 0 
    ? Math.max(...existingWidgets.map(w => w.layout.y + w.layout.h))
    : 0
}

/**
 * Finds empty space for new widget - fills rows horizontally first, then moves to next row
 */
export const findEmptyPosition = (
  widgetId: string, 
  existingWidgets: Widget[] = []
): Position => {
  const config = getWidgetConfig(widgetId)
  if (!config) return { x: 0, y: 0 } // Fallback position
  
  const widgetWidth = config.defaultSize.w
  const widgetHeight = config.defaultSize.h
  const gridCols = GRID_CONFIG.cols.lg
  
  // Create a grid to track occupied spaces
  const occupiedSpaces = createOccupiedSpaces(existingWidgets)

  console.log(`Finding position for widget ${widgetId} (${widgetWidth}x${widgetHeight}), existing widgets: ${existingWidgets.length}, occupied spaces: ${occupiedSpaces.size}`)

  // Find the highest Y position of any existing widget
  const maxExistingY = getMaxExistingY(existingWidgets)
  
  // Start from row 0 and work our way down systematically
  let currentRow = 0
  const maxSearchRows = Math.max(maxExistingY + 50, 100) // Search at least 100 rows or 50 rows past existing widgets
  
  while (currentRow < maxSearchRows) {
    // Try to place the widget in the current row, starting from x=0
    for (let x = 0; x <= gridCols - widgetWidth; x++) {
      if (canPlaceWidgetAt(x, currentRow, widgetWidth, widgetHeight, occupiedSpaces)) {
        console.log(`Found position for widget ${widgetId} at (${x}, ${currentRow})`)
        return { x, y: currentRow }
      }
    }
    
    // If we can't place the widget in this row, move to the next row
    currentRow++
  }
  
  // If we've searched all rows and still can't find a place, place it at the end
  // This should never happen with unlimited vertical space, but just in case
  console.log(`No empty space found after searching ${maxSearchRows} rows, placing widget at (0, ${maxSearchRows})`)
  return { x: 0, y: maxSearchRows }
}

/**
 * Constrains layout to grid boundaries
 */
export const constrainLayout = (layout: Layout): Layout => {
  // Constrain the layout horizontally only - allow unlimited vertical placement
  const maxCols = GRID_CONFIG.cols.lg
  
  // Constrain x position (left/right boundaries)
  const constrainedX = Math.max(0, Math.min(layout.x, maxCols - layout.w))
  
  // Don't constrain y position - allow unlimited vertical placement
  const constrainedY = Math.max(0, layout.y) // Only ensure y is not negative
  
  // Constrain width
  const maxWidth = maxCols - constrainedX
  const constrainedW = Math.max(1, Math.min(layout.w, maxWidth))
  
  // Don't constrain height - allow widgets to be as tall as needed
  const constrainedH = Math.max(1, layout.h)
  
  return {
    ...layout,
    x: constrainedX,
    y: constrainedY,
    w: constrainedW,
    h: constrainedH
  }
}

/**
 * Applies constraints to multiple layouts and returns debug information
 */
export const applyConstraintsToLayouts = (layouts: Layout[]) => {
  const constrainedLayout = layouts.map(constrainLayout)
  
  // Debug: Log the constraint calculations (horizontal only now)
  console.log('Boundary Debug:', {
    maxCols: GRID_CONFIG.cols.lg,
    layouts: layouts.map(l => ({ id: l.i, x: l.x, y: l.y, w: l.w, h: l.h }))
  })
  
  // Check if any layout was constrained (position or size changed)
  const wasConstrained = layouts.some((original, index) => {
    const constrained = constrainedLayout[index]
    return original.x !== constrained.x || 
           original.y !== constrained.y || 
           original.w !== constrained.w || 
           original.h !== constrained.h
  })
  
  return {
    constrainedLayout,
    wasConstrained
  }
}

/**
 * Converts API widget data to internal widget format
 */
export const convertApiWidgetsToInternal = (data: TodayWidgetsResponse): Widget[] => {
  const newWidgets: Widget[] = []
  
  for (const apiWidget of data.widgets) {
    // Map API widget types to config widget IDs using centralized mapping
    const typeMapping = getApiTypeToConfigMapping()
    const configWidgetId = typeMapping[apiWidget.widget_type] || apiWidget.widget_type
    const defaultConfig = getWidgetConfig(configWidgetId)
    
    if (!defaultConfig) {
      console.warn(`No widget config found for type: ${apiWidget.widget_type} (mapped to: ${configWidgetId})`)
      continue // Skip widgets without config
    }

    // Find empty position for this widget (considering already placed widgets)
    const position = findEmptyPosition(configWidgetId, newWidgets)

    console.log(`Placing widget ${apiWidget.title} at position (${position.x}, ${position.y}) with size (${defaultConfig.defaultSize.w}, ${defaultConfig.defaultSize.h})`)

    const layout: Layout = {
      i: apiWidget.id,
      x: position.x,
      y: position.y,
      w: defaultConfig.defaultSize.w,
      h: defaultConfig.defaultSize.h,
      minW: defaultConfig.minSize.w,
      minH: defaultConfig.minSize.h,
      maxW: defaultConfig.maxSize.w,
      maxH: defaultConfig.maxSize.h
    }

    // Convert API widget to internal BaseWidget format
    const widgetData: WidgetData = {
      id: apiWidget.id,
      type: apiWidget.widget_type as WidgetType,
      title: apiWidget.title,
      size: 'medium' as WidgetSize, // Default size, could be derived from grid_position if available
      category: apiWidget.category,
      importance: apiWidget.importance as WidgetImportance,
      frequency: apiWidget.frequency as WidgetFrequency,
      settings: apiWidget.settings || {},
      data: {} as any // Widget-specific data will be fetched separately by each widget
    }

    newWidgets.push({
      id: apiWidget.id,
      daily_widget_id: apiWidget.daily_widget_id,
      type: apiWidget.widget_type as WidgetType,
      layout,
      config: apiWidget.settings || {},
      priority: apiWidget.importance,
      enabled: true, // All widgets from API are enabled by default
      widgetData
    })
  }
  
  return newWidgets
}

/**
 * Creates default widget data for new widgets
 */
export const createDefaultWidgetData = (widgetId: string, config: any): WidgetData => {
  // Map config widget IDs to API widget types for new widgets
  const typeMapping = getConfigToApiTypeMapping()
  const apiWidgetType = (typeMapping[widgetId] || 'todo') as WidgetType
  
  return {
    id: `${widgetId}-${Date.now()}`,
    type: apiWidgetType,
    title: config.title || widgetId,
    size: 'medium',
    category: 'productivity',
    importance: 3,
    frequency: 'daily',
    settings: {},
    data: {
      tasks: [],
      stats: {
        total_tasks: 0,
        completed_tasks: 0,
        pending_tasks: 0,
        completion_rate: 0,
        tasks_by_priority: {},
        tasks_by_category: {}
      }
    }
  }
}

/**
 * Creates a new widget with proper layout and configuration
 */
export const createNewWidget = (widgetId: string): Widget | null => {
  const config = getWidgetConfig(widgetId)
  
  if (!config) {
    console.error('Widget configuration not found for:', widgetId)
    return null
  }
  
  const position = findEmptyPosition(widgetId)

  const newLayout = {
    i: `${widgetId}-${Date.now()}`,
    x: position.x,
    y: position.y,
    w: config.defaultSize.w,
    h: config.defaultSize.h,
    minW: config.minSize.w,
    minH: config.minSize.h,
    maxW: config.maxSize.w,
    maxH: config.maxSize.h
  }

  // Apply constraints to the new widget layout
  const constrainedLayout = constrainLayout(newLayout)

  // Create default widget data based on type
  const defaultWidgetData = createDefaultWidgetData(widgetId, config)
  const typeMapping = getConfigToApiTypeMapping()
  const apiWidgetType = (typeMapping[widgetId] || 'todo') as WidgetType

  return {
    id: `${widgetId}-${Date.now()}`,
    type: apiWidgetType,
    layout: constrainedLayout,
    config: {},
    priority: undefined,
    enabled: true,
    widgetData: defaultWidgetData
  }
}

/**
 * Prepares dashboard layout data for API saving
 */
export const prepareDashboardLayoutForSave = (widgets: Widget[]) => {
  return {
    widgets: widgets.map(widget => ({
      id: widget.id,
      type: widget.type,
      layout: {
        x: widget.layout.x,
        y: widget.layout.y,
        w: widget.layout.w,
        h: widget.layout.h,
        minW: widget.layout.minW,
        minH: widget.layout.minH,
        maxW: widget.layout.maxW,
        maxH: widget.layout.maxH
      },
      config: widget.config,
      priority: widget.priority,
      enabled: widget.enabled
    })),
    layout_version: '1.0',
    last_updated: new Date().toISOString()
  }
}

/**
 * Maps API widget types to config widget IDs
 */
export const getConfigWidgetId = (apiType: string): string => {
  const typeMapping = getApiTypeToConfigMapping()
  return typeMapping[apiType] || apiType
}

/**
 * Creates layouts object from widgets array
 */
export const createLayoutsFromWidgets = (widgets: Widget[]): Record<string, Layout> => {
  return widgets.reduce((acc: Record<string, Layout>, widget: Widget) => {
    acc[widget.id] = widget.layout
    return acc
  }, {} as Record<string, Layout>)
} 