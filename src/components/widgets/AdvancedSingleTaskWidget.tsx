import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import BaseWidget from './BaseWidget';
import {
  Target,
  Plus,
  X,
  Save,
  Clock,
  RotateCcw,
  Check
} from 'lucide-react';
import { DailyWidget } from '../../services/api';
import { useTodayWidgetsData } from '../../hooks/useDashboardData';
import { useDashboardActions } from '../../stores/dashboardStore';
import { categoryColors } from './CalendarWidget';

interface AdvancedSingleTaskWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  onHeightChange: (dailyWidgetId: string, height: number) => void;
  targetDate: string;
}

const snoozeTime = 10;

// Removed: exact trigger helper is no longer needed due to window-based alerting

const getValueTypeInput = (valueType: string) => {
  switch (valueType) {
    case 'number':
    case 'decimal':
      return 'number';
    case 'text':
      return 'text';
    default:
      return 'text';
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return 'text-green-600 bg-green-50';
    case 'in_progress': return 'text-blue-600 bg-blue-50';
    case 'pending': return 'text-yellow-600 bg-yellow-50';
    case 'cancelled': return 'text-red-600 bg-red-50';
    default: return 'text-gray-600 bg-gray-50';
  }
};

const AdvancedSingleTaskWidget = ({ onRemove, widget, onHeightChange, targetDate }: AdvancedSingleTaskWidgetProps) => {
  const { todayWidgets, isLoading, error } = useTodayWidgetsData(targetDate);
  const { updateWidgetActivity } = useDashboardActions();

  const [updating, setUpdating] = useState(false);

  // Use the passed widget prop directly - it already contains the widget data
  // const widgetData = todayWidgets.find(w => w.id === widget.daily_widget_id);
  const widgetData = widget; // Use the passed widget directly

  // Alarm states
  const [isAlerting, setIsAlerting] = useState(false);
  const [snoozeTimeLeft, setSnoozeTimeLeft] = useState<number | null>(null);

  // Tracker states
  const [showAddForm, setShowAddForm] = useState(false);
  const [newValue, setNewValue] = useState('');
  const [notes, setNotes] = useState('');

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    var height = 2;
    if (widgetData?.activity_data?.activity_history) {
      height += (widgetData.activity_data.activity_history.length * 0.75) + 1;
    }
    if (widgetData?.description) {
      height += 1;
    }
    if (widgetData?.widget_config?.target_value) {
      height += 1;
    }
    if (isAlerting || (snoozeTimeLeft !== null && snoozeTimeLeft > 0)) {
      height += 1;
    }
    onHeightChange(widget.daily_widget_id, height);
  }, [widgetData, isAlerting, snoozeTimeLeft]);

  // Helper function to update activity data locally
  const updateActivityData = (updates: Record<string, any>) => {
    if (!widgetData) return;

    // Since we're using the widget prop directly, we can't update it locally
    // The store will handle updates and refresh the data
  };

  // Alarm functions
  const snoozeAlarm = async () => {

    setUpdating(true);
    const now = new Date();
    const newSnoozeCount = (widgetData?.activity_data?.snooze_count || 0) + 1;

    // Get existing activity history or create new
    const existingActivity = widgetData?.activity_data?.activity_history || [];
    const newActivity = {
      type: 'snooze',
      timestamp: now.toISOString(),
      snooze_count: newSnoozeCount
    };

    // Update locally first for immediate UI feedback
    updateActivityData({
      ...widgetData?.activity_data,
      snooze_count: newSnoozeCount,
      activity_history: [...existingActivity, newActivity]
    });

    setIsAlerting(false);
    setSnoozeTimeLeft(snoozeTime * 60); // snoozeTime minutes in seconds

    // Then update on server
    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        snooze_count: newSnoozeCount,
        activity_history: [...existingActivity, newActivity]
      });
    } catch (err) {
      console.error('Error snoozing alarm:', err);
      // Revert local changes on error
      // await fetchWidgetData(); // This line is removed as per the new_code
    } finally {
      setUpdating(false);
    }
  };

  const stopAlarm = async () => {
    if (!widgetData?.id || updating) return;

    setUpdating(true);
    const now = new Date();
    const startedAt = now.toISOString();

    // Get existing activity history or create new
    const existingActivity = widgetData?.activity_data?.activity_history || [];
    const newActivity = {
      type: 'stop',
      timestamp: now.toISOString(),
      total_snooze_count: widgetData?.activity_data?.snooze_count || 0
    };

    // Update locally first for immediate UI feedback
    updateActivityData({
      ...widgetData?.activity_data,
      started_at: startedAt,
      status: 'completed',
      progress: 100,
      activity_history: [...existingActivity, newActivity]
    });

    setIsAlerting(false);
    setSnoozeTimeLeft(null);

    // Then update on server
    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        started_at: startedAt,
        activity_history: [...existingActivity, newActivity]
      });

      // Also update the task status to completed
      await updateWidgetActivity(widget.daily_widget_id, {
        status: 'completed',
        progress: 100
      });
    } catch (err) {
      console.error('Error stopping alarm:', err);
      // Revert local changes on error
      // await fetchWidgetData(); // This line is removed as per the new_code
    } finally {
      setUpdating(false);
    }
  };

  // Tracker functions
  const updateTrackerValue = async () => {
    if (!newValue.trim() || updating) return;

    setUpdating(true);
    const trackerUpdate = {
      value: newValue,
      time_added: new Date().toISOString(),
      notes: notes || undefined
    };

    // Update locally first for immediate UI feedback
    updateActivityData({
      ...widgetData?.activity_data,
      ...trackerUpdate
    });

    setNewValue('');
    setNotes('');
    setShowAddForm(false);

    // Then update on server
    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        ...trackerUpdate
      });
    } catch (err) {
      console.error('Failed to update tracker value:', err);
      // Revert local changes on error
      // await fetchWidgetData(); // This line is removed as per the new_code
    } finally {
      setUpdating(false);
    }
  };

  // Task status functions
  const updateTaskStatus = async (status: 'pending' | 'in_progress' | 'completed' | 'cancelled') => {
    if (updating) return;

    setUpdating(true);
    const progress = status === 'completed' ? 100 : status === 'in_progress' ? 50 : 0;

    // Update locally first for immediate UI feedback
    updateActivityData({
      ...widgetData?.activity_data,
      status,
      progress
    });

    // Then update on server
    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        status,
        progress
      });
    } catch (err) {
      console.error('Error updating task status:', err);
      // Revert local changes on error
      // await fetchWidgetData(); // This line is removed as per the new_code
    } finally {
      setUpdating(false);
    }
  };

  const getCategoryColor = (category: string) => {
    // Default to gray if category is missing or not found in map
    const defaultColor = 'text-gray-600 bg-gray-50';
    // Check if category exists in map
    if (category && category in categoryColors) {
      return categoryColors[category as keyof typeof categoryColors].color;
    }
    return defaultColor;
  };
  // Check for triggered alarms
  useEffect(() => {
    const checkAlarms = () => {
      if (!widgetData?.widget_config?.alarm_times || widgetData?.date !== new Date().toISOString().split('T')[0]) return;

      const now = new Date();
      let shouldAlert = false;

      // Check if alarm was already started today
      if (widgetData?.activity_data?.started_at) {
        setIsAlerting(false);
        setSnoozeTimeLeft(null);
        return;
      }

      // Check if currently snoozed by calculating from activity history
      const activityHistory = widgetData?.activity_data?.activity_history || [];
      const lastSnoozeActivity = activityHistory
        .filter((activity: any) => activity.type === 'snooze')
        .pop();

      if (lastSnoozeActivity) {
        const lastSnoozeTime = new Date(lastSnoozeActivity.timestamp);
        const snoozeUntil = new Date(lastSnoozeTime.getTime() + snoozeTime * 60 * 1000);
        const snoozeWindowEnd = new Date(snoozeUntil.getTime() + 60 * 60 * 1000);

        if (now < snoozeUntil) {
          // Still snoozed, calculate time left
          const timeLeft = Math.ceil((snoozeUntil.getTime() - now.getTime()) / 1000);
          setSnoozeTimeLeft(timeLeft > 0 ? timeLeft : null);
          setIsAlerting(false);
          return;
        } else if (now >= snoozeUntil && now < snoozeWindowEnd) {
          // Snooze expired, ring within the 1-hour window after snooze
          setSnoozeTimeLeft(null);
          shouldAlert = true;
        }
      }

      // Check if now falls within any alarm's 1-hour alert window
      widgetData.widget_config.alarm_times.forEach((alarmTime: string) => {
        const [hours, minutes] = alarmTime.split(':').map(Number);
        const alarmStart = new Date();
        alarmStart.setHours(hours, minutes, 0, 0);
        const alarmEnd = new Date(alarmStart.getTime() + 60 * 60 * 1000);
        if (now >= alarmStart && now < alarmEnd) {
          shouldAlert = true;
        }
      });



      if (shouldAlert && !isAlerting) {
        setIsAlerting(true);
        setSnoozeTimeLeft(null);

        // Play alert sound
        try {
          const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
          const oscillator = audioContext.createOscillator();
          const gainNode = audioContext.createGain();

          oscillator.connect(gainNode);
          gainNode.connect(audioContext.destination);

          oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
          oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
          oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);

          gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
          console.log('Audio not supported, but alarm is triggered!');
        }
      } else if (!shouldAlert && isAlerting) {
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
  }, [widgetData, isAlerting]);

  // Update countdowns
  useEffect(() => {
    const countdowns: NodeJS.Timeout[] = [];

    if (snoozeTimeLeft !== null && snoozeTimeLeft > 0) {
      const snoozeCountdown = setInterval(() => {
        setSnoozeTimeLeft(prev => {
          if (prev === null || prev <= 1) {
            return null;
          }
          return prev - 1;
        });
      }, 1000);
      countdowns.push(snoozeCountdown);
    }

    return () => {
      countdowns.forEach(clearInterval);
    };
  }, [snoozeTimeLeft]);

  useEffect(() => {
    // This useEffect is no longer needed as data fetching is handled by useTodayWidgetsData
    // fetchWidgetData(); 
  }, [widget.daily_widget_id]);

  if (isLoading) {
    return (
      <BaseWidget title="Advanced Task" icon="🎯" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading advanced task...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error && !widgetData) {
    return (
      <BaseWidget title="Advanced Task" icon="🎯" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-destructive mb-2">{error}</p>
            <button
              onClick={() => {
                // Re-fetch data if there's an error
                // This might need to be handled by the parent component or a global state
                // For now, we'll just show the error message
              }}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (!widgetData) {
    return (
      <BaseWidget title="Advanced Task" icon="🎯" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-muted-foreground">No widget data available</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  const activityData = widgetData.activity_data || {};
  const widgetConfig = widgetData.widget_config || {};

  // Extract data for different features
  const trackerActivity = activityData || {};
  const todoActivity = activityData || {};
  const isCompleted = widgetData.activity_data?.status === 'completed';

  const formatSnoozeTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getNextAlarmTime = (alarm_times: string[]): string => {
    const now = new Date();
    const nextAlarmTime = alarm_times?.find(time => {
      const [hours, minutes] = time.split(':').map(Number);
      const alarmDate = new Date();
      alarmDate.setHours(hours, minutes, 0, 0);
      return alarmDate > now;
    });
    return nextAlarmTime || '';
  };

  return (
    <BaseWidget
      title={isAlerting ? `🚨 Time for ${widgetData.title}! 🚨` : widgetData.title}
      icon={isAlerting ? "" : widgetData.activity_data?.status === 'completed' ? "✅" : "◻️"}
      onRemove={onRemove}
    >
      <div
        className={`flex flex-1 h-full p-2 flex-col overflow-y-auto rounded-lg transition-all ${isAlerting
          ? 'bg-gradient-to-r from-red-500 to-orange-500 border-2 border-red-400 text-white animate-pulse'
          : `bg-${getCategoryColor(widgetData.category)}-100 border border-${getCategoryColor(widgetData.category)}-200 rounded-lg`
          }`}
      >
        {/* Error Indicator */}
        {error && (
          <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-xs text-orange-700 text-center">{error}</p>
          </div>
        )}

        <div
          className={`flex flex-row items-start gap-3 transition-all `}
        >
          <button
            onClick={() => updateTaskStatus(widgetData.activity_data?.status === 'completed' ? 'pending' : 'completed')}
            className="mt-0.5 flex-shrink-0"
          >
            {widgetData.activity_data?.status === 'completed' ? (
              '✅'
            ) : (
              '◻️'
            )}
          </button>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h4 className={`font-medium text-sm ${widgetData.activity_data?.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
                }`}>
                {widgetData.title}
              </h4>
              {widgetData.category && (
                <span className={`px-2 py-1 rounded-full text-xs font-medium text-${getCategoryColor(widgetData.category)}-800  `}>
                  {widgetData.category}
                </span>
              )}
            </div>

            <div className="flex flex-col">

              {widgetData.description && (
                <p className={`text-xs mt-1 ${widgetData.activity_data?.status === 'completed' ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                  {widgetData.description}
                </p>
              )}
              {widgetConfig.value_type && widgetConfig.target_value && (
                <div className={`  rounded-xl text-center flex flex-row items-center justify-end gap-2`}>
                  <div className={`text-lg font-extrabold ${isAlerting ? 'text-white' : 'text-green-900'}`}>
                    {trackerActivity.value || '0'}
                    {widgetConfig.value_unit && (
                      <span className={`ml-1 text-base ${isAlerting ? 'text-white/80' : 'text-green-600'}`}>{widgetConfig.value_unit}</span>
                    )}
                  </div>
                  {!isCompleted && (<div className="">
                    <button
                      onClick={() => setShowAddForm(true)}
                      disabled={updating || isCompleted}
                      className={`inline-flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium ${updating || isCompleted
                        ? `${isAlerting ? 'bg-white/30 text-white/70' : 'bg-green-300 text-white'} cursor-not-allowed`
                        : `${isAlerting ? 'bg-white text-red-600 hover:bg-white/90' : 'bg-green-600 text-white hover:bg-green-700'}`
                        }`}
                    >
                      <Plus className="h-4 w-4" />
                      Add
                    </button>
                  </div>)}
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Snooze countdown */}
        {snoozeTimeLeft !== null && snoozeTimeLeft > 0 && (
          <div className={`mt-3 px-3 py-1 mb-1 rounded ${isAlerting ? 'bg-white/10 text-white' : 'bg-yellow-100 text-yellow-800 border border-yellow-300'}`}>
            <span className="text-xs">⏰ Snoozed for {formatSnoozeTime(snoozeTimeLeft)}</span>
          </div>
        )}
        {false && todoActivity.progress !== undefined && (
          <div className="px-2 ">
            <div className="w-full bg-blue-200 rounded-full h-1">
              <div
                className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                style={{ width: `${todoActivity.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Top bar: Next alarm + completed badge */}
        <div className="flex items-center justify-between gap-2">

          {widgetConfig.include_tracker_details && (<div className={`text-xs ${isAlerting ? 'text-white/80' : 'text-green-700'} 
                           flex items-center justify-center gap-2`}>
            <Target className="h-4 w-4" /> {widgetConfig.target_value}
            {widgetConfig.value_unit}
          </div>)}
          {widgetConfig.include_alarm_details && (
            <div className="flex items-center gap-2">
              <Clock className={`h-4 w-4 ${isAlerting ? 'text-white' : 'text-yellow-600'}`} />
              <span className={`text-xs ${isAlerting ? 'text-white' : 'text-yellow-800'}`}>
                <span className="text-xs truncate max-w-[40px]">{getNextAlarmTime(widgetConfig.alarm_times)}</span>
              </span>
              <span className={`text-[10px] truncate max-w-[40px] ${isAlerting ? 'text-white/80' : 'text-yellow-700'}`}>
                {widgetConfig.alarm_times.join(', ')}
              </span>
            </div>
          )}
        </div>
        {/* Actions when ringing */}
        {isAlerting && (
          <div className="flex gap-2 mt-3">
            <button
              onClick={snoozeAlarm}
              disabled={updating}
              className={`flex-1 px-3 py-2 rounded text-sm transition-colors flex items-center justify-center gap-2 ${updating ? 'bg-white/40 text-white cursor-not-allowed' : 'bg-white text-red-600 hover:bg-white/90'
                }`}
            >
              <RotateCcw className={`h-4 w-4 ${updating ? 'animate-spin' : ''}`} />
              Snooze
            </button>
            <button
              onClick={stopAlarm}
              disabled={updating}
              className={`flex-1 px-3 py-2 rounded text-sm transition-colors flex items-center justify-center gap-2 ${updating ? 'bg-white/40 text-white cursor-not-allowed' : 'bg-green-500 text-white hover:bg-green-600'
                }`}
            >
              <Check className="h-4 w-4" />
              Stop
            </button>
          </div>
        )}

        {/* Minimal Activity History */}
        {widgetData?.activity_data?.activity_history &&
          widgetData?.activity_data?.activity_history.length > 0 && (
            <div className={`mt-3 p-2 rounded ${isAlerting ? 'bg-white/10 text-white' : 'bg-gray-50 text-gray-700 border border-gray-200'}`}>
              <div className={`text-xs mb-1 ${isAlerting ? 'text-white/80' : 'text-gray-600'}`}>Recent activity</div>
              <div className="space-y-1">
                {widgetData?.activity_data?.activity_history.map((activity: any, index: number) => (
                  <div key={index} className="text-xs flex justify-between opacity-90">
                    <span>{activity.type === 'snooze' ? '⏰ Snoozed' : '🛑 Stopped'}</span>
                    <span>
                      {new Date(activity.timestamp).toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true,
                      })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}


        {/* Add Value Modal */}
        {showAddForm && createPortal(
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
              {/* Header */}
              <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-4 rounded-t-xl">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-bold">Add New Value</h3>
                    <p className="text-green-100 text-sm">Track your progress</p>
                  </div>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="text-white hover:text-green-100 p-1 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Form Content */}
              <div className="p-4">
                <div className="space-y-3">
                  {/* Value Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Value {widgetConfig.value_unit && `(${widgetConfig.value_unit})`}
                    </label>
                    <input
                      type={getValueTypeInput(widgetConfig.value_type)}
                      value={newValue}
                      onChange={(e) => setNewValue(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder={`Enter value`}
                      required
                    />
                  </div>

                  {/* Notes Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notes (Optional)
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Add any notes about this entry..."
                      rows={2}
                    />
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="bg-gray-50 p-4 rounded-b-xl">
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 px-3 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={updateTrackerValue}
                    disabled={!newValue.trim() || updating}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center ${updating || !newValue.trim() ? 'bg-gray-400 text-white cursor-not-allowed' : 'bg-gradient-to-r from-green-600 to-blue-600 text-white hover:from-green-700 hover:to-blue-700'}`}
                  >
                    {updating ? (
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                    ) : (
                      <Save className="h-3 w-3 mr-1" />
                    )}
                    {updating ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            </div>
          </div>,
          document.body
        )}
      </div>
    </BaseWidget>
  );
};

export default AdvancedSingleTaskWidget; 