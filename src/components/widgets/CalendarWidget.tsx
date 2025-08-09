import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight, Calendar, Clock, MapPin, Circle, CheckCircle, Trophy, ThumbsUp, Flame } from 'lucide-react';
import { getDummyCalendarData } from '../../data/widgetDummyData';
import { DailyWidget, apiService } from '../../services/api';


export const categoryColors = {
  productivity: { value: 'productivity', label: 'Productivity', color: 'blue' },
  health: { value: 'health', label: 'Health', color: 'red' },
  job: { value: 'job', label: 'Job', color: 'purple' },
  information: { value: 'information', label: 'Information', color: 'yellow' },
  entertainment: { value: 'entertainment', label: 'Entertainment', color: 'pink' },
  utilities: { value: 'utilities', label: 'Utilities', color: 'gray' },
  personal: { value: 'personal', label: 'Personal', color: 'transparent' }
};

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  location?: string;
  type: 'event' | 'milestone-achieved' | 'reminder' | 'task' | 'milestone-upcoming';
  priority: 'High' | 'Medium' | 'Low';
  description?: string;
  category?: string;
  widget_id?: string;
  widget_config?: Record<string, any>;
  activity_data?: Record<string, any>;
  due_date?: string;
  achieved_date?: string;
}

interface CalendarDay {
  date: string;
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
  todosCompleted: any[];
  todosTotal: any[];
  habitStreak: number;
  milestones: Set<any>;
  milestonesAchieved: Set<any>;
  // Enhanced data structure
  streaksByCategory?: Map<string, number>;
  top3Completed?: boolean;
  milestonesData?: {
    future: CalendarEvent[];
    past: CalendarEvent[];
  };
}

interface CalendarWeek {
  weekIndex: number;
  todosCompleted: any[];
  todosTotal: any[];
  weeklyHabitStreak: number;
}

interface CalendarData {
  year: number;
  month: number;
  days: CalendarDay[];
  weeks: CalendarWeek[];
  events: CalendarEvent[];
  milestones: CalendarEvent[];
  monthlyStats?: {
    totalTodosCompleted: number;
    totalTodos: number;
    averageCompletionRate: number;
    longestHabitStreak: number;
    totalMilestones: number;
  };
}

// Enhanced color utilities
const getCategoryColor = (category: string): string => {
  return categoryColors[category as keyof typeof categoryColors]?.color || 'gray';
};
const getStreakSize = (day: number, totalStreakDays: number): number => {
  const position = totalStreakDays - day + 1;
  return position >= 7 ? 16 : 12;
};

// Circular progress component
interface CircularProgressProps {
  todosCompleted: any[];
  todosTotal: any[];
  day: number;
  size?: number;
  strokeWidth?: number;
}

const CircularProgress = ({ todosCompleted, todosTotal, day, size = 20, strokeWidth = 3 }: CircularProgressProps) => {
  if (todosTotal.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-xs font-medium">{day}</span>
      </div>
    );
  }

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const totalTasks = todosTotal.length;
  const share = circumference / totalTasks;
  const gap = Math.min(2, share * 0.2);
  const segmentLength = Math.max(0, share - gap);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Per-task arcs */}
        {todosTotal
          .sort((a, b) => a.activity_data?.status === 'completed' ? -1 : 1)
          .sort((a, b) => a.category > b.category ? 1 : -1)
          .map((todo, index) => {
            const isCompleted = todo?.activity_data?.status === 'completed'
              || todosCompleted.includes(todo);
            const strokeColor = isCompleted ? getCategoryColor(todo?.category) : 'transparent';
            const dashArray = `${segmentLength} ${circumference - segmentLength}`;
            const dashOffset = circumference - index * share;
            return (
              <circle
                key={index}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke={strokeColor}
                strokeWidth={strokeWidth}
                fill="none"
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                className="transition-all duration-300"
              />
            );
          })}
      </svg>
      {/* Center date */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-medium text-gray-700">{day}</span>
      </div>
    </div>
  );
};


