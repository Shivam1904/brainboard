import { TodayWidgetsResponse, ScheduledItem } from '../types/dashboard';

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
  const widgets = [];
  let x = 0;
  let y = 0;
  const maxCols = 24;
  const widgetWidth = 10;
  const widgetHeight = 8;

  // Group items by type
  const webSearches = items.filter(item => item.type === 'webSearch');
  const userTasks = items.filter(item => item.type === 'userTask');
  const userHabits = items.filter(item => item.type === 'userHabit');
  const itemTrackers = items.filter(item => item.type === 'itemTracker');
  const otherWidgets = items.filter(item => 
    !['webSearch', 'userTask', 'userHabit', 'itemTracker'].includes(item.type)
  );

  // Create widgets for each webSearch item
  webSearches.forEach((item, index) => {
    const widgetId = `webSearch-${item.id}`;
    widgets.push({
      id: widgetId,
      type: 'webSearch',
      layout: {
        x: x,
        y: y,
        w: widgetWidth,
        h: widgetHeight,
        minW: 8,
        minH: 8,
        maxW: 12,
        maxH: 10
      },
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

    // Move to next position
    x += widgetWidth;
    if (x + widgetWidth > maxCols) {
      x = 0;
      y += widgetHeight;
    }
  });

  // Add other widget types
  if (userTasks.length > 0 || userHabits.length > 0) {
    widgets.push({
      id: 'everydayTaskList-1',
      type: 'everydayTaskList',
      layout: {
        x: x,
        y: y,
        w: widgetWidth,
        h: widgetHeight,
        minW: 8,
        minH: 8,
        maxW: 12,
        maxH: 10
      },
      config: {
        showCompleted: true,
        sortBy: 'priority'
      },
      priority: 1,
      enabled: true,
      scheduledItem: {
        id: 'taskList',
        title: 'Task List',
        type: 'everydayTaskList',
        frequency: 'daily'
      }
    });

    x += widgetWidth;
    if (x + widgetWidth > maxCols) {
      x = 0;
      y += widgetHeight;
    }
  }

  // Add calendar widget
  const calendarItem = otherWidgets.find(item => item.type === 'calendar');
  if (calendarItem) {
    widgets.push({
      id: 'monthlyCalendar-1',
      type: 'monthlyCalendar',
      layout: {
        x: x,
        y: y,
        w: widgetWidth,
        h: widgetHeight,
        minW: 8,
        minH: 8,
        maxW: 12,
        maxH: 10
      },
      config: {
        showMilestones: true,
        highlightToday: true
      },
      priority: 2,
      enabled: true,
      scheduledItem: calendarItem
    });

    x += widgetWidth;
    if (x + widgetWidth > maxCols) {
      x = 0;
      y += widgetHeight;
    }
  }

  // Add item trackers as small widgets
  itemTrackers.forEach((item, index) => {
    const widgetId = `itemTracker-${item.id}`;
    widgets.push({
      id: widgetId,
      type: 'itemTracker',
      layout: {
        x: x,
        y: y,
        w: 6,
        h: 6,
        minW: 6,
        minH: 4,
        maxW: 10,
        maxH: 8
      },
      config: {
        itemName: item.title,
        category: item.category
      },
      priority: 10 + index,
      enabled: true,
      scheduledItem: item
    });

    x += 6;
    if (x + 6 > maxCols) {
      x = 0;
      y += 6;
    }
  });

  return {
    date: new Date().toISOString().split('T')[0],
    widgets,
    layout: {
      gridCols: 24,
      gridRows: Math.max(16, y + widgetHeight)
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