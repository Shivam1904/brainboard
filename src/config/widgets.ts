export interface WidgetConfig {
  id: string;
  title: string;
  description: string;
  component: string;
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
  category: 'productivity' | 'information' | 'entertainment' | 'utilities';
  icon?: string;
}

export const WIDGET_CONFIGS: Record<string, WidgetConfig> = {
  // Medium sized widgets (10x8 or 8x10)
  webSearch: {
    id: 'webSearch',
    title: 'Web Search',
    description: 'Daily web search functionality',
    component: 'WebSearchWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🔍'
  },

  everydayTaskList: {
    id: 'everydayTaskList',
    title: 'Every Day Task List',
    description: 'Daily task management and tracking',
    component: 'EverydayTaskListWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📋'
  },

  monthlyCalendar: {
    id: 'monthlyCalendar',
    title: 'Monthly Calendar',
    description: 'Monthly calendar view and planning',
    component: 'MonthlyCalendarWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📅'
  },

  habitListTracker: {
    id: 'habitListTracker',
    title: 'Habit List Tracker',
    description: 'Track and monitor daily habits',
    component: 'HabitListTrackerWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '✅'
  },

  notes: {
    id: 'notes',
    title: 'Notes',
    description: 'Quick notes and idea capture',
    component: 'NotesWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📝'
  },

  aiTaskHistory: {
    id: 'aiTaskHistory',
    title: 'AI Task History',
    description: 'AI-powered task history and insights',
    component: 'AiTaskHistoryWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '🤖'
  },

  webSearchChart: {
    id: 'webSearchChart',
    title: 'Web Search Chart',
    description: 'Visualize web search patterns and trends',
    component: 'WebSearchChartWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '📊'
  },

  notifications: {
    id: 'notifications',
    title: 'Notifications',
    description: 'Centralized notification center',
    component: 'NotificationsWidget',
    minSize: { w: 8, h: 8 },
    maxSize: { w: 12, h: 10 },
    defaultSize: { w: 10, h: 8 },
    deletable: true,
    resizable: true,
    category: 'utilities',
    icon: '🔔'
  },

  // Small sized widgets (8x6)
  reminders: {
    id: 'reminders',
    title: 'Reminders',
    description: 'Quick reminder management',
    component: 'RemindersWidget',
    minSize: { w: 6, h: 4 },
    maxSize: { w: 10, h: 8 },
    defaultSize: { w: 8, h: 6 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '⏰'
  },

  singleItemTracker: {
    id: 'singleItemTracker',
    title: 'Single Item Tracker',
    description: 'Track single items like smoke/gym/weight',
    component: 'SingleItemTrackerWidget',
    minSize: { w: 6, h: 4 },
    maxSize: { w: 10, h: 8 },
    defaultSize: { w: 8, h: 6 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📈'
  },

  thisHour: {
    id: 'thisHour',
    title: 'This Hour',
    description: 'Hourly task and time tracking',
    component: 'ThisHourWidget',
    minSize: { w: 6, h: 4 },
    maxSize: { w: 10, h: 8 },
    defaultSize: { w: 8, h: 6 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '⏱️'
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
  // Currently implemented widgets
  return [
    WIDGET_CONFIGS.webSearch,
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
