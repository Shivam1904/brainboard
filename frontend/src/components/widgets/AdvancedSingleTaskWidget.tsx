import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import BaseWidget from './BaseWidget';
import {
  Target,
  Clock,
  RotateCcw,
  Check,
  AlertTriangle,
  X,
  Plus
} from 'lucide-react';
import { DailyWidget } from '../../services/api';
import { useDashboardActions } from '../../stores/dashboardStore';
import { categoryColors } from '../../constants/widgetConstants';
import { formatTime, getTodayDateString } from '../../utils/dateUtils';

import { checkAlarmTrigger, getAlarmStatus, AlarmActivity } from '../../utils/alarmUtils';

interface AdvancedSingleTaskWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  onHeightChange: (dailyWidgetId: string, height: number) => void;
}

const snoozeTime = 10;

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

const getCategoryColor = (category: string) => {
  const defaultColor = 'text-gray-600 bg-gray-50';
  if (category && category in categoryColors) {
    return categoryColors[category as keyof typeof categoryColors].color;
  }
  return defaultColor;
};





const AdvancedSingleTaskWidget = ({ onRemove, widget, onHeightChange }: AdvancedSingleTaskWidgetProps) => {
  const { updateWidgetActivity } = useDashboardActions();

  const [updating, setUpdating] = useState(false);

  // States
  const [isAlerting, setIsAlerting] = useState(false);
  const [snoozeTimeLeft, setSnoozeTimeLeft] = useState<number | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());



  // Helper imports
  // Note: Imported functions are used below. Ensure they are imported at the top of the file

  // Tracker states
  const [showAddForm, setShowAddForm] = useState(false);
  const [newValue, setNewValue] = useState('');
  const [notes, setNotes] = useState('');

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Update time for alarm checking
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);



  const dismissUpcoming = async (alarmDateStr: string) => {
    setUpdating(true);
    const alarmTime = new Date(alarmDateStr);
    const existingActivity = (widget?.activity_data?.activity_history as AlarmActivity[]) || [];

    // Create a new activity record timestamped at the alarm time
    // This effectively "handles" the alarm before it even starts ringing
    const newActivity: AlarmActivity = {
      type: 'stop',
      timestamp: alarmTime.toISOString(),
    };

    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        activity_history: [...existingActivity, newActivity]
        // Note: We do NOT set status='completed' here. 
        // Dismising an upcoming alarm just skips that specific alarm instance.
        // The user can manually complete the task if they want.
      });
    } catch (err) {
      console.error('Error dismissing alarm:', err);
    } finally {
      setUpdating(false);
    }
  };

  // Height adjustment
  useEffect(() => {
    if (!widget) return;

    let height = 2;
    const activityHistory = (widget?.activity_data?.activity_history as AlarmActivity[]) || [];
    if (activityHistory.length > 0) {
      height += (activityHistory.length * 0.75) + 1;
    }
    if (widget?.description) {
      height += 1;
    }
    if (widget?.widget_config?.target_value) {
      height += 1;
    }
    // Simplified height adjustment
    const alarmTimes = (widget?.widget_config?.alarm_times as string[]) || [];
    if (alarmTimes.length > 0) {
      // Approximate height for list
      height += alarmTimes.length * 0.8;
    }

    onHeightChange(widget.daily_widget_id, height);
  }, [widget, isAlerting, onHeightChange]);

  // Alarm Check Loop
  useEffect(() => {
    const checkAlarms = () => {
      const alarmTimes = (widget?.widget_config?.alarm_times as string[]) || [];
      if (alarmTimes.length === 0 || !widget?.date) return;
      if (widget.date !== getTodayDateString()) return;

      const activityHistory = (widget?.activity_data?.activity_history as AlarmActivity[]) || [];
      const { shouldAlert, activeSnoozeTimeLeft } = checkAlarmTrigger(
        alarmTimes,
        activityHistory,
        snoozeTime
      );

      if (shouldAlert && !isAlerting) {
        setIsAlerting(true);
        setSnoozeTimeLeft(null);

        // Play sound logic...
        try {
          const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
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
          // Audio not supported, but alarm is triggered
        }
      } else if (!shouldAlert && isAlerting) {
        setIsAlerting(false);
      }

      // Sync local snooze countdown if logic says so
      if (activeSnoozeTimeLeft !== null && !isAlerting) {
        // Only update if widely different to avoid jitter, or if null
        if (snoozeTimeLeft === null || Math.abs(snoozeTimeLeft - activeSnoozeTimeLeft) > 2) {
          setSnoozeTimeLeft(activeSnoozeTimeLeft);
        }
      } else if (activeSnoozeTimeLeft === null && !shouldAlert) {
        setSnoozeTimeLeft(null);
      }
    };

    checkAlarms();
    intervalRef.current = setInterval(checkAlarms, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  }, [widget, isAlerting, snoozeTimeLeft]); // Added snoozeTimeLeft to dependency

  // Snooze Countdown
  useEffect(() => {
    const countdowns: NodeJS.Timeout[] = [];

    if (snoozeTimeLeft !== null && snoozeTimeLeft > 0) {
      const snoozeCountdown = setInterval(() => {
        setSnoozeTimeLeft(prev => {
          if (prev === null || prev <= 1) return null;
          return prev - 1;
        });
      }, 1000);
      countdowns.push(snoozeCountdown);
    }

    return () => countdowns.forEach(clearInterval);
  }, [snoozeTimeLeft]);

  // Actions
  const snoozeAlarm = async () => {
    setUpdating(true);
    const now = new Date();
    const newSnoozeCount = (Number(widget?.activity_data?.snooze_count) || 0) + 1;
    const existingActivity = (widget?.activity_data?.activity_history as AlarmActivity[]) || [];
    const newActivity: AlarmActivity = {
      type: 'snooze',
      timestamp: now.toISOString(),
    };

    setIsAlerting(false);
    setSnoozeTimeLeft(snoozeTime * 60);

    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        snooze_count: newSnoozeCount,
        activity_history: [...existingActivity, newActivity]
      });
    } catch (err) {
      console.error('Error snoozing alarm:', err);
    } finally {
      setUpdating(false);
    }
  };

  const stopAlarm = async () => {
    if (!widget?.id || updating) return;

    setUpdating(true);
    const now = new Date();
    const startedAt = now.toISOString();
    const existingActivity = (widget?.activity_data?.activity_history as AlarmActivity[]) || [];
    const newActivity: AlarmActivity = {
      type: 'stop',
      timestamp: now.toISOString(),
    };

    setIsAlerting(false);
    setSnoozeTimeLeft(null);

    try {
      await updateWidgetActivity(widget.daily_widget_id, {
        started_at: startedAt,
        activity_history: [...existingActivity, newActivity],
        status: 'completed',
        progress: 100
      });
    } catch (err) {
      console.error('Error stopping alarm:', err);
    } finally {
      setUpdating(false);
    }
  };

  const updateTrackerValue = async () => {
    if (!newValue.trim() || updating) return;

    setUpdating(true);
    const trackerUpdate = {
      value: newValue,
      time_added: new Date().toISOString(),
      notes: notes || undefined
    };

    setNewValue('');
    setNotes('');
    setShowAddForm(false);

    try {
      await updateWidgetActivity(widget.daily_widget_id, { ...trackerUpdate });
    } catch (err) {
      console.error('Failed to update tracker value:', err);
    } finally {
      setUpdating(false);
    }
  };

  const updateTaskStatus = async (status: 'pending' | 'in_progress' | 'completed' | 'cancelled') => {
    if (updating) return;

    setUpdating(true);
    const progress = status === 'completed' ? 100 : status === 'in_progress' ? 50 : 0;

    try {
      await updateWidgetActivity(widget.daily_widget_id, { status, progress });
    } catch (err) {
      console.error('Error updating task status:', err);
    } finally {
      setUpdating(false);
    }
  };

  if (!widget) {
    return (
      <BaseWidget title="Advanced Task" icon="🎯" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">No widget data available</p>
        </div>
      </BaseWidget>
    );
  }

  const activityData = widget.activity_data || {};
  const widgetConfig = widget.widget_config || {};
  const isCompleted = widget.activity_data?.status === 'completed';

  return (
    <BaseWidget
      title={isAlerting ? `🚨 Time for ${widget.title}! 🚨` : widget.title}
      icon={isAlerting ? "" : widget.activity_data?.status === 'completed' ? "✅" : "◻️"}
      onRemove={onRemove}
    >
      <div
        className={`flex flex-1 h-full p-2 flex-col overflow-y-auto rounded-lg transition-all ${isAlerting
          ? 'bg-gradient-to-r from-red-500 to-orange-500 border-2 border-red-400 text-white animate-pulse'
          : `border border-gray-200 rounded-lg`
          }`}
      >
        {/* ACTIONS when ringing */}
        {isAlerting && (
          <div className="flex gap-2 mb-3">
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

        {/* 1. HEADER: Checkbox | Title | Tracker Input */}
        <div className="flex items-start gap-3">
          <button
            onClick={() => updateTaskStatus(widget.activity_data?.status === 'completed' ? 'pending' : 'completed')}
            className="mt-1 flex-shrink-0"
            title={widget.activity_data?.status === 'completed' ? "Mark as pending" : "Mark as completed"}
          >
            {widget.activity_data?.status === 'completed' ? '✅' : '◻️'}
          </button>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h4 className={`font-medium text-base ${widget.activity_data?.status === 'completed' ? 'line-through text-gray-400' : 'text-gray-900'} leading-snug`}>
                {widget.title}
              </h4>

              {/* Tracker Value Display (Compact) */}
              {Boolean(widgetConfig.value_type) && Boolean(widgetConfig.target_value) && (
                <div className="flex flex-col items-end">
                  <div className="flex items-center gap-2 bg-gray-50 px-2 py-1 rounded-md border border-gray-100">
                    <span className={`font-bold ${isAlerting ? 'text-red-500' : 'text-gray-700'}`}>
                      {String(activityData.value || '0')}
                      <span className="text-xs font-normal text-gray-500 ml-0.5">{widgetConfig.value_unit as string as string}</span>
                    </span>
                    {!isCompleted && (
                      <button
                        onClick={() => setShowAddForm(true)}
                        disabled={updating}
                        className="text-green-600 hover:text-green-700 hover:bg-green-50 rounded-full p-0.5"
                        title="Add value"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-gray-400 mt-0.5 opacity-80">
                    <Target className="w-3 h-3" /> Target: {widgetConfig.target_value as string}
                  </div>
                </div>
              )}
            </div>

            {widget.description && (
              <p className={`text-xs mt-1 line-clamp-2 ${widget.activity_data?.status === 'completed' ? 'text-gray-300' : 'text-gray-500'}`}>
                {widget.description as string}
              </p>
            )}


          </div>
        </div>

        {/* 2. ALARMS LIST (Compact) */}
        {(widgetConfig.alarm_times as string[]) && (widgetConfig.alarm_times as string[]).length > 0 && (
          <div className="mt-4 border-t border-gray-100 pt-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-[10px] uppercase font-bold text-gray-400 tracking-wider flex items-center gap-1">
                <Clock className="w-3 h-3" /> Schedule
              </div>
            </div>

            <div className="space-y-1.5">
              {(widgetConfig.alarm_times as string[]).map((time: string) => {
                const statusData = getAlarmStatus(time, (widget.activity_data?.activity_history as AlarmActivity[]) || [], currentTime, isAlerting, snoozeTime);
                const status = statusData.status;

                // Status styles - Minimalist
                let rowClass = "text-gray-400";
                let statusText = null;
                let StatusIcon = null;

                if (status === 'active') { // Ringing
                  rowClass = "bg-red-50 text-red-600 border border-red-200 font-bold animate-pulse";
                  statusText = "Ringing";
                  StatusIcon = AlertTriangle;
                } else if (status === 'snoozed') {
                  rowClass = "bg-yellow-50 text-yellow-700 border border-yellow-200";
                  statusText = `Snoozed (${statusData.details})`;
                  StatusIcon = RotateCcw;
                } else if (status === 'done') {
                  rowClass = "text-green-600 font-medium bg-green-50/50";
                  statusText = "Done";
                  StatusIcon = Check;
                } else if (status === 'dismissed') {
                  rowClass = "text-gray-400 italic bg-gray-50/30";
                  statusText = "Dismissed";
                  StatusIcon = X;
                } else if (status === 'missed') {
                  rowClass = "text-amber-600 font-medium bg-amber-50/50";
                  statusText = "Missed";
                  StatusIcon = AlertTriangle;
                } else if (status === 'pending') {
                  const [h, m] = time.split(':').map(Number);
                  const d = new Date(); d.setHours(h, m, 0, 0);
                  // Highlight if within next hour
                  const now = currentTime.getTime();
                  const diff = d.getTime() - now;
                  if (diff > 0 && diff < 3600000) {
                    rowClass = "text-blue-600 font-medium bg-blue-50/50";
                    statusText = "Coming up";
                  } else {
                    rowClass = "text-gray-600";
                  }
                }

                return (
                  <div key={time} className={`flex items-center justify-between px-2 py-1.5 rounded text-xs transition-colors ${rowClass}`}>
                    <div className="flex items-center gap-2">
                      <span className="font-mono">{formatTime(new Date(new Date().setHours(parseInt(time.split(':')[0]), parseInt(time.split(':')[1]))), { hour: 'numeric', minute: '2-digit' })}</span>
                      {statusText && (
                        <span className="text-[10px] opacity-90 uppercase tracking-wide flex items-center gap-1 font-semibold">
                          {StatusIcon && <StatusIcon className="w-3 h-3" />} {statusText}
                        </span>
                      )}
                    </div>

                    {status === 'pending' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const [h, m] = time.split(':').map(Number);
                          const d = new Date(); d.setHours(h, m, 0, 0);
                          dismissUpcoming(d.toISOString());
                        }}
                        className={`${isAlerting ? 'text-white/70 hover:text-white' : 'text-gray-300 hover:text-red-500'} p-0.5 rounded transition-colors`}
                        title="Skip this alarm"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}



        {/* 4. FOOTER: Tags */}
        <div className="mt-auto pt-3 flex justify-end">
          {widget.category && (
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium text-${getCategoryColor(widget.category)}-700 bg-${getCategoryColor(widget.category)}-50 border border-${getCategoryColor(widget.category)}-100 opacity-80`}>
              {widget.category as string}
            </span>
          )}
        </div>

        {/* Add Value Modal */}
        {showAddForm && createPortal(
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
              <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-4 rounded-t-xl">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-bold">Add New Value</h3>
                    <p className="text-green-100 text-sm">Track your progress</p>
                  </div>
                  <button onClick={() => setShowAddForm(false)} className="text-white hover:text-green-100 p-1 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Value {(widgetConfig.value_unit as string) && `(${(widgetConfig.value_unit as string)})`}
                    </label>
                    <input
                      type={getValueTypeInput(widgetConfig.value_type as string)}
                      value={newValue}
                      onChange={(e) => setNewValue(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder={`Enter value`}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Add any notes about this entry..."
                      rows={3}
                    />
                  </div>
                </div>
                <div className="mt-6 flex justify-end gap-3">
                  <button onClick={() => setShowAddForm(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
                  <button
                    onClick={updateTrackerValue}
                    disabled={updating}
                    className={`px-4 py-2 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg shadow hover:shadow-lg transition-all transform hover:-translate-y-0.5 ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {updating ? 'Saving...' : 'Save Entry'}
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