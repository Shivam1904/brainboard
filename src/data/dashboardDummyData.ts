import { TodayWidgetsResponse, ScheduledItem, DashboardWidgetConfig } from '../types/dashboard';
import { findEmptyPosition, GRID_CONFIG } from '../config/grid';
import { getWidgetConfig } from '../config/widgets';

// Dummy scheduled items data (what the API would return)
export const DUMMY_SCHEDULED_ITEMS: ScheduledItem[] = [
  {
    id: '1',
    title: 'India Shopping',
    type: 'userTask',
    frequency: 'daily',
    category: 'health',
    importance: 'High'
  },
  {
    id: '2',
    title: 'FootballQuery',
    type: 'webSearch',
    frequency: 'daily',
    category: 'self-imp',
    searchQuery: 'latest football news and scores'
  },
  {
    id: '3',
    title: 'MySearchQuery',
    type: 'webSearch',
    frequency: 'daily',
    category: 'self-imp',
    searchQuery: 'artificial intelligence developments today'
  },
  {
    id: '4',
    title: 'StockQuery',
    type: 'webSearch',
    frequency: 'daily',
    category: 'self-imp',
    searchQuery: 'stock market trends and analysis'
  },
  {
    id: '5',
    title: 'Stock Chart',
    type: 'aiWebChart',
    frequency: 'alternate',
    category: 'finance'
  },
  {
    id: '6',
    title: 'Weather',
    type: 'weatherWig',
    frequency: 'daily',
    category: 'awareness'
  },
  {
    id: '7',
    title: 'Calendar',
    type: 'calendar',
    frequency: 'daily'
  },
  {
    id: '8',
    title: 'Gym',
    type: 'userHabit',
    frequency: 'weekly-2',
    category: 'health',
    importance: 'Low',
    alarm: '[7am]'
  },
  {
    id: '9',
    title: 'Smoking',
    type: 'itemTracker',
    frequency: 'daily',
    category: 'health'
  },
  {
    id: '10',
    title: 'Weight',
    type: 'itemTracker',
    frequency: 'onGym',
    category: 'health'
  },
  {
    id: '11',
    title: 'Yogi Bday',
    type: 'alarm',
    frequency: 'Jun 20',
    alarm: '[9am]'
  },
  {
    id: '12',
    title: 'Sit Straight',
    type: 'alarm',
    frequency: 'daily-5',
    alarm: '[list of times]'
  },
  {
    id: '13',
    title: 'Hourly Stats',
    type: 'statsWidget',
    frequency: 'hourly',
    category: 'awareness'
  },
  {
    id: '14',
    title: 'How was AI Helpful',
    type: 'statsWidget',
    frequency: 'daily',
    category: 'awareness'
  },
  {
    id: '15',
    title: 'News',
    type: 'newsWidget',
    frequency: 'daily'
  },
  {
    id: '16',
    title: 'Drink Water',
    type: 'userHabit',
    frequency: 'daily-8',
    category: 'health',
    importance: 'High',
    alarm: '[every 2 hr]'
  }
];

