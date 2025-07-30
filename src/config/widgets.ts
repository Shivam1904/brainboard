// Widget Configuration - API-Compatible
// These configs map directly to API widget types without conversions

export interface WidgetConfig {
  id: string;
  title: string;
  description: string;
  component: string;
  apiWidgetType: string; // Maps directly to API widget_type
  minSize: {
    w: number; // width in grid units
    h: number; // height in grid units
  };
  maxSize: {
    w: number;
    h: number;
  };
  defaultSize: {
    w: number;
    h: number;
  };
  deletable: boolean;
  resizable: boolean;
  category: 'productivity' | 'health' | 'job' | 'information' | 'entertainment' | 'utilities';
  icon?: string;
}

export const WIDGET_CONFIGS: Record<string, WidgetConfig> = {
  // TODO HABIT Widget
  'todo-habit': {
    id: 'todo-habit',
    apiWidgetType: 'todo-habit',
    title: 'Habit Tracker',
    description: 'Track daily habits and routines',
    component: 'TaskListWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 30, h: 36 },
    defaultSize: { w: 12, h: 15 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '🔄'
  },

  // TODO TASK Widget
  'todo-task': {
    id: 'todo-task',
    apiWidgetType: 'todo-task',
    title: 'Task List',
    description: 'Manage daily tasks and to-dos',
    component: 'TaskListWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 30, h: 36 },
    defaultSize: { w: 12, h: 15 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📋'
  },

  // TODO EVENT Widget
  'todo-event': {
    id: 'todo-event',
    apiWidgetType: 'todo-event',
    title: 'Event Tracker',
    description: 'Track events and appointments',
    component: 'TaskListWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 30, h: 36 },
    defaultSize: { w: 10, h: 6 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📅'
  },

  // ALARM Widget
  alarm: {
    id: 'alarm',
    apiWidgetType: 'alarm',
    title: 'Alarms',
    description: 'Time-based reminders and alarms',
    component: 'AlarmWidget',
    minSize: { w: 6, h: 4 },
    maxSize: { w: 20, h: 28 },
    defaultSize: { w: 12, h: 10 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '⏰'
  },

  // SINGLE ITEM TRACKER Widget
  singleitemtracker: {
    id: 'singleitemtracker',
    apiWidgetType: 'singleitemtracker',
    title: 'Item Tracker',
    description: 'Track single items like weight, water intake, etc.',
    component: 'SingleItemTrackerWidget',
    minSize: { w: 6, h: 4 },
    maxSize: { w: 15, h: 18 },
    defaultSize: { w: 10, h: 12 },
    deletable: true,
    resizable: true,
    category: 'health',
    icon: '📈'
  },

  // WEBSEARCH Widget
  websearch: {
    id: 'websearch',
    apiWidgetType: 'websearch',
    title: 'Web Search',
    description: 'AI-powered web search and summaries',
    component: 'WebSearchWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 11, h: 14 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🔍'
  },

  calendar: {
    id: 'calendar',
    apiWidgetType: 'calendar',
    title: 'Calendar',
    description: 'Calendar widget',
    component: 'CalendarWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 11, h: 14 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '📅'
  },

  // ALL SCHEDULES Widget (UI-only, not in API)
  allSchedules: {
    id: 'allSchedules',
    apiWidgetType: 'allSchedules', // This doesn't exist in API, but we keep it for UI
    title: 'All Schedules',
    description: 'Manage all widget schedules and configurations',
    component: 'AllSchedulesWidget',
    minSize: { w: 12, h: 10 },
    maxSize: { w: 30, h: 36 },
    defaultSize: { w: 12, h: 15 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '⚙️'
  }
};

// Helper functions
export const getWidgetConfig = (widgetId: string): WidgetConfig | undefined => {
  return WIDGET_CONFIGS[widgetId];
};

export const getWidgetsByCategory = (category: WidgetConfig['category']): WidgetConfig[] => {
  return Object.values(WIDGET_CONFIGS).filter(widget => widget.category === category);
};

export const getAllWidgets = (): WidgetConfig[] => {
  return Object.values(WIDGET_CONFIGS);
};

export const getImplementedWidgets = (): WidgetConfig[] => {
  // Currently implemented widgets that match API types
  return [
    WIDGET_CONFIGS['todo-habit'],
    WIDGET_CONFIGS['todo-task'],
    WIDGET_CONFIGS['todo-event'],
    WIDGET_CONFIGS.alarm,
    WIDGET_CONFIGS.singleitemtracker,
    WIDGET_CONFIGS.websearch,
    WIDGET_CONFIGS.allSchedules, // UI-only widget
    WIDGET_CONFIGS.calendar,
  ];
};

export const getPlannedWidgets = (): WidgetConfig[] => {
  // Widgets planned for implementation (excluding implemented ones)
  const implementedIds = getImplementedWidgets().map(w => w.id);
  return Object.values(WIDGET_CONFIGS).filter(widget => !implementedIds.includes(widget.id));
};

export const getMediumSizedWidgets = (): WidgetConfig[] => {
  return Object.values(WIDGET_CONFIGS).filter(widget => 
    widget.defaultSize.w >= 8 && widget.defaultSize.h >= 8
  );
};

export const getSmallSizedWidgets = (): WidgetConfig[] => {
  return Object.values(WIDGET_CONFIGS).filter(widget => 
    widget.defaultSize.w < 8 || widget.defaultSize.h < 8
  );
};

// API Mapping Helper Functions
export const getConfigWidgetIdByApiType = (apiWidgetType: string): string | undefined => {
  const widget = Object.values(WIDGET_CONFIGS).find(w => w.apiWidgetType === apiWidgetType);
  return widget?.id;
};

export const getApiWidgetTypeByConfigId = (configWidgetId: string): string | undefined => {
  return WIDGET_CONFIGS[configWidgetId]?.apiWidgetType;
};

// Type mapping for Dashboard component
export const getApiTypeToConfigMapping = (): Record<string, string> => {
  const mapping: Record<string, string> = {};
  Object.values(WIDGET_CONFIGS).forEach(widget => {
    if (widget.apiWidgetType) {
      mapping[widget.apiWidgetType] = widget.id;
    }
  });
  return mapping;
};

export const getConfigToApiTypeMapping = (): Record<string, string> => {
  const mapping: Record<string, string> = {};
  Object.values(WIDGET_CONFIGS).forEach(widget => {
    if (widget.apiWidgetType) {
      mapping[widget.id] = widget.apiWidgetType;
    }
  });
  return mapping;
};
