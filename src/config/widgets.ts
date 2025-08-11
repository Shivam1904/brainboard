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

// TODO: Add all widgets here
export const WIDGET_CONFIGS: Record<string, WidgetConfig> = {
  // HABIT TRACKER Widget
  habitTracker: {
    id: 'habitTracker',
    apiWidgetType: 'habitTracker',
    title: 'Habit Tracker',
    description: 'Track daily habits and routines with circular grid layout',
    component: 'HabitTrackerWidget',
    minSize: { w: 12, h: 12 },
    maxSize: { w: 30, h: 30 },
    defaultSize: { w: 11, h: 10 },
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



  // ADVANCED SINGLE TASK Widget
  advancedsingletask: {
    id: 'advancedsingletask',
    apiWidgetType: 'advancedsingletask', // Uses the same API type as singleitemtracker
    title: 'Advanced Single Task',
    description: 'Advanced single task with tracker, alarm, and progress details',
    component: 'SingleTaskWidget',
    minSize: { w: 8, h: 6 },
    maxSize: { w: 18, h: 20 },
    defaultSize: { w: 12, h: 6 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '🎯'
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
    defaultSize: { w: 11, h: 11 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🔍'
  },

  // YEAR CALENDAR Widget
  yearCalendar: {
    id: 'yearCalendar',
    apiWidgetType: 'yearCalendar',
    title: 'Year Calendar',
    description: 'Year calendar widget',
    component: 'YearCalendarWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 11, h: 6 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '📅'
  },
  calendar: {
    id: 'calendar',
    apiWidgetType: 'calendar',
    title: 'Calendar',
    description: 'Calendar widget',
    component: 'CalendarWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 12, h: 12 },
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
    defaultSize: { w: 12, h: 5 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '⚙️'
  },

  aiChat: { 
    id: 'aiChat',
    apiWidgetType: 'aiChat',
    title: 'Brainy AI',
    description: 'AI-powered chat widget',
    component: 'AIChatWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 14, h: 14 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🤖'
  },

  // MOOD TRACKER (View-type, UI-managed visibility)
  moodTracker: {
    id: 'moodTracker',
    apiWidgetType: 'moodTracker',
    title: 'Mood Tracker',
    description: 'Track and reflect on your mood',
    component: 'MoodTrackerWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 8, h: 6 },
    deletable: true,
    resizable: true,
    category: 'health',
    icon: '😊'
  },

  // WEATHER (View-type, UI-managed visibility)
  weatherWidget: {
    id: 'weatherWidget',
    apiWidgetType: 'weatherWidget',
    title: 'Weather',
    description: 'Current weather and forecast',
    component: 'WeatherWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 20, h: 24 },
    defaultSize: { w: 8, h: 8 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '⛅️'
  },

  // SIMPLE CLOCK (View-type, UI-managed visibility)
  simpleClock: {
    id: 'simpleClock',
    apiWidgetType: 'simpleClock',
    title: 'Simple Clock',
    description: 'Current time at a glance',
    component: 'SimpleClockWidget',
    minSize: { w: 6, h: 6 },
    maxSize: { w: 20, h: 20 },
    defaultSize: { w: 8, h: 8 },
    deletable: true,
    resizable: true,
    category: 'utilities',
    icon: '🕒'
  },

  // ALARM Widget
  alarm: {
    id: 'alarm',
    apiWidgetType: 'alarm',
    title: 'Alarm',
    description: 'Set and manage alarms',
    component: 'AlarmWidget',
    minSize: { w: 6, h: 6 },
    maxSize: { w: 16, h: 20 },
    defaultSize: { w: 10, h: 12 },
    deletable: true,
    resizable: true,
    category: 'utilities',
    icon: '⏰'
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
    WIDGET_CONFIGS['todo-task'],
    WIDGET_CONFIGS.advancedsingletask,
    WIDGET_CONFIGS.websearch,
    WIDGET_CONFIGS.allSchedules, // UI-only widget
    WIDGET_CONFIGS.calendar,
    WIDGET_CONFIGS.aiChat,
    WIDGET_CONFIGS.moodTracker,
    WIDGET_CONFIGS.weatherWidget,
    WIDGET_CONFIGS.simpleClock,
    WIDGET_CONFIGS.alarm,
    WIDGET_CONFIGS.yearCalendar,
    WIDGET_CONFIGS.habitTracker,
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