const CircularProgressConcentric = ({ todosCompleted, todosTotal, day, size = 20, strokeWidth = 3 }: CircularProgressProps) => {
  if (todosTotal.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>

        <Circle size={size-5} fill="#eeeeee" stroke="transparent" strokeWidth={strokeWidth} />
              </div>
    );
  }

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const totalTasks = todosTotal.length;
  const share = circumference / totalTasks;
  const gap = Math.min(2, share * 0.2);
  const segmentLength = Math.max(0, share - gap);

  //group todosTotal by category
  const todosByCategory = new Map<string, any[]>();
  for (const todo of todosTotal) {
    const category = todo.category;
    if (!todosByCategory.has(category)) {
      todosByCategory.set(category, []);
    }
    todosByCategory.get(category)!.push(todo);
  }

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Per-task arcs */}
        {Array.from(todosByCategory.entries()).map(([category, todos], tIndex) => (
          <g key={category}>
          {todos
          .sort((a, b) => a.activity_data?.status === 'completed' ? -1 : 1)
          .map((todo, index) => {
            const isCompleted = todo?.activity_data?.status === 'completed'
              || todosCompleted.includes(todo);
            const strokeColor = isCompleted ? getCategoryColor(todo?.category) : 'transparent';
            const dashArray = `${segmentLength} ${circumference - segmentLength}`;
            const dashOffset = circumference - index * share;
            return (
              <circle
                key={index}
                cx={size / 2}
                cy={size / 2}
                r={radius-tIndex*3}
                stroke={strokeColor}
                strokeWidth={strokeWidth}
                fill="none"
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                className="transition-all duration-300"
              />
              );
            })}
          </g>
        ))}
      </svg>
    </div>
  );
};

// Enhanced streak component
interface StreakIndicatorProps {
  streaksByCategory: Map<string, number>;
  size?: number;
}

const StreakIndicator = ({ streaksByCategory, size = 12 }: StreakIndicatorProps) => {
  if (streaksByCategory.size === 0) return null;

  return (
    <div className="flex flex-wrap">
      {Array.from(streaksByCategory.entries()).map(([category, totalStreakDays]) => {
        // For each category, we show the total streak days
        // The color will be darkest for the most recent day
        return (
          <div
            key={category}
            className="flex items-center"
            title={`${category} streak: ${totalStreakDays} days`}
          >
            <span
              className="text-orange-500"
              style={{
                fontSize: `${getStreakSize(totalStreakDays, totalStreakDays)}px`,
                color: getCategoryColor(category),
                opacity: totalStreakDays >= 7 ? 1 : 0.2 * totalStreakDays
              }}
            >
              <Flame size={12} />
            </span>
          </div>
        );
      })}
    </div>
  );
};

// Top 3 indicator component
interface Top3IndicatorProps {
  completed: boolean;
  size?: number;
}

const Top3Indicator = ({ completed, size = 12 }: Top3IndicatorProps) => {
  if (!completed) return null;

  return (
    <div className="flex items-center justify-center">
      <ThumbsUp size={size} color='green' />
    </div>
  );
};

const getEventTypeColor = (type: string) => {
  switch (type) {
    case 'event': return 'bg-blue-100 text-blue-800';
    case 'milestone-achieved': return 'bg-purple-100 text-purple-800';
    case 'milestone-upcoming': return 'bg-purple-100 text-purple-800';
    case 'reminder': return 'bg-yellow-100 text-yellow-800';
    case 'task': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'High': return 'border-red-500';
    case 'Medium': return 'border-yellow-500';
    case 'Low': return 'border-green-500';
    default: return 'border-gray-300';
  }
};

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

interface CalendarWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
}

