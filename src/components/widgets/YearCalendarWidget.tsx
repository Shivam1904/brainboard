import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight, Calendar, Clock, MapPin, X, Pencil, Check } from 'lucide-react';
import { DailyWidget, apiService, DashboardWidget } from '../../services/api';

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
  streaksByCategory?: Map<string, number>;
  top3Completed: boolean;
  milestonesData?: {
    future: CalendarEvent[];
    past: CalendarEvent[];
  };
}

// Enhanced color utilities
const getCategoryColor = (category: string): string => {
  return categoryColors[category as keyof typeof categoryColors]?.color || 'gray';
};

// Circular progress component for the heatmap
interface CircularProgressProps {
  todosCompleted: any[];
  todosTotal: any[];
  day: number;
  size?: number;
  strokeWidth?: number;
  isToday?: boolean;
}

const CircularProgress = ({ todosCompleted, todosTotal, day, size = 12, strokeWidth = 1.5, isToday = false }: CircularProgressProps) => {
  if (todosTotal.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>
      </div>
    );
  }

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const totalTasks = todosTotal.length;
  const share = circumference / totalTasks;
  const gap = Math.min(0.5, share * 0.2);
  const segmentLength = Math.max(0, share - gap);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        {todosTotal.length > 0 && (<circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill={isToday ? 'white' : 'none'}
        />)}
        {/* Per-task arcs */}
        {todosTotal
          .sort((a, b) => a.category > b.category ? 1 : -1)
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
                r={isToday ? radius : radius}
                stroke={strokeColor}
                strokeWidth={isToday ? strokeWidth + 0.5 : strokeWidth}
                fill="none"
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                className="transition-all duration-300"
              />
            );
          })}
      </svg>
    </div>
  );
};

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

interface YearCalendarWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
}

