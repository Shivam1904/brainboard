// Dummy Data - API-Compatible
// This dummy data matches the actual API response structures exactly

import {
  TodayWidgetsResponse,
  DailyWidget,
  TodoTodayResponse,
  TodoActivity,
  AlarmDetailsAndActivityResponse,
  AlarmDetails,
  AlarmActivity,
  TrackerDetailsAndActivityResponse,
  TrackerDetails,
  TrackerActivity,
  WebSearchSummaryAndActivityResponse,
  WebSearchDetails,
  WebSearchActivity,
  WebSearchAISummaryResponse
} from '../types';

// ============================================================================
// DASHBOARD DUMMY DATA
// ============================================================================

export const getDummyTodayWidgets = (): TodayWidgetsResponse => {
  return {
    date: new Date().toISOString().split('T')[0],
    widgets: [
      {
        daily_widget_id: "daily-todo-habit-001",
        widget_ids: ["widget-todo-habit-001"],
        widget_type: "todo-habit",
        priority: "HIGH",
        reasoning: "Habit tracker is essential for daily routines",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-todo-task-001",
        widget_ids: ["widget-todo-task-001"],
        widget_type: "todo-task",
        priority: "HIGH",
        reasoning: "Task list is essential for daily productivity",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-todo-event-001",
        widget_ids: ["widget-todo-event-001"],
        widget_type: "todo-event",
        priority: "LOW",
        reasoning: "Event tracker for important appointments",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-alarm-001",
        widget_ids: ["widget-alarm-001"],
        widget_type: "alarm",
        priority: "HIGH",
        reasoning: "Alarm widget for important reminders",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-tracker-001",
        widget_ids: ["widget-tracker-001"],
        widget_type: "singleitemtracker",
        priority: "LOW",
        reasoning: "Tracker widget for health monitoring",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      },
      {
        daily_widget_id: "daily-websearch-001",
        widget_ids: ["widget-websearch-001"],
        widget_type: "websearch",
        priority: "LOW",
        reasoning: "Web search widget for research tasks",
        date: new Date().toISOString().split('T')[0],
        created_at: "2024-01-15T10:00:00Z"
      }
    ],
    total_widgets: 6,
    ai_generated: true,
    last_updated: "2024-01-15T10:00:00Z"
  };
};

// ============================================================================
// TODO WIDGET DUMMY DATA
// ============================================================================

export const getDummyTodoTodayResponse = (todoType: 'habit' | 'task' | 'event'): TodoTodayResponse => {
  if(todoType === 'event') {
    return {
      todo_type: todoType,
      todos: [
        {
          id: "activity-001",
          widget_id: "widget-todo-001",
          daily_widget_id: "daily-todo-001",
          todo_details_id: "todo-details-001",
          title: "Event 1",
          todo_type: todoType,
          description: "Event 1 description",
          due_date: "2024-01-20",
          status: "pending",
          progress: 0,
          created_at: "2024-01-15T10:00:00Z",
          updated_at: "2024-01-15T10:00:00Z"
        }
      ],
      total_todos: 1
    }
  }
  return {
    todo_type: todoType,
    todos: [
      {
        id: "activity-001",
        widget_id: "widget-todo-001",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-001",
        title: todoType === 'task' ? "Complete project documentation" : todoType === 'habit' ? "Morning meditation everyday" : "",
        todo_type: todoType,
        description: todoType === 'task' ? "Finish the project documentation by end of day" : todoType === 'habit' ? "Practice mindfulness for 10 minutes" : "",
        due_date: "2024-01-20",
        status: "pending",
        progress: 0,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z"
      },
      {
        id: "activity-002",
        widget_id: "widget-todo-002",
        daily_widget_id: "daily-todo-001",
        todo_details_id: "todo-details-002",
        title: todoType === 'task' ? "Review code changes" : "Drink 8 glasses of water",
        todo_type: todoType,
        description: todoType === 'task' ? "Review and approve pending code changes" : "Stay hydrated throughout the day",
        due_date: "2024-01-16",
        status: "in progress",
        progress: 50,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z"
      }
    ],
    total_todos: 2
  };
};

// ============================================================================
// ALARM WIDGET DUMMY DATA
// ============================================================================

export const getDummyAlarmDetailsAndActivity = (widgetId: string): AlarmDetailsAndActivityResponse => {
  return {
    alarm_details: {
      id: "alarm-details-001",
      widget_id: widgetId,
      title: "Morning Workout Alarm",
      description: "Alarm for morning workout routine",
      alarm_times: ["06:00", "06:15"],
      target_value: "workout",
      is_snoozable: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "alarm-activity-001",
      started_at: "",
      snoozed_at: "",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    }
  };
};

// ============================================================================
// SINGLE ITEM TRACKER WIDGET DUMMY DATA
// ============================================================================