const CalendarWidget = ({ onRemove, widget }: CalendarWidgetProps) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isUsingDummyData, setIsUsingDummyData] = useState(false);

  const fetchCalendarData = async (year: number, month: number) => {
    try {
      setLoading(true);
      setError(null);
      setIsUsingDummyData(false);

      // Compute start and end of month
      const startOfMonth = new Date(year, month - 1, 1);
      const endOfMonth = new Date(year, month, 0);

      // Fetch widgets linked to this calendar by selected_calendar
      const items = await apiService.getWidgetActivityForCalendar({
        calendar_id: widget.widget_id,
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: endOfMonth.toISOString().split('T')[0],
      });

      // Use dummy skeleton and overlay real events
      const base = getDummyCalendarData(year, month) as unknown as CalendarData;
      // Clear monthly stats when using real data
      // (keep as-is if dummy provides it, we won't display in API mode)
      // Reset events per day
      base.days = base.days.map(d => ({
        ...d,
        events: [],
        todosCompleted: [],
        todosTotal: [],
        habitStreak: 0,
        milestones: new Set(),
        streaksByCategory: new Map(),
        top3Completed: false
      }));
      base.weeks = base.weeks.map(d => ({
        ...d,
        events: [],
        todosCompleted: [],
        todosTotal: [],
        weeklyHabitStreak: 0,
      }));
      base.events = [];
      var tempMilestones: any[] = [];

      // Map API items to calendar events
      const toPriority = (p?: string): 'High' | 'Medium' | 'Low' => {
        if (p === 'HIGH') return 'High';
        if (p === 'LOW') return 'Low';
        return 'Medium';
      };

      const events = items.map(item => ({
        id: item.daily_widget_id || item.id,
        title: item.title,
        category: item.category,
        date: item.date || new Date().toISOString().split('T')[0],
        type: item.widget_type,
        priority: toPriority(item.priority),
        description: item.description,
        widget_config: item.widget_config,
        activity_data: item.activity_data,
      }));

      // Place events into days
      const dayByKey = new Map(base.days.map(d => [d.date, d] as const));
      for (const ev of events) {
        const key = ev.date;
        const day = dayByKey.get(key);
        if (day) {
          day.events.push(ev);
        }
      }

      // count total todos and completed todos for each day
      for (const day of base.days) {
        const todos = items.filter(item => item.date === day.date);
        day.todosTotal = todos;
        day.todosCompleted = todos.filter(item => item.activity_data?.status === 'completed');
      }

      // count total todos and completed todos for each day
      for (const week of base.weeks) {
        const todos = items.filter(item => item.date && item.date >= base.days[week.weekIndex*7].date && item.date <= base.days[week.weekIndex*7+6].date);
        week.todosTotal = todos;
        week.todosCompleted = todos.filter(item => item.activity_data?.status === 'completed');

      }

      // Enhanced: Calculate streaks backwards from current day
      const todayStr = new Date().toISOString().split('T')[0];
      const sortedDays = base.days
        .filter(day => day.isCurrentMonth)
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

      // Track streaks by category across all days
      const streakTracker = new Map<string, { currentStreak: number, lastCompletedDate: string | null }>();

      // Process days in chronological order to build streaks
      for (const day of sortedDays) {
        const dayItems = items.filter(item => item.date === day.date);

        for (const item of dayItems) {
          const streakType = (item as any).widget_config?.streak_type;
          const hasStreak = streakType && streakType !== 'none';

          if (!hasStreak) continue;

          const category = item.category;
          const todoActivity = (item as any).activity_data;
          const isCompleted = todoActivity?.status === 'completed' || (typeof todoActivity?.progress === 'number' && todoActivity.progress >= 100);

          if (isCompleted) {
            // Update streak tracker
            const tracker = streakTracker.get(category) || { currentStreak: 0, lastCompletedDate: null };

            // Check if this is consecutive (previous day was completed)
            const isConsecutive = tracker.lastCompletedDate &&
              new Date(day.date).getTime() - new Date(tracker.lastCompletedDate).getTime() === 86400000; // 24 hours in ms

            if (isConsecutive) {
              tracker.currentStreak++;
            } else {
              tracker.currentStreak = 1; // Reset streak
            }

            tracker.lastCompletedDate = day.date;
            streakTracker.set(category, tracker);

            // Set streak for this day (backwards calculation)
            if (!day.streaksByCategory) day.streaksByCategory = new Map();
            day.streaksByCategory.set(category, tracker.currentStreak);
          } else {
            // Task not completed, reset streak for this category
            const tracker = streakTracker.get(category) || { currentStreak: 0, lastCompletedDate: null };
            tracker.currentStreak = 0;
            tracker.lastCompletedDate = null;
            streakTracker.set(category, tracker);
          }
        }
      }

      // Add upcoming milestones from widget_config (within month and not past today)
      // Track unique widget IDs that have milestones on each day
      const milestoneWidgetsByDate = new Map<string, Set<any>>();
      const milestoneWidgetsByDateAchieved = new Map<string, Set<any>>();

      for (const item of items) {
        const milestones = Array.isArray((item as any).widget_config?.milestones) ? (item as any).widget_config.milestones : [];
        const widgetId = item.widget_id;
        console.log(item.category, "category1");

        for (const m of milestones) {
          if (!m?.due_date || tempMilestones.find(milestone => milestone.due_date === m.due_date && milestone.widget_id === item.widget_id)) continue;
          const due = new Date(m.due_date);
          if (due >= startOfMonth && due <= endOfMonth && (due >= new Date())) {
            const dateKey = m.due_date;
            const day = dayByKey.get(dateKey);
            if (day) {
              const milestoneEvent: CalendarEvent = {
                widget_id: widgetId,
                id: `${widgetId}-milestone-upcoming-${dateKey}`,
                title: m.text || `${item.title || 'Milestone'}`,
                date: dateKey,
                due_date: m.due_date,
                category: item.category,
                type: 'milestone-upcoming',
                priority: 'Medium',
                description: m.description,
              };
              // Track unique widget IDs for this date
              if (!milestoneWidgetsByDate.has(dateKey)) {
                milestoneWidgetsByDate.set(dateKey, new Set());
              }
              milestoneWidgetsByDate.get(dateKey)!.add(milestoneEvent);

              day.events.push(milestoneEvent);
              tempMilestones.push(milestoneEvent);
            }
          }
        }
      }


      //get cahieved milestones from activity_data
      for (const item of items) {
        console.log(item.category, "category2");
        const milestones = Array.isArray((item as any).activity_data?.milestones_achieved) ? (item as any).activity_data.milestones_achieved : [];
        const widgetId = item.widget_id;
        const dateKey = item.date || new Date().toISOString().split('T')[0];
        for (const m of milestones) {
          if (true) {
            const milestoneEvent: CalendarEvent = {
              widget_id: widgetId,
              id: `${widgetId}-milestone-achieved-${item.date}`,
              title: m.text || `${item.title || 'Milestone'}`,
              date: dateKey,
              category: item.category,
              achieved_date: item.date,
              type: 'milestone-achieved',
              priority: 'Medium',
              description: m.description,
            };
            if (!milestoneWidgetsByDateAchieved.has(dateKey)) {
              milestoneWidgetsByDateAchieved.set(dateKey, new Set());
            }
            milestoneWidgetsByDateAchieved.get(dateKey)!.add(milestoneEvent);

            base.events.push(milestoneEvent);
            tempMilestones.push(milestoneEvent);
          }
        }
      }

      // Update milestone counts based on unique widget IDs
      for (const [dateKey, widgetSet] of milestoneWidgetsByDateAchieved) {
        const day = dayByKey.get(dateKey);
        if (day) {
          day.milestonesAchieved = widgetSet; // Count unique widget IDs
        }
      }
      // Update milestone counts based on unique widget IDs
      for (const [dateKey, widgetSet] of milestoneWidgetsByDate) {
        const day = dayByKey.get(dateKey);
        if (day) {
          day.milestones = widgetSet; // Count unique widget IDs
        }
      }

      // Enhanced: Add dummy top 3 completion data for UI testing
      for (const day of base.days) {
        // Simulate top 3 completion (random for now)
        day.top3Completed = Math.random() > 0.7; // 30% chance of completion
      }

      base.events = events;
      setCalendarData(base);
    } catch (err) {
      setError('Failed to load calendar data');
      setIsUsingDummyData(true);
      console.error('Error fetching calendar data:', err);
    } finally {
      setLoading(false);
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
    fetchCalendarData(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    fetchCalendarData(today.getFullYear(), today.getMonth() + 1);
  };

  useEffect(() => {
    fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1);
  }, []);

  if (loading) {
    return (
      <BaseWidget title="Calendar" icon="📅" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="Calendar" icon="📅" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-red-600 mb-2">{error}</p>
          <button
            onClick={() => fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1)}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  if (!calendarData) {
    return (
      <BaseWidget title="Calendar" icon="📅" onRemove={onRemove}>
        <div className="text-center py-8 text-gray-500">
          <p>No calendar data available</p>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title={widget.title} icon="📅" onRemove={onRemove}>
      <div className="px-4">
        {/* Calendar Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronLeft size={16} />
            </button>
            <h3 className="font-semibold text-lg">
              {monthNames[calendarData.month - 1]} {calendarData.year}
            </h3>
            <button
              onClick={() => navigateMonth('next')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronRight size={16} />
            </button>
          </div>
          <button
            onClick={goToToday}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Today
          </button>
        </div>

        {/* Dummy Data Indicator */}
        {isUsingDummyData && (
          <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-700 text-center">
              📅 Showing sample data - API not connected
            </p>
          </div>
        )}

        <div className="flex flex-row">
          <div className="flex flex-col">

            <div className="text-center text-xs font-medium text-transparent">
              0
            </div>
            {/* Enhanced Calendar Grid */}
            <div className="grid grid-cols-1">
              {calendarData.weeks.map((week, index) => (
                <div key={index} className="min-h-[40px] ">
                  <div className="flex flex-col items-center">
                    <div className="">
                      <CircularProgressConcentric
                        todosCompleted={week.todosCompleted}
                        todosTotal={week.todosTotal}
                        day={week.weekIndex}
                        size={25}
                        strokeWidth={2}
                      />
                    </div>
                    {/* {week.isCurrentMonth && week.streaksByCategory && week.streaksByCategory.size > 0 && (
                      <div className="">
                        <StreakIndicator streaksByCategory={week.streaksByCategory} />
                      </div>
                    )} */}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-col flex-1">
            {/* Day Headers */}
            <div className="grid grid-cols-7 ">
              {dayNames.map(day => (
                <div key={day} className="text-center text-xs font-medium text-gray-600 ">
                  {day}
                </div>
              ))}
            </div>

            {/* Enhanced Calendar Grid */}
            <div className="grid grid-cols-7">
              {calendarData.days.map((day, index) => (
                <div
                  key={index}
                  className={`min-h-[40px] text-xs  rounded ${!day.isCurrentMonth ? 'bg-gray-50 text-gray-300' : 'bg-white text-gray-500'
                    } ${day.isToday ? 'bg-blue-500' : 'text-gray-500'}`}
                >
                  {/* Enhanced Day Header with Streaks */}
                  <div className="flex flex-col items-center">
                    {/* Streak Indicators */}
                    {/* Date with Circular Progress */}
                    <div className="">
                      <CircularProgress
                        todosCompleted={day.todosCompleted}
                        todosTotal={day.todosTotal}
                        day={day.day}
                        size={25}
                        strokeWidth={2}
                      />
                    </div>
                  </div>

                  {/* Enhanced Events Display */}
                  <div className="flex flex-row justify-center items-center">
                    {/* Milestone Indicator */}
                    {day.isCurrentMonth && day.milestonesAchieved?.size > 0 && (
                      <div>
                        {Array.from(day.milestonesAchieved).map((milestone) => (
                          <div key={milestone.id} className="">
                            <Trophy size={10} color={getCategoryColor(milestone.category)} />
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Milestone Indicator */}
                    {day.isCurrentMonth && day.milestones?.size > 0 && (
                      <div className="">
                        {Array.from(day.milestones).map((milestone) => (
                          <div key={milestone.id} className="">
                            <Trophy size={10} color={getCategoryColor(milestone.category)} />
                          </div>
                        ))}
                      </div>
                    )}


                    {/* Top 3 Indicator */}
                    {day.isCurrentMonth && day.top3Completed && (
                      <div className="">
                        <Top3Indicator completed={day.top3Completed} size={10} />
                      </div>
                    )}
                    {day.isCurrentMonth && day.streaksByCategory && day.streaksByCategory.size > 0 && (
                      <div className="">
                        <StreakIndicator streaksByCategory={day.streaksByCategory} />
                      </div>
                    )}

                  </div>

                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">{selectedEvent.title}</h3>
                <div className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 ${getEventTypeColor(selectedEvent.type)}`}>
                  {selectedEvent.type}
                </div>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <ChevronRight size={20} />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-gray-500" />
                <span className="text-sm text-gray-700">
                  {new Date(selectedEvent.date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>

              {selectedEvent.time && (
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-gray-500" />
                  <span className="text-sm text-gray-700">{selectedEvent.time}</span>
                </div>
              )}

              {selectedEvent.location && (
                <div className="flex items-center gap-2">
                  <MapPin size={16} className="text-gray-500" />
                  <span className="text-sm text-gray-700">{selectedEvent.location}</span>
                </div>
              )}

              {selectedEvent.description && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-1">Description</h4>
                  <p className="text-sm text-gray-600">{selectedEvent.description}</p>
                </div>
              )}

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Priority:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(selectedEvent.priority).replace('border-', 'bg-').replace('-500', '-100')} text-gray-700`}>
                  {selectedEvent.priority}
                </span>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                onClick={() => setSelectedEvent(null)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Close
              </button>
              <button
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Edit Event
              </button>
            </div>
          </div>
        </div>
      )}
    </BaseWidget>
  );
};

export default CalendarWidget; 