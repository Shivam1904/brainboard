import { useState, useEffect, useRef } from 'react';
import BaseWidget from './BaseWidget';
import { Bell, Plus, X, Clock, RotateCcw, Check, AlertTriangle } from 'lucide-react';
import { AlarmDetailsAndActivityResponse, AlarmDetails, AlarmActivity } from '../../types';
import { getDummyAlarmDetailsAndActivity } from '../../data/widgetDummyData';
import { apiService } from '../../services/api';

interface AlarmWidgetProps {
  onRemove: () => void;
  widget: {
    widget_ids: string[];
    daily_widget_id: string;
    widget_type: string;
    priority: string;
    reasoning: string;
    date: string;
    created_at: string;
  };
}

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

const isAlarmTriggered = (alarmTime: string) => {
  const now = new Date();
  const triggerTime = new Date(alarmTime);
  const diff = Math.abs(triggerTime.getTime() - now.getTime());
  
  // Consider alarm triggered if within 1 minute of trigger time
  return diff <= 60 * 1000;
};

const AlarmWidget = ({ onRemove, widget }: AlarmWidgetProps) => {
  const [alarmData, setAlarmData] = useState<AlarmDetailsAndActivityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [triggeredAlarms, setTriggeredAlarms] = useState<Set<string>>(new Set());
  const [isAlerting, setIsAlerting] = useState(false);
  const [isUsingDummyData, setIsUsingDummyData] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    alarm_times: ['09:00'],
    target_value: '',
    is_snoozable: true
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAlarms = async () => {
    try {
      setLoading(true);
      setError(null);
      setIsUsingDummyData(false);
      
      // Get the widget_id from the widget_ids array (first one for alarm widgets)
      const widgetId = widget.widget_ids[0];
      
      // Call the real API
      const response = await apiService.getAlarmDetailsAndActivity(widgetId);
      setAlarmData(response);
    } catch (err) {
      console.error('Failed to fetch alarms:', err);
      setError('Failed to load alarms');
      setIsUsingDummyData(true);
      // Fallback to dummy data
      const dummyData = getDummyAlarmDetailsAndActivity(widget.daily_widget_id);
      setAlarmData(dummyData);
    } finally {
      setLoading(false);
    }
  };

  const createAlarm = async () => {
    if (!alarmData || !formData.title.trim()) return;
    
    try {
      // For now, we'll just refresh the alarms since creating new alarms
      // would require additional API endpoints that aren't implemented yet
      await fetchAlarms();
      setShowAddForm(false);
      setFormData({
        title: '',
        description: '',
        alarm_times: ['09:00'],
        target_value: '',
        is_snoozable: true
      });
    } catch (err) {
      console.error('Error creating alarm:', err);
    }
  };

  const updateAlarmStatus = async (alarmId: string, action: 'snooze' | 'dismiss') => {
    if (!alarmData) return;
    
    try {
      // Update alarm activity using the real API
      const updateData: {
        updated_by: string;
        snoozed_at?: string;
        started_at?: string;
      } = {
        updated_by: 'user'
      };
      
      if (action === 'snooze') {
        updateData.snoozed_at = new Date().toISOString();
      } else if (action === 'dismiss') {
        updateData.started_at = new Date().toISOString();
      }
      
      await apiService.updateAlarmActivity(alarmData.activity.id, updateData);
      
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
      // Still remove from triggered alarms even if API fails
      setTriggeredAlarms(prev => {
        const newSet = new Set(prev);
        newSet.delete(alarmId);
        return newSet;
      });
    }
  };

  // Check for triggered alarms every 30 seconds
  useEffect(() => {
    const checkAlarms = () => {
      if (!alarmData) return;
      
      const newTriggeredAlarms = new Set<string>();
      let hasTriggered = false;
      
      // Check if any alarm times are triggered
      alarmData.alarm_details.alarm_times.forEach((alarmTime, index) => {
        if (isAlarmTriggered(alarmTime)) {
          newTriggeredAlarms.add(`alarm-${index}`);
          hasTriggered = true;
        }
      });
      
      setTriggeredAlarms(newTriggeredAlarms);
      
      if (hasTriggered && !isAlerting) {
        setIsAlerting(true);
        // Play alert sound or show notification
        console.log('Alarm triggered!');
      } else if (!hasTriggered && isAlerting) {
        setIsAlerting(false);
      }
    };

    checkAlarms();
    intervalRef.current = setInterval(checkAlarms, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [alarmData]);

  useEffect(() => {
    fetchAlarms();
  }, [widget.daily_widget_id]);

  if (loading) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading alarms...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error && !alarmData) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-destructive mb-2">{error}</p>
            <button
              onClick={fetchAlarms}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (!alarmData) {
    return (
      <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-muted-foreground">No alarm data available</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title="Alarms" icon="⏰" onRemove={onRemove}>
      <div className="h-full flex flex-col">
        {/* Alert Banner */}
        {isAlerting && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <span className="font-medium text-red-800">Alarm Triggered!</span>
            </div>
            <p className="text-sm text-red-700 mt-1">
              {Array.from(triggeredAlarms).map(id => {
                const alarmIndex = parseInt(id.split('-')[1]);
                return alarmData.alarm_details.alarm_times[alarmIndex];
              }).join(', ')}
            </p>
          </div>
        )}
        
        {/* Dummy Data Indicator */}
        {isUsingDummyData && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-700 text-center">
              ⏰ Showing sample data - API not connected
            </p>
          </div>
        )}
        
        {/* Next Alarm Display */}
        {alarmData.alarm_details.alarm_times.length > 0 && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Next Alarm</span>
            </div>
            <div className="text-lg font-bold text-blue-900">
              {alarmData.alarm_details.title}
            </div>
          </div>
        )}

        {/* Alarms List */}
        <div className="space-y-3">
          {alarmData.alarm_details.alarm_times.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No alarms set</p>
              <p className="text-sm">Add an alarm to get started!</p>
            </div>
          ) : (
            alarmData.alarm_details.alarm_times.map((alarmTime, index) => {
              const alarmId = `alarm-${index}`;
              const isTriggered = triggeredAlarms.has(alarmId);
              
              return (
                <div
                  key={alarmId}
                  className={`p-3 border rounded-lg transition-colors ${
                    isTriggered 
                      ? 'bg-red-50 border-red-200' 
                      : 'bg-card/50 border-border hover:bg-card/70'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <Bell className={`h-4 w-4 ${
                          isTriggered ? 'text-red-600' : 'text-muted-foreground'
                        }`} />
                        <span className={`font-medium ${
                          isTriggered ? 'text-red-800' : 'text-foreground'
                        }`}>
                          {alarmTime}
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {alarmData.alarm_details.title}
                      </span>
                    </div>
                    
                    {isTriggered && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => updateAlarmStatus(alarmId, 'snooze')}
                          className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                          title="Snooze"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => updateAlarmStatus(alarmId, 'dismiss')}
                          className="p-1 text-green-600 hover:bg-green-100 rounded"
                          title="Dismiss"
                        >
                          <Check className="h-4 w-4" />
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
    </BaseWidget>
  );
};

export default AlarmWidget; 