export const getDummyTrackerDetailsAndActivity = (widgetId: string): TrackerDetailsAndActivityResponse => {
  return {
    tracker_details: {
      id: "tracker-details-001",
      widget_id: widgetId,
      title: "Weight Tracker",
      value_type: "number",
      value_unit: "kg",
      target_value: "70",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "tracker-activity-001",
      value: "72.5",
      time_added: "2024-01-15T08:00:00Z",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    }
  };
};

// ============================================================================
// WEBSEARCH WIDGET DUMMY DATA
// ============================================================================

export const getDummyWebSearchSummaryAndActivity = (widgetId: string): WebSearchSummaryAndActivityResponse => {
  return {
    websearch_details: {
      id: "websearch-details-001",
      widget_id: widgetId,
      title: "AI Research",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    },
    activity: {
      id: "websearch-activity-001",
      status: "completed",
      reaction: "positive",
      summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
      source_json: {
        sources: [
          "https://example.com/ai-news-1",
          "https://example.com/ai-news-2",
          "https://example.com/ai-news-3"
        ]
      },
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z"
    }
  };
};

export const getDummyWebSearchAISummary = (widgetId: string): WebSearchAISummaryResponse => {
  return {
    ai_summary_id: "ai-summary-001",
    widget_id: widgetId,
    query: "AI Research",
    summary: "Recent AI developments show significant progress in large language models, with new breakthroughs in multimodal AI and improved reasoning capabilities. Key areas include GPT-4 advancements, Claude 3 improvements, and emerging open-source alternatives.",
    sources: [
      {
        title: "AI News Article 1",
        url: "https://example.com/ai-news-1"
      },
      {
        title: "AI News Article 2", 
        url: "https://example.com/ai-news-2"
      },
      {
        title: "AI News Article 3",
        url: "https://example.com/ai-news-3"
      }
    ],
    search_successful: true,
    results_count: 3,
    ai_model_used: "gpt-3.5-turbo",
    generation_type: "ai_generated",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z"
  };
};

// ============================================================================
// LEGACY COMPATIBILITY (for existing widget components)
// ============================================================================

// These functions maintain compatibility with existing widget components
// They will be removed once widgets are updated to use API types directly

export const getDummyAlarms = (widgetId: string) => {
  return getDummyAlarmDetailsAndActivity(widgetId);
};

export const getDummyTasks = () => {
  const response = getDummyTodoTodayResponse('task');
  return response.todos;
};

export const getDummyWebSearchResult = (searchQuery: string) => {
  const response = getDummyWebSearchSummaryAndActivity('widget-websearch-001');
  return response.activity;
};

export const getDummyTracker = (widgetId: string) => {
  return getDummyTrackerDetailsAndActivity(widgetId);
};

export const getDummyCalendarData = (year: number, month: number) => {
  // Generate calendar days for the specified month
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday
  
  const days: any[] = [];
  const currentDate = new Date();
  
  // Generate 42 days (6 weeks) to fill the calendar grid
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    const isCurrentMonth = date.getMonth() === month - 1;
    const isToday = date.toDateString() === currentDate.toDateString();
    
    // Generate random events for each day
    const dayEvents = generateDayEvents(date, isCurrentMonth);
    
    days.push({
      date: date.toISOString().split('T')[0],
      day: date.getDate(),
      isCurrentMonth,
      isToday,
      events: dayEvents,
      todosCompleted: Math.floor(Math.random() * 8) + 2, // 2-9 todos
      todosTotal: Math.floor(Math.random() * 5) + 8, // 8-12 total todos
      habitStreak: Math.floor(Math.random() * 15) + 1, // 1-15 day streak
      milestones: Math.floor(Math.random() * 3) // 0-2 milestones
    });
  }

  // Generate events for the month
  const events = generateMonthEvents(year, month);
  
  // Generate milestones for the month
  const milestones = generateMonthMilestones(year, month);

  return {
    year,
    month,
    days,
    events,
    milestones,
    monthlyStats: {
      totalTodosCompleted: days.reduce((sum, day) => sum + day.todosCompleted, 0),
      totalTodos: days.reduce((sum, day) => sum + day.todosTotal, 0),
      averageCompletionRate: Math.round((days.reduce((sum, day) => sum + day.todosCompleted, 0) / days.reduce((sum, day) => sum + day.todosTotal, 0)) * 100),
      longestHabitStreak: Math.max(...days.map(day => day.habitStreak)),
      totalMilestones: days.reduce((sum, day) => sum + day.milestones, 0)
    }
  };
};

