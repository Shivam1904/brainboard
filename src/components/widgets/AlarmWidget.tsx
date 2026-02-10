import { useState, useEffect, useRef } from 'react';
import BaseWidget from './BaseWidget';
import { Clock, RotateCcw, Check, AlertTriangle } from 'lucide-react';
import { AlarmDetailsAndActivityResponse } from '../../types/widgets';
import { apiService, DailyWidget } from '../../services/api';

interface AlarmWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
}

// Removed unused helpers; using time window-based alerting below

const AlarmWidget = ({ onRemove, widget }: AlarmWidgetProps) => {
  const [alarmData, setAlarmData] = useState<AlarmDetailsAndActivityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAlerting, setIsAlerting] = useState(false);
  const [snoozeTimeLeft, setSnoozeTimeLeft] = useState<number | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAlarms = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get the widget_id from the widget_ids array (first one for alarm widgets)
      const widgetId = widget.widget_id || '111111';

      // Call the real API
      const response = await apiService.getAlarmDetailsAndActivity(widgetId);
      setAlarmData(response);
    } catch (err) {
      console.error('Failed to fetch alarms:', err);
      setError('Failed to load alarms');
      // Fallback to empty state
      setAlarmData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlarmsRef = useRef(fetchAlarms);
  fetchAlarmsRef.current = fetchAlarms;

  const snoozeAlarm = async () => {
    if (!alarmData?.activity?.id) return;

    try {
      await apiService.snoozeAlarm(alarmData.activity.id, 10);
      setIsAlerting(false);
      setSnoozeTimeLeft(600); // 10 minutes in seconds
      await fetchAlarms(); // Refresh data
    } catch (err) {
      console.error('Error snoozing alarm:', err);
    }
  };

  const stopAlarm = async () => {
    if (!alarmData?.activity?.id) return;

    try {
      await apiService.stopAlarm(alarmData.activity.id);
      setIsAlerting(false);
      setSnoozeTimeLeft(null);
      await fetchAlarms(); // Refresh data
    } catch (err) {
      console.error('Error stopping alarm:', err);
    }
  };

  // Check for triggered alarms and snooze status
  useEffect(() => {
    const checkAlarms = () => {
      if (!alarmData) return;

      const now = new Date();
      let shouldAlert = false;

      // Check if alarm was already started today
      if (alarmData.activity?.started_at) {
        setIsAlerting(false);
        setSnoozeTimeLeft(null);
        return;
      }

      // Check if currently snoozed
      if (alarmData.activity?.snooze_until) {
        const snoozeUntil = new Date(alarmData.activity.snooze_until);
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
      alarmData.alarm_details?.alarm_times.forEach((alarmTime) => {
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
    };

    checkAlarms();
    intervalRef.current = setInterval(checkAlarms, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [alarmData, isAlerting]);

  // Update snooze countdown
  useEffect(() => {
    if (snoozeTimeLeft === null || snoozeTimeLeft <= 0) return;

    const countdown = setInterval(() => {
      setSnoozeTimeLeft(prev => {
        if (prev === null || prev <= 1) {
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdown);
  }, [snoozeTimeLeft]);

  useEffect(() => {
    fetchAlarmsRef.current();
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

  const getNextAlarmTime = (alarm_times: string[]): string => {
    const now = new Date();
    const nextAlarmTime = alarm_times?.find(time => {
      const [hours, minutes] = time.split(':').map(Number);
      const alarmDate = new Date();
      alarmDate.setHours(hours, minutes, 0, 0);
      return alarmDate > now;
    });
    return nextAlarmTime || 'No alarms set';
  };

  const formatSnoozeTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <BaseWidget
      title={isAlerting ? "🚨 ALARM TRIGGERED! 🚨" : "Alarms"}
      icon={isAlerting ? "🔔" : "⏰"}
      onRemove={onRemove}
    >
      <div className="h-full flex flex-col">
        {/* Main Alarm Display - Always visible */}
        <div className={`flex-1 p-4 rounded-lg transition-all duration-300 ${isAlerting
          ? 'bg-gradient-to-r from-red-500 to-orange-500 border-2 border-red-400 animate-pulse shadow-lg'
          : 'bg-blue-50 border border-blue-200'
          }`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex flex-col items-center gap-2">
              <div className="flex flex-row items-center gap-2">
                <Clock className={`h-5 w-5 ${isAlerting ? 'text-white' : 'text-blue-600'}`} />
                <span className={`text-sm font-medium ${isAlerting ? 'text-white' : 'text-blue-800'}`}>
                  Next Alarm at {getNextAlarmTime(alarmData.alarm_details?.alarm_times)}
                </span>
              </div>
              <span className={`text-sm font-medium ${isAlerting ? 'text-white' : 'text-blue-800'}`}>
                All Alarms: {alarmData.alarm_details?.alarm_times.join(', ')}
              </span>
            </div>
            {isAlerting && (
              <div className="animate-bounce">
                <AlertTriangle className="h-5 w-5 text-white" />
              </div>
            )}
          </div>

          <div className={`text-lg font-bold mb-3 ${isAlerting ? 'text-white' : 'text-blue-900'}`}>
            {alarmData.alarm_details?.title}
          </div>

          {/* Snooze countdown */}
          {snoozeTimeLeft !== null && snoozeTimeLeft > 0 && (
            <div className="mb-3 p-2 bg-yellow-100 border border-yellow-300 rounded">
              <div className="text-sm text-yellow-800">
                ⏰ Snoozed for {formatSnoozeTime(snoozeTimeLeft)}
              </div>
            </div>
          )}

          {/* Action buttons - only show when alerting */}
          {isAlerting && (
            <div className="flex gap-3 mt-4">
              <button
                onClick={snoozeAlarm}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md flex items-center justify-center gap-2"
                title="Snooze for 2 minutes"
              >
                <RotateCcw className="h-4 w-4" />
                <span className="font-medium">Snooze</span>
              </button>
              <button
                onClick={stopAlarm}
                className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors shadow-md flex items-center justify-center gap-2"
                title="Stop alarm"
              >
                <Check className="h-4 w-4" />
                <span className="font-medium">Stop</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </BaseWidget>
  );
};

export default AlarmWidget; 