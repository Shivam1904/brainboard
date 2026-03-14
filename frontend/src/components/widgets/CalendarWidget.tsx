import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight, Calendar, Clock, MapPin, Circle, Trophy, ThumbsUp, Flame, Pencil, Check } from 'lucide-react';
import { DailyWidget, apiService, DashboardWidget } from '../../services/api';
import { formatDate, getTodayDateString, toLocalISOString } from '../../utils/dateUtils';


import { categoryColors } from '../../constants/widgetConstants';
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
  widget_config?: Record<string, unknown>;
  activity_data?: Record<string, unknown>;
  due_date?: string;
  achieved_date?: string;
}

interface CalendarDay {
  date: string;
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
  todosCompleted: DailyWidget[];
  todosTotal: DailyWidget[];
  habitStreak: number;
  milestones: Set<CalendarEvent>;
  milestonesAchieved: Set<CalendarEvent>;
  // Enhanced data structure
  streaksByCategory?: Map<string, number>;
  top3Completed: boolean;
  milestonesData?: {
    future: CalendarEvent[];
    past: CalendarEvent[];
  };
}

interface CalendarWeek {
  weekIndex: number;
  todosCompleted: DailyWidget[];
  todosTotal: DailyWidget[];
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
  if (!category) return 'gray';
  const lowerCategory = category.toLowerCase();
  return categoryColors[lowerCategory as keyof typeof categoryColors]?.color || 'gray';
};
const getCategoryColorHex = (category: string): string => {
  if (!category) return '#6b7280';
  const lowerCategory = category.toLowerCase();
  const hex = categoryColors[lowerCategory as keyof typeof categoryColors]?.hex;
  return (hex && hex !== 'transparent' ? hex : '#6b7280') as string;
};
/** Returns rgba string for the category color with the given opacity (0–1). Use for stroke so fill can stay opaque. */
const getCategoryColorWithOpacity = (category: string, opacity: number): string => {
  const hex = getCategoryColorHex(category);
  if (hex === 'transparent') return 'transparent';
  const clean = hex.replace(/^#/, '');
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${opacity})`;
};
const getStreakSize = (day: number, totalStreakDays: number): number => {
  const position = totalStreakDays - day + 1;
  return position >= 7 ? 16 : 12;
};

// Circular progress component
interface CircularProgressProps {
  todosCompleted: DailyWidget[];
  todosTotal: DailyWidget[];
  day: number;
  size?: number;
  strokeWidth?: number;
  isToday?: boolean;
  isCurrentMonth?: boolean;
}

const CircularProgress = ({ todosCompleted, todosTotal, day, size = 20, strokeWidth = 3, isToday = false, isCurrentMonth = false }: CircularProgressProps) => {
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
        {((todosTotal.length > 0) || isToday) && (<circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill={isToday ? 'white' : 'none'}
        />)}
        {/* Per-task arcs */}
        {(todosTotal as DailyWidget[])
          .sort((a, b) => (a.category as string) > (b.category as string) ? 1 : -1)
          .sort((a) => (a.activity_data as Record<string, unknown>)?.status === 'completed' ? -1 : 1)
          .map((todo, index) => {
            const isCompleted = (todo?.activity_data as Record<string, unknown>)?.status === 'completed'
              || todosCompleted.includes(todo);
            const dashOffset = circumference - index * share;
            return (
              <circle
                key={index}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke={isCompleted ? getCategoryColorHex(todo.category as string) : 'transparent'}
                strokeWidth={isToday ? strokeWidth + 1 : strokeWidth}
                fill="none"
                strokeDasharray={`${segmentLength} ${circumference - segmentLength}`}
                strokeDashoffset={dashOffset}
                className="transition-all duration-300"
              />
            );
          })}
      </svg>
      {/* Center date */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-xs font-medium ${isToday ? 'text-gray-700' : isCurrentMonth ? 'text-gray-500' : 'text-gray-300'}`}>{day}</span>
      </div>
    </div>
  );
};