// Helper function to generate 6-month calendar structure (5 months before + 1 month after today)
const generateSixMonthCalendarStructure = (centerDate: string): CalendarDay[] => {
  const days: CalendarDay[] = [];
  
  // Calculate the 6-month period
  const today = new Date(centerDate);
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  
  // Start date: 5 months before today
  const startDate = new Date(currentYear, currentMonth - 5, 1);
  // End date: 1 month after today
  const endDate = new Date(currentYear, currentMonth + 1, 0);
  
  // Generate days for the 6-month period
  for (let i = 0; i <= (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24); i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    const isToday = date.toISOString().split('T')[0] === centerDate;

    days.push({
      date: date.toISOString().split('T')[0],
      day: date.getDate(),
      isCurrentMonth: true,
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

  return days;
};

// Group days by weeks for the grid layout
const groupDaysByWeeks = (days: CalendarDay[]) => {
  const weeks: (CalendarDay | null)[][] = [];
  let currentWeek: (CalendarDay | null)[] = [];
  
  days.forEach((day, index) => {
    // Add empty cells for days before the first day of the year
    if (index === 0 && new Date(day.date).getDay() > 0) {
      for (let i = 0; i < new Date(day.date).getDay(); i++) {
        currentWeek.push(null);
      }
    }
    
    currentWeek.push(day);
    
    // Start new week on Sunday
    if (new Date(day.date).getDay() === 6 || index === days.length - 1) {
      weeks.push([...currentWeek]);
      currentWeek = [];
    }
  });
  
  return weeks;
};

const YearCalendarWidget = ({ onRemove, widget, targetDate }: YearCalendarWidgetProps) => {
  const [yearlyCalendarData, setYearlyCalendarData] = useState<CalendarDay[]>([]);
  const [currentDate, setCurrentDate] = useState(targetDate);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);

  // New state for widget selection
  const [availableWidgets, setAvailableWidgets] = useState<DashboardWidget[]>([]);
  const [selectedWidgets, setSelectedWidgets] = useState<Set<string>>(new Set());
  const [loadingWidgets, setLoadingWidgets] = useState(false);
  const [updatingWidget, setUpdatingWidget] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [editingWidgets, setEditingWidgets] = useState(false);

  const fetchSixMonthCalendarData = async (centerDate: string) => {
    try {
      setLoading(true);
      setError(null);

      // Calculate the 6-month period for API call
      const today = new Date(centerDate);
      const currentMonth = today.getMonth();
      const currentYear = today.getFullYear();
      
      // Start date: 5 months before today
      const startDate = new Date(currentYear, currentMonth - 5, 1);
      // End date: 1 month after today
      const endDate = new Date(currentYear, currentMonth + 1, 0);

      // Fetch widgets linked to this calendar by selected_yearly_calendar
      const items = await apiService.getWidgetActivityForCalendar({
        calendar_id: widget.widget_id,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        calendar_type: 'yearly'
      });

      // Generate 6-month calendar structure
      const base = generateSixMonthCalendarStructure(centerDate);

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
        type: (item.widget_type === 'event' || item.widget_type === 'milestone-achieved' || item.widget_type === 'reminder' || item.widget_type === 'task' || item.widget_type === 'milestone-upcoming')
          ? item.widget_type as 'event' | 'milestone-achieved' | 'reminder' | 'task' | 'milestone-upcoming'
          : 'event',
        priority: toPriority(item.priority),
        description: item.description,
        widget_config: item.widget_config,
        activity_data: item.activity_data,
      }));

      // Place events into days
      const dayByKey = new Map(base.map(d => [d.date, d] as const));
      
      for (const ev of events) {
        const key = ev.date;
        const day = dayByKey.get(key);
        if (day) {
          day.events.push(ev);
        }
      }

      // Count total todos and completed todos for each day
      for (const day of base) {
        const todos = items.filter(item => item.date === day.date);
        day.todosTotal = todos;
        day.todosCompleted = todos.filter(item => item.activity_data?.status === 'completed');
      }

      setYearlyCalendarData(base);
    } catch (err) {
      setError('Failed to load yearly calendar data');
      console.error('Error fetching yearly calendar data:', err);
    } finally {
      setLoading(false);
    }
  };

  const navigatePeriod = (direction: 'prev' | 'next') => {
    // For 6-month view, we'll shift the target date by 6 months
    const today = new Date(currentDate);
    const shiftMonths = direction === 'prev' ? -1 : 1;
    today.setMonth(today.getMonth() + shiftMonths);
    const newTargetDate = today.toISOString().split('T')[0];
    setCurrentDate(newTargetDate);
    // Update the targetDate prop would require parent component changes
    // For now, we'll just refetch with the current targetDate
    fetchSixMonthCalendarData(newTargetDate);
  };

  // Fetch available widgets for selection
  const fetchAvailableWidgets = async () => {
    try {
      setLoadingWidgets(true);
      const widgets = await apiService.getAllWidgets();
      // Filter out the current calendar widget and only show task-like widgets
      const taskWidgets = widgets.filter(w =>
        w.id !== widget.widget_id &&
        !['allSchedules', 'aiChat', 'simpleClock', 'weatherWidget', 'calendar','yearCalendar', 'moodTracker', 'notes', 'habitTracker'].includes(w.widget_type)
      );
      setAvailableWidgets(taskWidgets);

      // Initialize selected widgets based on current widget_config.selected_yearly_calendar
      const currentSelected = new Set<string>();
      for (const w of taskWidgets) {
        if (w.widget_config?.selected_yearly_calendar === widget.widget_id) {
          currentSelected.add(w.id);
        }
      }
      setSelectedWidgets(currentSelected);
    } catch (err) {
      console.error('Error fetching available widgets:', err);
      setError('Failed to load available widgets');
    } finally {
      setLoadingWidgets(false);
    }
  };

  // Handle widget selection/deselection
  const handleWidgetSelection = async (widgetId: string, isSelected: boolean) => {
    try {
      setUpdatingWidget(widgetId);
      setError(null);
      setSuccessMessage(null);

      const newSelected = new Set(selectedWidgets);
      if (isSelected) {
        newSelected.add(widgetId);
      } else {
        newSelected.delete(widgetId);
      }
      setSelectedWidgets(newSelected);

      // Update the widget's selected_yearly_calendar field
      const widgetToUpdate = availableWidgets.find(w => w.id === widgetId);
      if (!widgetToUpdate) {
        throw new Error('Widget not found');
      }

      const updateData = {
        widget_config: {
          ...widgetToUpdate.widget_config,
          selected_yearly_calendar: isSelected ? widget.widget_id : null
        }
      };

      await apiService.updateWidget(widgetId, updateData);

      // Show success message
      setSuccessMessage(`Task "${widgetToUpdate.title}" ${isSelected ? 'added to' : 'removed from'} calendar`);
      setTimeout(() => setSuccessMessage(null), 3000);

      // Refresh calendar data to show the changes
      await fetchSixMonthCalendarData(currentDate);
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
      setUpdatingWidget(null);
    }
  };



  useEffect(() => {
    fetchSixMonthCalendarData(currentDate);
    fetchAvailableWidgets();
  }, []);

  if (loading) {
    return (
      <BaseWidget title="6-Month Calendar" icon="📅" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }
  if (!yearlyCalendarData || yearlyCalendarData.length === 0) {
    return (
      <BaseWidget title="6-Month Calendar" icon="📅" onRemove={onRemove}>
        <div className="text-center py-8 text-gray-500">
          <p>No 6-month calendar data available</p>
        </div>
      </BaseWidget>
    );
  }

  const weeks = groupDaysByWeeks(yearlyCalendarData);
  const isToday = (date: string): boolean => {
    const today = new Date();
    return date === today.toISOString().split('T')[0];
  };

  return (
    <BaseWidget title={widget.title} icon="📅" onRemove={onRemove}>
      <div className="px-4 pt-4">
        {/* 6-Month Header */}
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => navigatePeriod('prev')}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <ChevronLeft size={16} />
              </button>
              <h3 className="font-semibold text-lg mx-2">
                {(() => {
                  const today = new Date(currentDate);
                  const currentMonth = today.getMonth();
                  const currentYear = today.getFullYear();
                  
                  // Get 6 months: 5 before + current + 1 after
                  const startMonth = monthNames[((currentMonth - 5 + 12) % 12)];
                  const endMonth = monthNames[((currentMonth + 1) % 12)];
                  const startYear = currentMonth - 5 < 0 ? currentYear - 1 : currentYear;
                  const endYear = currentMonth + 1 > 11 ? currentYear + 1 : currentYear;
                  
                  if (startYear === endYear) {
                    return `${startMonth} - ${endMonth} ${startYear}`;
                  } else {
                    return `${startMonth} ${startYear} - ${endMonth} ${endYear}`;
                  }
                })()}
              </h3>
              <button
                onClick={() => navigatePeriod('next')}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* 6-Month Heatmap Grid */}
        <div className="w-full">
          {/* Heatmap grid */}
          <div className="flex">
            
            {/* Heatmap squares */}
            <div className="flex-1">
              <div className="flex">
                {weeks.map((week, weekIndex) => (
                  <div key={weekIndex} className="flex flex-col">
                    {week.map((day: CalendarDay | null, dayIndex: number) => {
                      if (!day) {
                        return <div key={dayIndex} className="w-3 h-3" />;
                      }
                      
                      return (
                        <div
                          key={dayIndex}
                          className={`w-3 h-3 rounded-sm transition-all ${
                            isToday(day.date) ? 'bg-gray-100 border border-blue-500' : 'bg-white/50'
                          }`}
                          title={`${day.date}: ${day.todosTotal.length} tasks, ${day.todosCompleted.length} completed`}
                        >
                          <CircularProgress
                            todosCompleted={day.todosCompleted}
                            todosTotal={day.todosTotal}
                            day={day.day}
                            size={12}
                            strokeWidth={4}
                            isToday={isToday(day.date)}
                          />
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Month labels */}
          <div className="w-[22rem] flex mt-2">
            {(() => {
              const today = new Date(currentDate);
              const currentMonth = today.getMonth();
              const currentYear = today.getFullYear();
              
              // Get 6 months: 5 before + current + 1 after
              const visibleMonths = [];
              for (let i = -5; i <= 1; i++) {
                const monthIndex = currentMonth + i;
                const year = currentYear + Math.floor(monthIndex / 12);
                const adjustedMonthIndex = ((monthIndex % 12) + 12) % 12;
                visibleMonths.push({
                  month: monthNames[adjustedMonthIndex],
                  year: year
                });
              }
              
              return visibleMonths.map((monthData, index) => (
                <div key={index} className="text-xs text-gray-500" style={{ width: `${100 / 6}%` }}>
                  {monthData.month.substring(0, 3)}
                </div>
              ));
            })()}
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
                className={`text-gray-800 text-sm
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
                <X size={20} />
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
                <span className={`px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700`}>
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

export default YearCalendarWidget; 