import { useState, useEffect, useRef } from 'react';
import BaseWidget from './BaseWidget';
import { Bell, Plus, X, Clock, RotateCcw, Check, AlertTriangle } from 'lucide-react';
import { buildApiUrl, apiCall, API_CONFIG } from '../../config/api';
import { AlarmWidgetDataResponse, Alarm } from '../../types/widgets';
import { Widget } from '../../utils/dashboardUtils';

interface AlarmWidgetProps {
  onRemove: () => void;
  widget: Widget;
}

const getDummyAlarms = (widgetId: string): AlarmWidgetDataResponse => ({
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

const formatTime = (timeString: string) => {
  const time = new Date(timeString);
  return time.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  });
};

const getTimeUntil = (targetTime: string) => {
  const now = new Date();
  const target = new Date(targetTime);
  const diff = target.getTime() - now.getTime();
  
  if (diff <= 0) return 'Now!';
  
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

const isAlarmTriggered = (alarm: Alarm) => {
  if (!alarm.next_trigger_time || alarm.is_snoozed) return false;
  
  const now = new Date();
  const triggerTime = new Date(alarm.next_trigger_time);
  const diff = Math.abs(triggerTime.getTime() - now.getTime());
  
  // Consider alarm triggered if within 1 minute of trigger time
  return diff <= 60 * 1000;
};

const AlarmWidget = ({ onRemove, widget }: AlarmWidgetProps) => {
  const [widgetData, setWidgetData] = useState<AlarmWidgetDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [triggeredAlarms, setTriggeredAlarms] = useState<Set<string>>(new Set());
  const [isAlerting, setIsAlerting] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    alarm_type: 'daily',
    alarm_times: ['09:00'],
    frequency_value: undefined as number | undefined,
    specific_date: undefined as string | undefined
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAlarms = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const widgetId = widget.daily_widget_id;
      
      const response = await apiCall<AlarmWidgetDataResponse>(
        buildApiUrl(API_CONFIG.alarm.getWidgetData.replace('{widget_id}', widgetId))
      );
      
      setWidgetData(response);
    } catch (err) {
      console.error('Error fetching alarms:', err);
      // Fallback to dummy data on error
      const widgetId = widget.daily_widget_id;
      const dummyAlarms = getDummyAlarms(widgetId);
      setWidgetData(dummyAlarms);
      setError('Using offline data - API unavailable');
    } finally {
      setLoading(false);
    }
  };

  const createAlarm = async () => {
    if (!widgetData || !formData.title.trim()) return;
    
    try {
      const response = await apiCall<Alarm>(
        buildApiUrl(API_CONFIG.alarm.createAlarm),
        {
          method: 'POST',
          body: JSON.stringify({
            dashboard_widget_id: widgetData.widget_id,
            title: formData.title,
            alarm_type: formData.alarm_type,
            alarm_times: formData.alarm_times,
            frequency_value: formData.frequency_value,
            specific_date: formData.specific_date
          })
        }
      );
      
      // Refresh alarms
      await fetchAlarms();
      setShowAddForm(false);
      setFormData({
        title: '',
        alarm_type: 'daily',
        alarm_times: ['09:00'],
        frequency_value: undefined,
        specific_date: undefined
      });
    } catch (err) {
      console.error('Error creating alarm:', err);
    }
  };

  const updateAlarmStatus = async (alarmId: string, action: 'snooze' | 'dismiss') => {
    if (!widgetData) return;
    
    try {
      await apiCall(
        buildApiUrl(API_CONFIG.alarm.updateAlarmStatus.replace('{alarm_id}', alarmId)),
        {
          method: 'POST',
          body: JSON.stringify({
            action: action,
            snooze_minutes: action === 'snooze' ? 5 : undefined
          })
        }
      );
      
      // Remove from triggered alarms
      setTriggeredAlarms(prev => {
        const newSet = new Set(prev);
        newSet.delete(alarmId);
        return newSet;
      });
      
      // Refresh alarms
      await fetchAlarms();
    } catch (err) {
      console.error('Error updating alarm status:', err);
    }
  };

  // Check for triggered alarms every 30 seconds
  useEffect(() => {
    const checkAlarms = () => {
      if (!widgetData) return;
      
      const newTriggeredAlarms = new Set<string>();
      let hasTriggered = false;
      
      widgetData.alarms.forEach(alarm => {
        if (isAlarmTriggered(alarm)) {
          newTriggeredAlarms.add(alarm.id);
          hasTriggered = true;
        }
      });
      
      setTriggeredAlarms(newTriggeredAlarms);
      setIsAlerting(hasTriggered);
    };

    // Check immediately
    checkAlarms();
    
    // Set up interval
    intervalRef.current = setInterval(checkAlarms, 30000);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [widgetData]);

  useEffect(() => {
    fetchAlarms();
  }, []);

  if (loading) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error && !widgetData) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-orange-600 mb-2">{error}</p>
          <button 
            onClick={fetchAlarms}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  if (!widgetData) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32 text-center">
          <p className="text-gray-500">No alarms found for this widget</p>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget 
      title="Alarms" 
      icon="⏰" 
      onRemove={onRemove}
      className={`${isAlerting ? 'animate-pulse bg-red-50 border-red-300 shadow-lg' : ''}`}
    >
      <div className="p-4 h-full overflow-y-auto">
        {/* Alert Banner */}
        {isAlerting && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg animate-pulse">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle size={16} className="animate-bounce" />
              <span className="font-medium">Alarm Triggered!</span>
            </div>
            <p className="text-sm text-red-700 mt-1">
              {Array.from(triggeredAlarms).map(id => {
                const alarm = widgetData.alarms.find(a => a.id === id);
                return alarm?.title;
              }).join(', ')}
            </p>
          </div>
        )}

        {/* Offline Indicator */}
        {error && (
          <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-xs text-orange-700 text-center">{error}</p>
          </div>
        )}
        
        {/* Next Alarm Display */}
        {widgetData.stats.next_alarm_time && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Clock size={16} className="text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Next Alarm</span>
            </div>
            <div className="text-lg font-bold text-blue-900">
              {widgetData.stats.next_alarm_title}
            </div>
            <div className="text-sm text-blue-700">
              {formatTime(widgetData.stats.next_alarm_time)} 
              {widgetData.stats.next_alarm_time && (
                <span className="ml-2 text-xs">
                  ({getTimeUntil(widgetData.stats.next_alarm_time)})
                </span>
              )}
            </div>
          </div>
        )}

        {/* Add Alarm Button */}
        <div className="mb-4">
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={16} />
            Add Alarm
          </button>
        </div>

        {/* Alarms List */}
        <div className="space-y-3">
          {widgetData.alarms.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No alarms set</p>
              <p className="text-sm">Add an alarm to get started!</p>
            </div>
          ) : (
            widgetData.alarms.map(alarm => {
              const isTriggered = triggeredAlarms.has(alarm.id);
              
              return (
                <div 
                  key={alarm.id} 
                  className={`p-3 rounded-lg border transition-all ${
                    isTriggered 
                      ? 'bg-red-50 border-red-300 animate-pulse' 
                      : alarm.is_active 
                        ? 'bg-white border-gray-200 hover:border-blue-300' 
                        : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Bell 
                          size={16} 
                          className={isTriggered ? 'text-red-600 animate-bounce' : 'text-gray-600'} 
                        />
                        <h4 className={`font-medium text-sm ${
                          isTriggered ? 'text-red-800' : 'text-gray-900'
                        }`}>
                          {alarm.title}
                        </h4>
                        {!alarm.is_active && (
                          <span className="px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                            Inactive
                          </span>
                        )}
                        {alarm.is_snoozed && (
                          <span className="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-700">
                            Snoozed
                          </span>
                        )}
                      </div>
                      
                      <div className="text-xs text-gray-600 mb-2">
                        {alarm.alarm_times.join(', ')} • {alarm.alarm_type}
                      </div>
                      
                      {alarm.next_trigger_time && (
                        <div className="text-xs text-gray-500">
                          Next: {formatTime(alarm.next_trigger_time)}
                          <span className="ml-2">
                            ({getTimeUntil(alarm.next_trigger_time)})
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {isTriggered && (
                      <div className="flex gap-1">
                                                 <button
                           onClick={() => updateAlarmStatus(alarm.id, 'snooze')}
                           className="p-1 text-yellow-600 hover:bg-yellow-100 rounded"
                           title="Snooze 5 minutes"
                         >
                           <RotateCcw size={14} />
                         </button>
                        <button
                          onClick={() => updateAlarmStatus(alarm.id, 'dismiss')}
                          className="p-1 text-green-600 hover:bg-green-100 rounded"
                          title="Dismiss"
                        >
                          <Check size={14} />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Add Alarm Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-xl">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-bold">Add New Alarm</h3>
                  <p className="text-blue-100 mt-1">Set up your reminder</p>
                </div>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-white hover:text-blue-100 p-2 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
            
            {/* Form Content */}
            <div className="p-6">
              <div className="space-y-4">
                {/* Title Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alarm Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Morning Standup"
                    required
                  />
                </div>
                
                {/* Time Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time
                  </label>
                  <input
                    type="time"
                    value={formData.alarm_times[0]}
                    onChange={(e) => setFormData({...formData, alarm_times: [e.target.value]})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                
                {/* Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frequency
                  </label>
                  <select
                    value={formData.alarm_type}
                    onChange={(e) => setFormData({...formData, alarm_type: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="once">Once</option>
                  </select>
                </div>
              </div>
            </div>
            
            {/* Footer */}
            <div className="bg-gray-50 p-6 rounded-b-xl">
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 hover:border-gray-400 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={createAlarm}
                  disabled={!formData.title.trim()}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Create Alarm
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </BaseWidget>
  );
};

export default AlarmWidget; 