import { 
  AlarmWidgetDataResponse, 
  SingleItemTrackerWidgetDataResponse,
  TodayWidgetsResponse
} from '../types';

// Local interface definitions that match what the widgets actually use
interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  category?: string;
  dueDate?: string;
  createdAt: string;
}

interface Summary {
  id: string;
  query: string;
  summary: string;
  sources: string[];
  createdAt: string;
}

interface WebSearchResult {
  id: string;
  searchTerm: string;
  heading: string;
  subheading: string;
  text: string;
  images?: string[];
  chartData?: any;
  scheduleDate: string;
}

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  location?: string;
  type: 'event' | 'milestone' | 'reminder' | 'task';
  priority: 'High' | 'Medium' | 'Low';
  description?: string;
}

interface CalendarDay {
  date: string;
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
}

interface CalendarData {
  year: number;
  month: number;
  days: CalendarDay[];
  events: CalendarEvent[];
  milestones: CalendarEvent[];
}

interface Reminder {
  id: string;
  text: string;
  completed: boolean;
  dueDate?: string;
  createdAt: string;
}

interface WidgetData {
  id: string;
  title: string;
  type: string;
  frequency: string;
  category: string;
  importance: number;
  size: string;
  settings: any;
  data: any;
}

type WidgetType = 'todo' | 'habittracker' | 'websearch' | 'websummary' | 'calendar' | 'alarm' | 'allSchedules' | 'singleitemtracker' | 'thisHour' | 'reminder';

// ============================================================================
// ALARM WIDGET DUMMY DATA
// ============================================================================

export const getDummyAlarms = (widgetId: string): AlarmWidgetDataResponse => ({
  widget_id: widgetId,
  alarms: [
    {
      id: '1',
      dashboard_widget_id: widgetId,
      title: 'Morning Standup',
      alarm_type: 'daily',
      alarm_times: ['09:00'],
      is_active: true,
      is_snoozed: false,
      next_trigger_time: new Date().toISOString(),
      created_at: '2024-01-10T09:00:00Z',
      updated_at: '2024-01-15T14:30:00Z'
    },
    {
      id: '2',
      dashboard_widget_id: widgetId,
      title: 'Lunch Break',
      alarm_type: 'daily',
      alarm_times: ['12:30'],
      is_active: true,
      is_snoozed: false,
      next_trigger_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
      created_at: '2024-01-10T10:00:00Z',
      updated_at: '2024-01-15T14:30:00Z'
    },
    {
      id: '3',
      dashboard_widget_id: widgetId,
      title: 'Evening Exercise',
      alarm_type: 'daily',
      alarm_times: ['18:00'],
      is_active: true,
      is_snoozed: false,
      next_trigger_time: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4 hours from now
      created_at: '2024-01-10T11:00:00Z',
      updated_at: '2024-01-15T14:30:00Z'
    }
  ],
  stats: {
    total_alarms: 3,
    active_alarms: 3,
    next_alarm_time: new Date().toISOString(),
    next_alarm_title: 'Morning Standup'
  }
});

// ============================================================================
// TASK LIST WIDGET DUMMY DATA
// ============================================================================

export const getDummyTasks = (): Task[] => [
  {
    id: '1',
    title: 'Complete project documentation',
    description: 'Finish the API documentation for the new features',
    completed: false,
    priority: 'High',
    category: 'work',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T09:00:00Z'
  },
  {
    id: '2',
    title: 'Review code changes',
    description: 'Go through the pull requests and provide feedback',
    completed: true,
    priority: 'Medium',
    category: 'work',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T10:00:00Z'
  },
  {
    id: '3',
    title: 'Exercise routine',
    description: 'Complete 30 minutes of cardio and strength training',
    completed: false,
    priority: 'High',
    category: 'health',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T07:00:00Z'
  },
  {
    id: '4',
    title: 'Read technical articles',
    description: 'Read 2-3 articles about React performance optimization',
    completed: false,
    priority: 'Low',
    category: 'learning',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T14:00:00Z'
  },
  {
    id: '5',
    title: 'Plan weekend activities',
    description: 'Organize activities for the upcoming weekend',
    completed: false,
    priority: 'Medium',
    category: 'personal',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T16:00:00Z'
  }
];