const CircularProgressConcentric = ({ todosCompleted, todosTotal, size = 20, strokeWidth = 3 }: CircularProgressProps) => {
  if (todosTotal.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>

        <Circle size={size - 5} fill="#eeeeee" stroke="transparent" strokeWidth={strokeWidth} />
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
  const todosByCategory = new Map<string, unknown[]>();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  for (const todo of (todosTotal as any[])) {
    const category = todo.category as string;
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
        {/* Per-task arcs */}
        {Array.from(todosByCategory.entries()).map(([category, todos], tIndex) => (
          <g key={category}>
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius - tIndex * 3}
              stroke="#E5E7EB"
              strokeWidth={strokeWidth}
              fill="none"
            />
            {(todos as Record<string, unknown>[])
              .sort((a, _) => (a.activity_data as Record<string, unknown>)?.status === 'completed' ? -1 : 1)
              .map((todo, index) => {
                const isCompleted = (todo?.activity_data as Record<string, unknown>)?.status === 'completed'
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  || (todosCompleted as any[]).includes(todo);
                const strokeColor = isCompleted ? getCategoryColor(todo?.category as string) : 'transparent';
                const dashArray = `${segmentLength} ${circumference - segmentLength}`;
                const dashOffset = circumference - index * share;
                return (
                  <circle
                    key={index}
                    cx={size / 2}
                    cy={size / 2}
                    r={radius - tIndex * 3}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeDasharray={dashArray}
                    strokeDashoffset={dashOffset}
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

const StreakIndicator = ({ streaksByCategory }: StreakIndicatorProps) => {
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
            {totalStreakDays < 7 && (<span
              className=""
              style={{ fontSize: `${getStreakSize(totalStreakDays, totalStreakDays)}px` }}
            >
              <Flame
                size={12}
                fill="white"
                stroke={getCategoryColorWithOpacity(category, totalStreakDays >= 7 ? 1 : 0.16 * totalStreakDays)}
                strokeWidth={2}
              />
            </span>)}

            {totalStreakDays >= 7 && (<span
              className=""
              style={{
                fontSize: `${getStreakSize(totalStreakDays, totalStreakDays)}px`,
                color: getCategoryColor(category),
                opacity: totalStreakDays >= 7 ? 1 : 0.2 * totalStreakDays
              }}
            >
              <span className="text-xs">🔥</span>
            </span>)}
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
      <ThumbsUp size={size} color='green' fill='white' />
    </div>
  );
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
  targetDate: string;
}

// Helper function to generate calendar structure without dummy data
const generateCalendarStructure = (year: number, month: number, targetDate: string): CalendarData => {
  const firstDay = new Date(year, month - 1, 1);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday

  const days: CalendarDay[] = [];

  // Generate 42 days (6 weeks) to fill the calendar grid
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);

    const isCurrentMonth = date.getMonth() === month - 1;
    const isToday = toLocalISOString(date) === targetDate;

    days.push({
      date: toLocalISOString(date),
      day: date.getDate(),
      isCurrentMonth,
      isToday,
      events: [],
      todosCompleted: [],
      todosTotal: [],
      habitStreak: 0,
      milestones: new Set(),
      milestonesAchieved: new Set(),
      streaksByCategory: new Map(),
      top3Completed: false,
    });
  }

  // Generate weeks structure
  const weeks: CalendarWeek[] = [];
  for (let i = 0; i < 6; i++) {
    weeks.push({
      weekIndex: i,
      todosCompleted: [],
      todosTotal: [],
      weeklyHabitStreak: 0,
    });
  }

  return {
    year,
    month,
    days,
    weeks,
    events: [],
    milestones: []
  };
};

const CalendarWidget = ({ onRemove, widget, targetDate }: CalendarWidgetProps) => {
  const [currentDate, setCurrentDate] = useState(new Date(targetDate));
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);

  // New state for widget selection
  const [availableWidgets, setAvailableWidgets] = useState<DashboardWidget[]>([]);
  const [selectedWidgets, setSelectedWidgets] = useState<Set<string>>(new Set());
  // const [showWidgetSelector, setShowWidgetSelector] = useState(false);
  // const [loadingWidgets, setLoadingWidgets] = useState(false);
  // const [updatingWidget, setUpdatingWidget] = useState<string | null>(null);
  // const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [editingWidgets, setEditingWidgets] = useState(false);
  const fetchCalendarData = async (year: number, month: number) => {
    try {
      setLoading(true);
      setError(null);

      // Compute start and end of month
      const startOfMonth = new Date(year, month - 1, 1);
      const endOfMonth = new Date(year, month, 0);

      // Fetch widgets linked to this calendar by selected_calendar
      const items = await apiService.getWidgetActivityForCalendar({
        calendar_id: widget.widget_id,
        start_date: toLocalISOString(startOfMonth),
        end_date: toLocalISOString(endOfMonth),
        calendar_type: 'monthly'
      });

      // Generate calendar structure without dummy data
      const base = generateCalendarStructure(year, month, targetDate);
      const tempMilestones: unknown[] = [];

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
        date: item.date || getTodayDateString(),
        type: (item.widget_type === 'event' || item.widget_type === 'milestone-achieved' || item.widget_type === 'reminder' || item.widget_type === 'task' || item.widget_type === 'milestone-upcoming')
          ? item.widget_type as 'event' | 'milestone-achieved' | 'reminder' | 'task' | 'milestone-upcoming'
          : 'event',
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

      // count total todos and completed todos for each week
      for (const week of base.weeks) {
        const todos = items.filter(item => item.date && item.date >= base.days[week.weekIndex * 7].date && item.date <= base.days[week.weekIndex * 7 + 6].date);
        week.todosTotal = todos;
        week.todosCompleted = todos.filter(item => item.activity_data?.status === 'completed');
      }

      // Enhanced: Calculate streaks backwards from current day
      // const todayStr = new Date().toISOString().split('T')[0];
      const sortedDays = base.days
        .filter(day => day.isCurrentMonth)
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

      // Track streaks by category across all days
      const streakTracker = new Map<string, { currentStreak: number, lastCompletedDate: string | null }>();

      // Process days in chronological order to build streaks
      for (const day of sortedDays) {
        const dayItems = items.filter(item => item.date === day.date);

        for (const item of dayItems) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const streakType = (item as any).widget_config?.streak_type;
          const hasStreak = streakType && streakType !== 'none';

          if (!hasStreak) continue;

          const category = item.category as string;
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
      const milestoneWidgetsByDate = new Map<string, Set<unknown>>();
      const milestoneWidgetsByDateAchieved = new Map<string, Set<unknown>>();

      for (const item of items) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const itemObj = item as any;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const milestones = Array.isArray(itemObj.widget_config?.milestones) ? (itemObj.widget_config?.milestones as any[]) : [];
        const widgetId = item.widget_id;

        for (const m of (milestones as Record<string, unknown>[])) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          if (!m?.due_date || (tempMilestones as any[]).find(milestone => milestone.due_date === m.due_date && milestone.widget_id === item.widget_id)) continue;
          const due = new Date(m.due_date as string);
          if (due >= startOfMonth && due <= endOfMonth && (due >= new Date())) {
            const dateKey = m.due_date as string;
            const day = dayByKey.get(dateKey);
            if (day) {
              const milestoneEvent: CalendarEvent = {
                widget_id: widgetId,
                id: `${widgetId}-milestone-upcoming-${dateKey}`,
                title: (m.text as string) || `${item.title || 'Milestone'}`,
                date: dateKey,
                due_date: m.due_date as string,
                category: item.category,
                type: 'milestone-upcoming',
                priority: 'Medium',
                description: m.description as string,
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

      //get achieved milestones from activity_data
      for (const item of items) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const itemObj = item as any;
        const activityData = itemObj.activity_data;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const milestones = Array.isArray(activityData?.milestones_achieved) ? (activityData?.milestones_achieved as any[]) : [];
        const widgetId = item.widget_id;
        const dateKey = item.date || getTodayDateString();

        for (const m of (milestones as Record<string, unknown>[])) {
          if (!m?.achieved_date) continue;
          // const achieved = new Date(m.achieved_date);
          const milestoneEvent: CalendarEvent = {
            widget_id: widgetId,
            id: `${widgetId}-milestone-achieved-${item.date}`,
            title: (m.text as string) || `${item.title || 'Milestone'}`,
            date: dateKey,
            category: item.category,
            achieved_date: item.date,
            type: 'milestone-achieved',
            priority: 'Medium',
            description: m.description as string,
          };
          if (!milestoneWidgetsByDateAchieved.has(dateKey)) {
            milestoneWidgetsByDateAchieved.set(dateKey, new Set());
          }
          milestoneWidgetsByDateAchieved.get(dateKey)!.add(milestoneEvent);

          base.events.push(milestoneEvent);
          tempMilestones.push(milestoneEvent);
        }
      }

      // Update milestone counts based on unique widget IDs
      for (const [dateKey, widgetSet] of milestoneWidgetsByDateAchieved) {
        const day = dayByKey.get(dateKey);
        if (day) {
          day.milestonesAchieved = widgetSet as Set<CalendarEvent>; // Count unique widget IDs
        }
      }

      for (const [dateKey, widgetSet] of milestoneWidgetsByDate) {
        const day = dayByKey.get(dateKey);
        if (day) {
          day.milestones = widgetSet as Set<CalendarEvent>; // Count unique widget IDs
        }
      }

      // Enhanced: Add dummy top 3 completion data for UI testing
      for (const day of base.days) {
        // Simulate top 3 completion (random for now)
        day.top3Completed = Math.random() > 0.7; // 30% chance of completion
      }

      setCalendarData(base);
    } catch (err) {
      setError('Failed to load calendar data');
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

  /*
    const goToToday = () => {
      const today = new Date();
      setCurrentDate(today);
      fetchCalendarData(today.getFullYear(), today.getMonth() + 1);
    };
  */

  // Fetch available widgets for selection
  const fetchAvailableWidgets = async () => {
    try {
      // setLoadingWidgets(true);
      setError(null);
      const widgets = await apiService.getAllWidgets();
      // Filter out the current calendar widget and only show task-like widgets
      const taskWidgets = widgets.filter(w =>
        w.id !== widget.widget_id &&
        !['allSchedules', 'aiChat', 'simpleClock', 'weatherWidget', 'calendar', 'pillarsGraph', 'yearCalendar', 'moodTracker', 'notes', 'habitTracker'].includes(w.widget_type)
      );
      setAvailableWidgets(taskWidgets);

      // Initialize selected widgets based on current widget_config.selected_calendar
      const currentSelected = new Set<string>();
      for (const w of taskWidgets) {
        if (w.widget_config?.selected_calendar === widget.widget_id) {
          currentSelected.add(w.id);
        }
      }
      setSelectedWidgets(currentSelected);
    } catch (err) {
      console.error('Error fetching available widgets:', err);
      setError('Failed to load available widgets');
    } finally {
      // setLoadingWidgets(false);
    }
  };

  // Handle widget selection/deselection
  const handleWidgetSelection = async (widgetId: string, isSelected: boolean) => {
    try {
      // setUpdatingWidget(widgetId);
      setError(null);
      // setSuccessMessage(null);

      const newSelected = new Set(selectedWidgets);
      if (isSelected) {
        newSelected.add(widgetId);
      } else {
        newSelected.delete(widgetId);
      }
      setSelectedWidgets(newSelected);

      // Update the widget's selected_calendar field
      const widgetToUpdate = availableWidgets.find(w => w.id === widgetId);
      if (!widgetToUpdate) {
        throw new Error('Widget not found');
      }

      const updateData = {
        widget_config: {
          ...widgetToUpdate.widget_config,
          selected_calendar: isSelected ? widget.widget_id : null
        }
      };

      await apiService.updateWidget(widgetId, updateData);

      // Show success message
      // setSuccessMessage(`Task "${widgetToUpdate.title}" ${isSelected ? 'added to' : 'removed from'} calendar`);
      // setTimeout(() => setSuccessMessage(null), 3000);

      // Refresh calendar data to show the changes
      await fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    } catch (err) {
      console.error('Error updating widget calendar selection:', err);
      // Revert the selection if update failed
      const reverted = new Set(selectedWidgets);
      if (isSelected) {
        reverted.delete(widgetId);
      } else {
        reverted.add(widgetId);
      }
      setSelectedWidgets(reverted);

      // Show error to user
      setError('Failed to update widget selection. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      // setUpdatingWidget(null);
    }
  };

  /*
    // Refresh both calendar data and available widgets
    const refreshAllData = async () => {
      await Promise.all([
        fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1),
        fetchAvailableWidgets()
      ]);
    };
  */



  useEffect(() => {
    fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    fetchAvailableWidgets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      <div className="px-4 pt-4">
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
        </div>


        {/* Enhanced Calendar Grid */}
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
                  className={`min-h-[40px] text-xs  rounded 
                    ${!day.isCurrentMonth ? 'text-gray-300' : 'text-gray-500'}`}
                >
                  {/* Enhanced Day Header with Streaks */}
                  <div className="flex flex-col items-center relative ml-2">
                    {/* Streak Indicators */}
                    {/* Date with Circular Progress */}
                    <div className="absolute top-0 left-0">
                      <CircularProgress
                        isToday={day.isToday}
                        isCurrentMonth={day.isCurrentMonth}
                        todosCompleted={day.todosCompleted}
                        todosTotal={day.todosTotal}
                        day={day.day}
                        size={25}
                        strokeWidth={2}
                      />
                    </div>

                    {/* Enhanced Events Display */}
                    <div className="absolute top-0 left-0 flex">
                      <div className="flex flex-row justify-end items-center pt-4">
                        {/* Milestone Indicator */}
                        {day.isCurrentMonth && day.milestonesAchieved?.size > 0 && (
                          <div>
                            {Array.from(day.milestonesAchieved).map((milestone) => (
                              <div key={milestone.id} className="">
                                <Trophy size={12} color={getCategoryColor(milestone.category || 'gray')}
                                />
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Milestone Indicator */}
                        {day.isCurrentMonth && day.milestones?.size > 0 && (
                          <div className="">
                            {Array.from(day.milestones).map((milestone) => (
                              <div key={milestone.id + milestone.date} className="">
                                <Trophy size={12} fill='white'
                                  stroke={getCategoryColor(milestone.category || 'gray')} strokeWidth={2} />
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
                  </div>


                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Task List Section */}
      <div className="">
        {editingWidgets && (
          <div className="px-2">
            {availableWidgets.map((event, index) => (
              <span key={event.id}
                onClick={() => handleWidgetSelection(event.id, !selectedWidgets.has(event.id))}
                className={` text-sm
                      ${selectedWidgets.has(event.id)
                    ? 'font-bold'
                    : ''
                  } text-${getCategoryColor(event.category)}-600`}>
                {event.title + (index < availableWidgets.length - 1 ? ', ' : '')}
              </span>
            ))}
            <button
              onClick={() => setEditingWidgets(false)}
              className="text-gray-500 text-sm ml-1"
            >
              <Check size={10} />
            </button>
          </div>
        )}
        {!editingWidgets && (
          <div className="px-2">
            {availableWidgets.filter(event => selectedWidgets.has(event.id)).map((event, index) => (
              <span key={event.id}
                onClick={() => handleWidgetSelection(event.id, !selectedWidgets.has(event.id))}
                className={`text-gray-500 text-sm
                      ${selectedWidgets.has(event.id)
                    ? 'font-bold'
                    : ''
                  } text-${getCategoryColor(event.category)}-600`}>
                {event.title + (index < availableWidgets.filter(event => selectedWidgets.has(event.id)).length - 1 ? ', ' : '')}
              </span>
            ))}
            <button
              onClick={() => setEditingWidgets(true)}
              className="text-gray-500 text-sm ml-1"
            >
              <Pencil size={10} />
            </button>
          </div>
        )}
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">{selectedEvent.title}</h3>
                <div className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 text-${getCategoryColor(selectedEvent.category || 'gray')}`}>
                  {selectedEvent.category}
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
                  {formatDate(new Date(selectedEvent.date), {
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