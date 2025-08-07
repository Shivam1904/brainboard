import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight, Calendar, Clock, MapPin } from 'lucide-react';
import { getDummyCalendarData } from '../../data/widgetDummyData';
import { DailyWidget } from '../../services/api';

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
  todosCompleted: number;
  todosTotal: number;
  habitStreak: number;
  milestones: number;
}

interface CalendarData {
  year: number;
  month: number;
  days: CalendarDay[];
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

const getEventTypeColor = (type: string) => {
  switch (type) {
    case 'event': return 'bg-blue-100 text-blue-800';
    case 'milestone': return 'bg-purple-100 text-purple-800';
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
      
      // TODO: Replace with real API call
      // const response = await apiService.getCalendarData(widget.daily_widget_id, { year, month });
      // setCalendarData(response);
      
      // Using dummy data for now
      const dummyData = getDummyCalendarData(year, month);
      setIsUsingDummyData(true);
      setCalendarData(dummyData);
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
    <BaseWidget title="Calendar" icon="📅" onRemove={onRemove}>
      <div className="px-4">
        {/* Calendar Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
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

        {/* Monthly Stats */}
        {calendarData.monthlyStats && (
          <div className="mt-3 p-3 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-800 mb-2">Monthly Overview</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-green-600">📋</span>
                <div>
                  <div className="font-medium">{calendarData.monthlyStats.averageCompletionRate}%</div>
                  <div className="text-gray-500">Completion Rate</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-orange-600">🔥</span>
                <div>
                  <div className="font-medium">{calendarData.monthlyStats.longestHabitStreak}d</div>
                  <div className="text-gray-500">Best Streak</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-purple-600">🏆</span>
                <div>
                  <div className="font-medium">{calendarData.monthlyStats.totalMilestones}</div>
                  <div className="text-gray-500">Milestones</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-blue-600">📊</span>
                <div>
                  <div className="font-medium">{calendarData.monthlyStats.totalTodosCompleted}</div>
                  <div className="text-gray-500">Todos Done</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Day Headers */}
        <div className="grid grid-cols-7 mb-1">
          {dayNames.map(day => (
            <div key={day} className="text-center text-xs font-medium text-gray-600 py-1">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 ">
          {calendarData.days.map((day, index) => (
            <div
              key={index}
              className={`min-h-[80px] p-1 border border-gray-200 text-xs ${
                !day.isCurrentMonth ? 'bg-gray-50 text-gray-400' : 'bg-white'
              } ${day.isToday ? 'bg-blue-50 border-blue-300' : ''}`}
            >
              <div className={`text-right mb-1 ${
                day.isToday ? 'font-bold text-blue-600' : 'text-gray-700'
              }`}>
                {day.day}
              </div>
              
              {/* Todos Progress */}
              {day.isCurrentMonth && day.todosTotal > 0 && (
                <div className="mb-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-500">📋</span>
                    <span className="text-xs text-gray-600">{day.todosCompleted}/{day.todosTotal}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-green-500 h-1 rounded-full"
                      style={{ width: `${(day.todosCompleted / day.todosTotal) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {/* Habit Streak */}
              {day.isCurrentMonth && day.habitStreak > 0 && (
                <div className="mb-1">
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-orange-500">🔥</span>
                    <span className="text-xs text-gray-600">{day.habitStreak}d</span>
                  </div>
                </div>
              )}
              
              {/* Milestones */}
              {day.isCurrentMonth && day.milestones > 0 && (
                <div className="mb-1">
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-purple-500">🏆</span>
                    <span className="text-xs text-gray-600">{day.milestones}</span>
                  </div>
                </div>
              )}
              
              {/* Events */}
              <div className="space-y-1">
                {day.events.slice(0, 1).map(event => (
                  <div
                    key={event.id}
                    onClick={() => setSelectedEvent(event)}
                    className={`cursor-pointer p-1 rounded text-xs truncate border-l-2 ${getEventTypeColor(event.type)} ${getPriorityColor(event.priority)}`}
                    title={event.title}
                  >
                    {event.title}
                  </div>
                ))}
                {day.events.length > 1 && (
                  <div className="text-xs text-gray-500 text-center">
                    +{day.events.length - 1} more
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Upcoming Events & Milestones */}
        <div className="mt-4 space-y-4">
          {/* Upcoming Events */}
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-2">Upcoming Events</h4>
            <div className="space-y-2 max-h-24 overflow-y-auto">
              {calendarData.events
                .filter(event => new Date(event.date) >= new Date())
                .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                .slice(0, 2)
                .map(event => (
                  <div
                    key={event.id}
                    onClick={() => setSelectedEvent(event)}
                    className="flex items-center gap-2 p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                  >
                    <Calendar size={12} className="text-gray-500" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{event.title}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(event.date).toLocaleDateString()}
                        {event.time && ` • ${event.time}`}
                      </div>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${getEventTypeColor(event.type).replace('bg-', '').replace(' text-', '')}`}></div>
                  </div>
                ))}
            </div>
          </div>

          {/* Recent Milestones */}
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-2">Recent Milestones</h4>
            <div className="space-y-2 max-h-24 overflow-y-auto">
              {calendarData.milestones
                .filter(milestone => new Date(milestone.date) <= new Date())
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                .slice(0, 2)
                .map(milestone => (
                  <div
                    key={milestone.id}
                    onClick={() => setSelectedEvent(milestone)}
                    className="flex items-center gap-2 p-2 bg-purple-50 rounded cursor-pointer hover:bg-purple-100"
                  >
                    <div className="text-purple-600">🏆</div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{milestone.title}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(milestone.date).toLocaleDateString()}
                        {milestone.time && ` • ${milestone.time}`}
                      </div>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-purple-500"></div>
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