// Helper function to generate events for a specific day
const generateDayEvents = (date: Date, isCurrentMonth: boolean) => {
  if (!isCurrentMonth) return [];
  
  const events: any[] = [];
  const dayOfWeek = date.getDay();
  const dayOfMonth = date.getDate();
  
  // Generate different types of events based on the day
  if (dayOfWeek === 1) { // Monday
    events.push({
      id: `event-${date.toISOString().split('T')[0]}-1`,
      title: "Team Meeting",
      date: date.toISOString().split('T')[0],
      time: "09:00",
      location: "Conference Room A",
      type: "event" as const,
      priority: "High" as const,
      description: "Weekly team sync meeting"
    });
  }
  
  if (dayOfMonth === 15) {
    events.push({
      id: `event-${date.toISOString().split('T')[0]}-2`,
      title: "Project Deadline",
      date: date.toISOString().split('T')[0],
      time: "17:00",
      type: "milestone" as const,
      priority: "High" as const,
      description: "Submit final project deliverables"
    });
  }
  
  if (dayOfWeek === 5) { // Friday
    events.push({
      id: `event-${date.toISOString().split('T')[0]}-3`,
      title: "Weekly Review",
      date: date.toISOString().split('T')[0],
      time: "16:00",
      type: "task" as const,
      priority: "Medium" as const,
      description: "Review weekly progress and plan next week"
    });
  }
  
  if (dayOfMonth % 7 === 0) {
    events.push({
      id: `event-${date.toISOString().split('T')[0]}-4`,
      title: "Health Check",
      date: date.toISOString().split('T')[0],
      time: "10:00",
      location: "Gym",
      type: "reminder" as const,
      priority: "Low" as const,
      description: "Weekly health and fitness check-in"
    });
  }
  
  // Add some random events
  if (Math.random() > 0.7) {
    const eventTypes: ('event' | 'milestone' | 'reminder' | 'task')[] = ['event', 'milestone', 'reminder', 'task'];
    const priorities: ('High' | 'Medium' | 'Low')[] = ['High', 'Medium', 'Low'];
    const titles = [
      "Client Call",
      "Code Review",
      "Lunch Meeting",
      "Training Session",
      "Product Demo",
      "Strategy Meeting",
      "Budget Review",
      "Performance Review"
    ];
    
    events.push({
      id: `event-${date.toISOString().split('T')[0]}-${Math.floor(Math.random() * 1000)}`,
      title: titles[Math.floor(Math.random() * titles.length)],
      date: date.toISOString().split('T')[0],
      time: `${Math.floor(Math.random() * 12) + 9}:${Math.random() > 0.5 ? '00' : '30'}`,
      type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      description: "Random event description"
    });
  }
  
  return events;
};

// Helper function to generate events for the entire month
const generateMonthEvents = (year: number, month: number) => {
  const events = [];
  
  // Add some recurring events
  for (let day = 1; day <= 31; day++) {
    const date = new Date(year, month - 1, day);
    if (date.getMonth() === month - 1) { // Ensure it's the correct month
      const dayEvents = generateDayEvents(date, true);
      events.push(...dayEvents);
    }
  }
  
  // Add some special events
  events.push(
    {
      id: "event-monthly-1",
      title: "Monthly Planning Session",
      date: `${year}-${month.toString().padStart(2, '0')}-01`,
      time: "14:00",
      location: "Board Room",
      type: "event" as const,
      priority: "High" as const,
      description: "Monthly strategic planning and goal setting session"
    },
    {
      id: "event-monthly-2",
      title: "Quarterly Review",
      date: `${year}-${month.toString().padStart(2, '0')}-15`,
      time: "10:00",
      location: "Conference Room B",
      type: "milestone" as const,
      priority: "High" as const,
      description: "Quarterly performance review and assessment"
    },
    {
      id: "event-monthly-3",
      title: "Team Building Event",
      date: `${year}-${month.toString().padStart(2, '0')}-20`,
      time: "16:00",
      location: "Office Lounge",
      type: "event" as const,
      priority: "Medium" as const,
      description: "Monthly team building and social event"
    }
  );
  
  return events;
};

// Helper function to generate milestones for the month
const generateMonthMilestones = (year: number, month: number) => {
  return [
    {
      id: "milestone-1",
      title: "Project Alpha Completed",
      date: `${year}-${month.toString().padStart(2, '0')}-10`,
      time: "17:30",
      type: "milestone" as const,
      priority: "High" as const,
      description: "Successfully completed major project milestone",
      category: "work"
    },
    {
      id: "milestone-2",
      title: "30-Day Fitness Streak",
      date: `${year}-${month.toString().padStart(2, '0')}-25`,
      time: "18:00",
      type: "milestone" as const,
      priority: "Medium" as const,
      description: "Achieved 30 consecutive days of exercise",
      category: "health"
    },
    {
      id: "milestone-3",
      title: "Learning Certification",
      date: `${year}-${month.toString().padStart(2, '0')}-28`,
      time: "15:00",
      type: "milestone" as const,
      priority: "Medium" as const,
      description: "Completed advanced certification course",
      category: "learning"
    }
  ];
};

export const getDummyAllSchedulesWidgets = () => {
  // AllSchedules widget is UI-only, so we return empty data
  return [];
};

export const getDummyWebSummary = (query: string) => {
  return getDummyWebSearchAISummary('widget-websearch-001');
};

export const getDummyReminders = () => {
  // Reminders are handled by alarm widget in the API
  return [];
}; 