// ============================================================================
// WEB SEARCH WIDGET DUMMY DATA
// ============================================================================

export const getDummyWebSearchResult = (searchQuery: string): WebSearchResult => {
  switch (searchQuery.toLowerCase()) {
    case 'latest football news and scores':
      return {
        id: 'football',
        searchTerm: searchQuery,
        heading: 'Football: Champions League Highlights',
        subheading: 'All the latest scores and news from Europe',
        text: 'Manchester United secured a dramatic win in the final minutes. Real Madrid and Barcelona both advanced to the next round. Stay tuned for more updates and analysis.',
        images: ['https://via.placeholder.com/300x200/2563EB/FFFFFF?text=Football'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    case 'artificial intelligence developments today':
      return {
        id: 'ai',
        searchTerm: searchQuery,
        heading: 'AI: New Breakthroughs in 2024',
        subheading: 'GPT-5 and robotics lead the way',
        text: 'Researchers have announced major advances in natural language processing and robotics. AI is now being used in healthcare, finance, and creative industries at an unprecedented scale.',
        images: ['https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=AI+News'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    case 'stock market trends and analysis':
      return {
        id: 'stocks',
        searchTerm: searchQuery,
        heading: 'Stocks: Market Trends & Analysis',
        subheading: 'Tech stocks rally, S&P 500 hits new high',
        text: 'The stock market saw a significant rally today, led by gains in the technology sector. Analysts predict continued growth as earnings season approaches.',
        images: ['https://via.placeholder.com/300x200/10B981/FFFFFF?text=Stocks'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    default:
      return {
        id: 'default',
        searchTerm: searchQuery,
        heading: `Search Results for: ${searchQuery}`,
        subheading: `Latest information about ${searchQuery}`,
        text: `This is a sample result for the search query: "${searchQuery}". In a real implementation, this would contain actual search results from the web.`,
        images: ['https://via.placeholder.com/300x200/64748B/FFFFFF?text=Web+Search'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
  }
};

// ============================================================================
// SINGLE ITEM TRACKER WIDGET DUMMY DATA
// ============================================================================

export const getDummyTracker = (widgetId: string): SingleItemTrackerWidgetDataResponse => ({
  widget_id: widgetId,
  tracker: {
    id: 'dummy-tracker-id',
    dashboard_widget_id: widgetId,
    item_name: 'Weight',
    item_unit: 'kg',
    current_value: '75.5',
    target_value: '70.0',
    value_type: 'decimal',
    created_at: '2024-01-10T09:00:00Z',
    updated_at: '2024-01-15T14:30:00Z',
    recent_logs: []
  },
  stats: {
    total_entries: 3,
    current_value: '75.5',
    target_value: '70.0',
    progress_percentage: 107.9,
    last_updated: '2024-01-15',
    streak_days: 3
  },
  recent_logs: [
    {
      id: '1',
      value: '75.5',
      date: '2024-01-15',
      notes: 'Morning weigh-in',
      created_at: '2024-01-15T08:00:00Z'
    },
    {
      id: '2',
      value: '75.8',
      date: '2024-01-14',
      notes: 'After workout',
      created_at: '2024-01-14T19:00:00Z'
    },
    {
      id: '3',
      value: '76.0',
      date: '2024-01-13',
      notes: 'Evening check',
      created_at: '2024-01-13T20:00:00Z'
    }
  ]
});

// ============================================================================
// CALENDAR WIDGET DUMMY DATA
// ============================================================================

export const getDummyCalendarData = (year: number, month: number): CalendarData => {
  const events: CalendarEvent[] = [
    {
      id: '1',
      title: 'Team Meeting',
      date: '2025-07-15',
      time: '10:00 AM',
      location: 'Conference Room A',
      type: 'event',
      priority: 'High',
      description: 'Weekly team sync meeting'
    },
    {
      id: '2',
      title: 'Project Deadline',
      date: '2025-07-20',
      type: 'milestone',
      priority: 'High',
      description: 'Phase 1 completion deadline'
    },
    {
      id: '3',
      title: 'Doctor Appointment',
      date: '2025-07-18',
      time: '2:30 PM',
      location: 'Medical Center',
      type: 'reminder',
      priority: 'Medium',
      description: 'Annual checkup'
    },
    {
      id: '4',
      title: 'Gym Session',
      date: '2025-07-16',
      time: '6:00 PM',
      location: 'Fitness Center',
      type: 'task',
      priority: 'Low',
      description: 'Cardio and strength training'
    },
    {
      id: '5',
      title: 'Client Presentation',
      date: '2025-07-22',
      time: '11:00 AM',
      location: 'Virtual Meeting',
      type: 'event',
      priority: 'High',
      description: 'Present quarterly results to client'
    },
    {
      id: '6',
      title: 'Birthday Party',
      date: '2025-07-25',
      time: '7:00 PM',
      location: 'Home',
      type: 'event',
      priority: 'Medium',
      description: 'Friend\'s birthday celebration'
    }
  ];

  // Generate calendar days
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay());

  const days: CalendarDay[] = [];
  const today = new Date();

  for (let i = 0; i < 42; i++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(startDate.getDate() + i);
    
    const dateString = currentDate.toISOString().split('T')[0];
    const dayEvents = events.filter(event => event.date === dateString);
    
    days.push({
      date: dateString,
      day: currentDate.getDate(),
      isCurrentMonth: currentDate.getMonth() === month - 1,
      isToday: currentDate.toDateString() === today.toDateString(),
      events: dayEvents
    });
  }

  return {
    year,
    month,
    days,
    events,
    milestones: events.filter(event => event.type === 'milestone')
  };
};

// ============================================================================
// ALL SCHEDULES WIDGET DUMMY DATA
// ============================================================================

export const getDummyAllSchedulesWidgets = (): WidgetData[] => [
  {
    id: '1',
    title: 'Daily Task List',
    type: 'todo' as WidgetType,
    frequency: 'daily',
    category: 'productivity',
    importance: 4,
    size: 'medium',
    settings: { showCompleted: true, maxTasks: 10 },
    data: { tasks: [], stats: { total_tasks: 0, completed_tasks: 0, pending_tasks: 0, completion_rate: 0 } }
  },
  {
    id: '2',
    title: 'Morning Exercise Habit',
    type: 'habittracker' as WidgetType,
    frequency: 'daily',
    category: 'health',
    importance: 5,
    size: 'small',
    settings: { targetDays: 7, currentStreak: 3 },
    data: { habits: [], stats: { total_habits: 0, completed_habits: 0, current_streak: 3 } }
  },
  {
    id: '3',
    title: 'Tech News Search',
    type: 'websearch' as WidgetType,
    frequency: 'daily',
    category: 'awareness',
    importance: 3,
    size: 'large',
    settings: { searchQuery: 'latest tech news', maxResults: 5 },
    data: { search_results: [], query: 'latest tech news' }
  },
  {
    id: '4',
    title: 'Weekly Finance Summary',
    type: 'websummary' as WidgetType,
    frequency: 'weekly',
    category: 'finance',
    importance: 4,
    size: 'medium',
    settings: { summaryLength: 'medium', includeCharts: true },
    data: { summary: '', url: 'https://finance.example.com' }
  },
  {
    id: '5',
    title: 'Calendar Overview',
    type: 'calendar' as WidgetType,
    frequency: 'daily',
    category: 'productivity',
    importance: 3,
    size: 'large',
    settings: { showWeekView: true, includeReminders: true },
    data: { events: [], reminders: [] }
  },
  {
    id: '6',
    title: 'Meditation Reminder',
    type: 'reminder' as WidgetType,
    frequency: 'daily',
    category: 'health',
    importance: 4,
    size: 'small',
    settings: { reminderTime: '18:00', repeatDaily: true },
    data: { total_reminders: 1, overdue_count: 0, severity: 'medium' }
  }
];

// ============================================================================
// WEB SUMMARY WIDGET DUMMY DATA
// ============================================================================

export const getDummyWebSummary = (query: string): Summary => ({
  id: Date.now().toString(),
  query,
  summary: `Here's a comprehensive summary about "${query}": This topic involves multiple aspects and considerations. Based on recent research and available information, the key findings suggest that this is an evolving area with significant implications for various stakeholders.`,
  sources: [
    'https://example.com/source1',
    'https://example.com/source2',
    'https://example.com/source3'
  ],
  createdAt: new Date().toISOString()
});

// ============================================================================
// REMINDER WIDGET DUMMY DATA
// ============================================================================

export const getDummyReminders = (): Reminder[] => [
  {
    id: '1',
    text: 'Review project proposal',
    completed: false,
    dueDate: '2025-07-27',
    createdAt: '2025-07-26'
  },
  {
    id: '2',
    text: 'Call dentist for appointment',
    completed: true,
    createdAt: '2025-07-26'
  },
  {
    id: '3',
    text: 'Buy groceries for the week',
    completed: false,
    dueDate: '2025-07-28',
    createdAt: '2025-07-26'
  },
  {
    id: '4',
    text: 'Schedule team meeting',
    completed: false,
    createdAt: '2025-07-26'
  }
];

// ============================================================================
// TODAY WIDGETS DUMMY DATA (from dashboardDummyData.ts)
// ============================================================================

export const getDummyTodayWidgets = (): TodayWidgetsResponse => {
  return {
    date: new Date().toISOString().split('T')[0],
    widgets: [
      {
        id: "18f2f446-6cb1-465c-b92c-52b3e758c3bf",
        daily_widget_id: "daily-todo-001",
        title: "Daily Task Manager",
        widget_type: "todo",
        category: "productivity",
        importance: 5,
        frequency: "daily",
        position: 0,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Todo widget is essential for daily productivity",
        settings: null,
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "68c2ab14-23e0-41f9-8d98-50b04d01961d",
        daily_widget_id: "daily-habit-001",
        title: "Daily Habits",
        widget_type: "habittracker",
        category: "health",
        importance: 5,
        frequency: "daily",
        position: 1,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Habit tracking is important for health goals",
        settings: {
          streak_goal: 30,
          reminder_time: "09:00"
        },
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "08db6466-e5a4-4c6c-9341-0cd2366360a4",
        daily_widget_id: "daily-websearch-001",
        title: "FastAPI Research Widget",
        widget_type: "websearch",
        category: "research",
        importance: 3,
        frequency: "daily",
        position: 2,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Web search widget for research tasks",
        settings: null,
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      },
      {
        id: "b2df57d5-d5a5-4eb0-8c27-fe5edc67dcde",
        daily_widget_id: "daily-schedules-001",
        title: "All Schedules",
        widget_type: "allSchedules",
        category: "productivity",
        importance: 4,
        frequency: "daily",
        position: 3,
        grid_position: null,
        is_pinned: false,
        ai_reasoning: "Schedule overview is important for productivity",
        settings: {
          max_tasks: 10,
          show_completed: true
        },
        created_at: "2025-07-29T01:38:26.710661",
        updated_at: "2025-07-29T01:38:26.710661"
      }
    ],
    total_widgets: 4,
    ai_generated: true,
    last_updated: "2025-07-29T02:36:55.560747"
  };
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export const getEnabledWidgets = (widgets: TodayWidgetsResponse): TodayWidgetsResponse => {
  return widgets; // All widgets are enabled by default in new structure
}; 