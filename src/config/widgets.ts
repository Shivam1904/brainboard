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
  reminder: {
    id: 'reminder',
    title: 'Reminders',
    description: 'Manage your tasks and to-do items',
    component: 'ReminderWidget',
    minSize: { w: 2, h: 3 },
    maxSize: { w: 6, h: 8 },
    defaultSize: { w: 3, h: 4 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📝'
  },
  
  webSummary: {
    id: 'webSummary',
    title: 'Web Summary',
    description: 'AI-powered web page summarization',
    component: 'WebSummaryWidget',
    minSize: { w: 3, h: 3 },
    maxSize: { w: 8, h: 6 },
    defaultSize: { w: 4, h: 4 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🌐'
  },

  // Future widgets (not yet implemented)
  calendar: {
    id: 'calendar',
    title: 'Calendar',
    description: 'View and manage your schedule',
    component: 'CalendarWidget',
    minSize: { w: 3, h: 3 },
    maxSize: { w: 6, h: 6 },
    defaultSize: { w: 4, h: 4 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📅'
  },

  notes: {
    id: 'notes',
    title: 'Quick Notes',
    description: 'Jot down quick notes and ideas',
    component: 'NotesWidget',
    minSize: { w: 2, h: 2 },
    maxSize: { w: 6, h: 8 },
    defaultSize: { w: 3, h: 3 },
    deletable: true,
    resizable: true,
    category: 'productivity',
    icon: '📄'
  },

  weather: {
    id: 'weather',
    title: 'Weather',
    description: 'Current weather and forecast',
    component: 'WeatherWidget',
    minSize: { w: 2, h: 2 },
    maxSize: { w: 4, h: 4 },
    defaultSize: { w: 2, h: 3 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '🌤️'
  },

  clock: {
    id: 'clock',
    title: 'World Clock',
    description: 'Display time in different time zones',
    component: 'ClockWidget',
    minSize: { w: 2, h: 1 },
    maxSize: { w: 4, h: 2 },
    defaultSize: { w: 2, h: 1 },
    deletable: true,
    resizable: true,
    category: 'utilities',
    icon: '🕐'
  },

  calculator: {
    id: 'calculator',
    title: 'Calculator',
    description: 'Simple calculator for quick calculations',
    component: 'CalculatorWidget',
    minSize: { w: 2, h: 3 },
    maxSize: { w: 3, h: 4 },
    defaultSize: { w: 2, h: 3 },
    deletable: true,
    resizable: false, // Fixed size for calculator
    category: 'utilities',
    icon: '🧮'
  },

  rssReader: {
    id: 'rssReader',
    title: 'RSS Reader',
    description: 'Read RSS feeds and news',
    component: 'RssReaderWidget',
    minSize: { w: 3, h: 4 },
    maxSize: { w: 8, h: 8 },
    defaultSize: { w: 4, h: 5 },
    deletable: true,
    resizable: true,
    category: 'information',
    icon: '📰'
  },

  spotify: {
    id: 'spotify',
    title: 'Music Player',
    description: 'Control Spotify playback',
    component: 'SpotifyWidget',
    minSize: { w: 3, h: 2 },
    maxSize: { w: 6, h: 3 },
    defaultSize: { w: 4, h: 2 },
    deletable: true,
    resizable: true,
    category: 'entertainment',
    icon: '🎵'
  },

  systemMonitor: {
    id: 'systemMonitor',
    title: 'System Monitor',
    description: 'Monitor CPU, memory, and system stats',
    component: 'SystemMonitorWidget',
    minSize: { w: 2, h: 2 },
    maxSize: { w: 4, h: 4 },
    defaultSize: { w: 3, h: 3 },
    deletable: true,
    resizable: true,
    category: 'utilities',
    icon: '💻'
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
  // Currently only reminder and webSummary are implemented
  return Object.values(WIDGET_CONFIGS).filter(widget => 
    ['reminder', 'webSummary'].includes(widget.id)
  );
};

export const getPlannedWidgets = (): WidgetConfig[] => {
  // All widgets except the implemented ones
  return Object.values(WIDGET_CONFIGS).filter(widget => 
    !['reminder', 'webSummary'].includes(widget.id)
  );
};
