import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight, Check, Pencil } from 'lucide-react';
import { DailyWidget, apiService, DashboardWidget } from '../../services/api';
import { useUpdateWidgetActivity } from '@/stores/dashboardStore';

export const categoryColors = {
  productivity: { value: 'productivity', label: 'Productivity', color: '#3B82F6' }, // blue
  health: { value: 'health', label: 'Health', color: '#EF4444' }, // red
  job: { value: 'job', label: 'Job', color: '#8B5CF6' }, // purple
  information: { value: 'information', label: 'Information', color: '#EAB308' }, // yellow
  entertainment: { value: 'entertainment', label: 'Entertainment', color: '#EC4899' }, // pink
  utilities: { value: 'utilities', label: 'Utilities', color: '#6B7280' }, // gray
  personal: { value: 'personal', label: 'Personal', color: '#10B981' } // green
};

interface HabitTask {
  id: string;
  title: string;
  category: string;
  widget_id: string;
  date: string;
  activity_data?: Record<string, any>;
}

interface HabitDay {
  date: string;
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  tasks: HabitTask[];
  completedTasks: HabitTask[];
}

interface HabitData {
  year: number;
  month: number;
  days: HabitDay[];
  tasks: HabitTask[];
  monthlyStats?: {
    totalTasksCompleted: number;
    totalTasks: number;
    averageCompletionRate: number;
    longestStreak: number;
  };
}

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

interface HabitTrackerWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
}

// Enhanced color utilities
const getCategoryColor = (category: string): string => {
  return categoryColors[category as keyof typeof categoryColors].color;
};
// Helper function to generate calendar structure
const generateHabitStructure = (year: number, month: number, targetDate: string): HabitData => {
  const firstDay = new Date(year, month - 1, 1);

  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday

  const days: HabitDay[] = [];

  // Generate 42 days (6 weeks) to fill the calendar grid
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);

    const isCurrentMonth = date.getMonth() === month - 1;
    const isToday = date.toISOString().split('T')[0] === targetDate;

    days.push({
      date: date.toISOString().split('T')[0],
      day: date.getDate(),
      isCurrentMonth,
      isToday,
      tasks: [],
      completedTasks: [],
    });
  }

  return {
    year,
    month,
    days,
    tasks: []
  };
};

const WIDTH = 30;