// Helper function to convert scheduled items to widget configurations
export const convertScheduledItemsToWidgets = (items: ScheduledItem[]): TodayWidgetsResponse => {
  const widgets: DashboardWidgetConfig[] = [];

  // Group items by type
  const webSearches = items.filter(item => item.type === 'webSearch');
  const userTasks = items.filter(item => item.type === 'userTask');
  const userHabits = items.filter(item => item.type === 'userHabit');
  const itemTrackers = items.filter(item => item.type === 'itemTracker');
  const otherWidgets = items.filter(item => 
    !['webSearch', 'userTask', 'userHabit', 'itemTracker'].includes(item.type)
  );

  // Helper to add a widget using the shared findEmptyPosition
  function addWidgetWithAutoPosition(
    widgetType: string,
    widgetConfig: Omit<DashboardWidgetConfig, 'layout'> & { layout?: Partial<DashboardWidgetConfig['layout']> }
  ) {
    const position = findEmptyPosition({
      widgetId: widgetType,
      widgets,
      getWidgetConfig,
      gridCols: GRID_CONFIG.cols.lg, // match previous maxCols
      maxRows: 100,
    });
    if (!position) return; // skip if no space
    
    // Get layout details from widget config
    const config = getWidgetConfig(widgetType);
    if (!config) return; // skip if config not found
    
    widgets.push({
      ...widgetConfig,
      layout: {
        x: position.x,
        y: position.y,
        w: config.defaultSize.w,
        h: config.defaultSize.h,
        minW: config.minSize.w,
        minH: config.minSize.h,
        maxW: config.maxSize.w,
        maxH: config.maxSize.h,
        ...widgetConfig.layout, // allow override of specific layout properties if needed
      },
    });
  }

  // Create widgets for each webSearch item
  webSearches.forEach((item, index) => {
    const widgetId = `webSearch-${item.id}`;
    addWidgetWithAutoPosition('webSearch', {
      id: widgetId,
      type: 'webSearch',
      config: {
        searchQuery: item.searchQuery,
        title: item.title,
        maxResults: 5,
        showImages: true
      },
      priority: 3 + index,
      enabled: true,
      scheduledItem: item
    });
  });

  // Add Task List widget (always show for demo)
  addWidgetWithAutoPosition('everydayTaskList', {
    id: 'everydayTaskList-1',
    type: 'everydayTaskList',
    config: { showCompleted: true, sortBy: 'priority' },
    priority: 1,
    enabled: true,
    scheduledItem: { id: 'everydayTaskList', title: 'Every Day Task List', type: 'everydayTaskList', frequency: 'daily' }
  });

  // Add calendar widget
  const calendarItem = otherWidgets.find(item => item.type === 'calendar');
  if (calendarItem) {
    addWidgetWithAutoPosition('calendar', {
      id: 'monthlyCalendar-1',
      type: 'calendar',
      config: {
        showMilestones: true,
        highlightToday: true
      },
      priority: 2,
      enabled: true,
      scheduledItem: calendarItem
    });
  }


  // Add All Schedules widget
  addWidgetWithAutoPosition('allSchedules', {
    id: 'allSchedules-1',
    type: 'allSchedules',
    config: {
      showCompleted: false
    },
    priority: 1,
    enabled: true
  });

  // Add item trackers as small widgets
  itemTrackers.forEach((item, index) => {
    const widgetId = `itemTracker-${item.id}`;
    addWidgetWithAutoPosition('singleItemTracker', {
      id: widgetId,
      type: 'singleItemTracker',
      config: {
        title: item.title,
        category: item.category
      },
      priority: 4 + index,
      enabled: true,
      scheduledItem: item
    });
  });

  // Calculate gridRows for layout
  let maxY = 0;
  let maxH = 0;
  widgets.forEach(w => {
    if (w.layout.y + w.layout.h > maxY + maxH) {
      maxY = w.layout.y;
      maxH = w.layout.h;
    }
  });

  return {
    date: new Date().toISOString().split('T')[0],
    widgets,
    layout: {
      gridCols: GRID_CONFIG.cols.lg,
      gridRows: Math.max(16, maxY + maxH)
    }
  };
};

// Dummy data for today's dashboard widget configuration
export const DUMMY_TODAY_WIDGETS: TodayWidgetsResponse = convertScheduledItemsToWidgets(DUMMY_SCHEDULED_ITEMS);

// Helper function to get dummy data with a specific date
export const getDummyTodayWidgets = (date?: string): TodayWidgetsResponse => {
  return {
    ...DUMMY_TODAY_WIDGETS,
    date: date || new Date().toISOString().split('T')[0]
  };
};

// Helper function to filter enabled widgets
export const getEnabledWidgets = (widgets: TodayWidgetsResponse): TodayWidgetsResponse => {
  return {
    ...widgets,
    widgets: widgets.widgets.filter(widget => widget.enabled !== false)
  };
}; 