const HabitTrackerWidget = ({ onRemove, widget, targetDate }: HabitTrackerWidgetProps) => {
  const [currentDate, setCurrentDate] = useState(new Date(targetDate));
  const [habitData, setHabitData] = useState<HabitData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableWidgets, setAvailableWidgets] = useState<DashboardWidget[]>([]);
  const [selectedWidgets, setSelectedWidgets] = useState<Set<string>>(new Set());
  const [updatingWidget, setUpdatingWidget] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [editingWidgets, setEditingWidgets] = useState(false);
  const [radius, setRadius] = useState(100);
  const updateWidgetActivity = useUpdateWidgetActivity();
  const fetchHabitData = async (year: number, month: number) => {
    try {
      setLoading(true);
      setError(null);

      // Compute start and end of month
      const startOfMonth = new Date(year, month - 1, 1);
      const endOfMonth = new Date(year, month, 0);

      // Fetch widgets linked to this habit tracker by selected_habit_calendar
      const items = await apiService.getWidgetActivityForCalendar({
        calendar_id: widget.widget_id,
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: endOfMonth.toISOString().split('T')[0],
        calendar_type: 'habitTracker'
      });

      // Generate habit structure
      const base = generateHabitStructure(year, month, targetDate);
      console.log('Generated base structure:', base.days.map(d => ({ date: d.date, day: d.day, isCurrentMonth: d.isCurrentMonth })));

      // Map API items to habit tasks
      const tasks = items.map(item => ({
        id: item.daily_widget_id || item.id,
        title: item.title,
        category: item.category,
        widget_id: item.widget_id,
        date: item.date || new Date().toISOString().split('T')[0],
        activity_data: item.activity_data,
      }));

      // Place tasks into days
      const dayByKey = new Map(base.days.map(d => [d.date, d] as const));
      console.log('Day mapping:', Array.from(dayByKey.keys()));
      console.log('Tasks to place:', tasks);

      for (const task of tasks) {
        // Use the task's date field to determine which day it belongs to
        const key = task.date || new Date().toISOString().split('T')[0];
        console.log(`Placing task "${task.title}" on date ${key}, status: ${task.activity_data?.status}`);

        const day = dayByKey.get(key);
        if (day) {
          day.tasks.push(task);
          if (task.activity_data?.status === 'completed') {
            day.completedTasks.push(task);
            console.log(`Task "${task.title}" marked as completed for day ${day.day}`);
          }
        } else {
          console.log(`No day found for date ${key}`);
        }
      }

      base.tasks = tasks;
      setHabitData(base);
    } catch (err) {
      setError('Failed to load habit data');
      console.error('Error fetching habit data:', err);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    setRadius(((habitData?.tasks?.filter(t => selectedWidgets?.has(t.widget_id))?.length || 0) * WIDTH/2 )+WIDTH/2);
  }, [habitData, selectedWidgets]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
    fetchHabitData(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    fetchHabitData(today.getFullYear(), today.getMonth() + 1);
  };

  // Fetch available widgets for selection
  const fetchAvailableWidgets = async () => {
    try {
      const widgets = await apiService.getAllWidgets();
      // Filter out the current habit tracker widget and only show task-like widgets
      const taskWidgets = widgets.filter(w =>
        w.id !== widget.widget_id &&
        !['allSchedules', 'aiChat', 'simpleClock', 'weatherWidget', 'calendar', 'moodTracker', 'notes', 'habitTracker', 'yearCalendar', 'pillarsGraph'].includes(w.widget_type)
      );
      setAvailableWidgets(taskWidgets);

      // Initialize selected widgets based on current widget_config.selected_habit_calendar
      const currentSelected = new Set<string>();
      for (const w of taskWidgets) {
        if (w.widget_config?.selected_habit_calendar === widget.widget_id) {
          currentSelected.add(w.id);
        }
      }
      setSelectedWidgets(currentSelected);
    } catch (err) {
      console.error('Error fetching available widgets:', err);
      setError('Failed to load available widgets');
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

      // Update the widget's selected_habit_calendar field
      const widgetToUpdate = availableWidgets.find(w => w.id === widgetId);
      if (!widgetToUpdate) {
        throw new Error('Widget not found');
      }

      const updateData = {
        widget_config: {
          ...widgetToUpdate.widget_config,
          selected_habit_calendar: isSelected ? widget.widget_id : null
        }
      };

      await apiService.updateWidget(widgetId, updateData);

      // Show success message
      setSuccessMessage(`Task "${widgetToUpdate.title}" ${isSelected ? 'added to' : 'removed from'} habit tracker`);
      setTimeout(() => setSuccessMessage(null), 3000);

      // Refresh habit data to show the changes
      await fetchHabitData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    } catch (err) {
      console.error('Error updating widget habit selection:', err);
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
    fetchHabitData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    fetchAvailableWidgets();
  }, []);

  if (loading) {
    return (
      <BaseWidget title="Habit Tracker" icon="🔄" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="Habit Tracker" icon="🔄" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-red-600 mb-2">{error}</p>
          <button
            onClick={() => fetchHabitData(currentDate.getFullYear(), currentDate.getMonth() + 1)}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  if (!habitData) {
    return (
      <BaseWidget title="Habit Tracker" icon="🔄" onRemove={onRemove}>
        <div className="text-center py-8 text-gray-500">
          <p>No habit data available</p>
        </div>
      </BaseWidget>
    );
  }

  // Get unique tasks for the legend
  const uniqueTasks = Array.from(new Set(habitData.tasks.map(task => task.title)));

  return (
    <BaseWidget title={widget.title} icon="🔄" onRemove={onRemove}>
      <div className=" flex-col px-4 pt-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronLeft size={16} />
            </button>
            <h3 className="font-semibold text-lg mx-2">
              {monthNames[habitData.month - 1]} {habitData.year}
            </h3>
            <button
              onClick={() => navigateMonth('next')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        {/* Habit Tracker Grid */}
        <div className="flex flex-row">
          {/* SVG Circular Grid */}
          <div className="absolute flex-1 flex">
            <div className={`relative `}>
              <svg width={`${radius  + 120}`} height={`${radius  + 30}`} >

                {/* SVG arcs for each task and day */}
                {uniqueTasks.map((taskTitle, taskIndex) => {
                  const task = habitData.tasks.find(t => t.title === taskTitle);
                  const category = task?.category || 'personal';
                  const color = categoryColors[category as keyof typeof categoryColors]?.color || '#6B7280';
                  const ringRadius = WIDTH + (taskIndex * WIDTH); // Each habit gets its own ring

                  return (
                    <g key={taskIndex}>
                      {/* Arcs for each day */}
                      <text x={radius/2 + 100 -WIDTH/2} y={radius/2 - (WIDTH/2 + (taskIndex * WIDTH))}
                        textAnchor="end"
                        className="text-xs font-semibold fill-gray-600"
                        style={{ fill: color }}
                      >
                        {taskTitle}
                      </text>
                      {habitData.days.filter(day => day.isCurrentMonth).map((day, dayIndex) => {
                        // Calculate angle based on the actual day of the month (1-31)
                        // Map day 1 to 0°, day 2 to ~8.7°, etc. (270 degrees total)
                        const startAngle = ((day.day - 1) * 270) / 31;
                        const endAngle = ((day.day * 270) / 31)-1;

                        // Convert angles to radians and adjust for SVG coordinate system
                        const startRad = (startAngle - 90) * Math.PI / 180;
                        const endRad = (endAngle - 90) * Math.PI / 180;

                        // Calculate start and end points
                        const startX = radius/2 + 100 + Math.cos(startRad) * ringRadius;
                        const startY = radius/2 + 10 + Math.sin(startRad) * ringRadius;
                        const endX = radius/2 + 100 + Math.cos(endRad) * ringRadius;
                        const endY = radius/2 + 10 + Math.sin(endRad) * ringRadius;

                        // Determine if this day/task combination is completed
                        const dayTask = day.tasks.find(t => t.title === taskTitle);
                        let isCompleted = dayTask && day.completedTasks.includes(dayTask);

                        // Create arc path
                        const largeArcFlag = (endAngle - startAngle) > 180 ? 1 : 0;
                        const arcPath = `M ${startX} ${startY} A ${ringRadius} ${ringRadius} 0 ${largeArcFlag} 1 ${endX} ${endY}`;

                        return (
                          <path
                            key={`${taskIndex}-${dayIndex}`}
                            d={arcPath}
                            stroke={isCompleted ? getCategoryColor(dayTask?.category || 'personal') 
                              : dayTask && dayTask.date === currentDate.toISOString().split('T')[0] ? 'rgba(223, 209, 120, 0.39)' 
                              : day.date === currentDate.toISOString().split('T')[0] ? 'rgba(230, 227, 207, 0.39)' 
                              : dayTask ? 'rgba(143, 121, 121, 0.39)' 
                              : 'rgba(255, 255, 255, 0.39)'}
                            strokeWidth={WIDTH-1}
                            fill="none"
                            className={`${dayTask && dayTask.date === currentDate.toISOString().split('T')[0] ? 'cursor-pointer' : 'cursor-default'} hover:stroke-width-10 transition-all duration-200`}
                            onClick={async () => {
                              // Handle arc click - toggle completion
                              console.log(`Toggle ${taskTitle} for day ${day.day}, ${dayTask?.id}`);
                              if(dayTask?.id && dayTask.date === currentDate.toISOString().split('T')[0]) {
                                try {
                                  // Update the API
                                  await updateWidgetActivity(dayTask.id, { status: isCompleted ? 'not_completed' : 'completed' });
                                  
                                  // Update local state immediately for responsive UI
                                  setHabitData(prevData => {
                                    if (!prevData) return prevData;
                                    
                                    const newData = { ...prevData };
                                    const dayIndex = newData.days.findIndex(d => d.date === day.date);
                                    
                                    if (dayIndex !== -1) {
                                      const updatedDay = { ...newData.days[dayIndex] };
                                      const taskIndex = updatedDay.tasks.findIndex(t => t.id === dayTask.id);
                                      
                                      if (taskIndex !== -1) {
                                        // Update the task's activity_data
                                        const updatedTask = { ...updatedDay.tasks[taskIndex] };
                                        updatedTask.activity_data = {
                                          ...updatedTask.activity_data,
                                          status: isCompleted ? 'not_completed' : 'completed'
                                        };
                                        updatedDay.tasks[taskIndex] = updatedTask;
                                        
                                        // Update completedTasks array
                                        if (isCompleted) {
                                          // Remove from completedTasks
                                          updatedDay.completedTasks = updatedDay.completedTasks.filter(t => t.id !== dayTask.id);
                                        } else {
                                          // Add to completedTasks
                                          updatedDay.completedTasks.push(updatedTask);
                                        }
                                        
                                        newData.days[dayIndex] = updatedDay;
                                      }
                                    }
                                    
                                    return newData;
                                  });
                                } catch (error) {
                                  console.error('Failed to update activity:', error);
                                  // Optionally show an error message to the user
                                }
                              }
                            }}
                          />
                        );
                      })}
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        </div>

        {/* Task List Section */}
        {(<div className="absolute left-0 bottom-0 flex flex-col mt-4">
          {editingWidgets && (
            <div className="px-2">
              {availableWidgets.map((event, index) => (
                <span key={event.id}
                  onClick={() => handleWidgetSelection(event.id, !selectedWidgets.has(event.id))}
                  className={`text-gray-800 text-sm cursor-pointer
                        ${selectedWidgets.has(event.id)
                      ? 'font-bold'
                      : ''
                    }`}
                  style={{ color: categoryColors[event.category as keyof typeof categoryColors]?.color || '#6B7280' }}>
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
                  className={`text-gray-500 text-sm cursor-pointer
                        ${selectedWidgets.has(event.id)
                      ? 'font-bold'
                      : ''
                    }`}
                  style={{ color: categoryColors[event.category as keyof typeof categoryColors]?.color || '#6B7280' }}>
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
        </div>)}

      </div>
    </BaseWidget>
  );
};

export default HabitTrackerWidget; 