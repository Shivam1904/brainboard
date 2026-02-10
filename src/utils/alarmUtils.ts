
export interface AlarmActivity {
    timestamp: string;
    type: 'stop' | 'snooze';
}

export const formatSnoozeTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const getNextAlarmTime = (alarm_times?: string[]): string => {
    if (!alarm_times) return '';
    const now = new Date();
    const nextAlarmTime = alarm_times?.find(time => {
        const [hours, minutes] = time.split(':').map(Number);
        const alarmDate = new Date();
        alarmDate.setHours(hours, minutes, 0, 0);
        return alarmDate > now;
    });
    return nextAlarmTime || '';
};

export const checkAlarmTrigger = (
    alarm_times: string[],
    activityHistory: AlarmActivity[],
    snoozeTime: number = 10
): { shouldAlert: boolean; activeSnoozeTimeLeft: number | null } => {
    const now = new Date();
    let shouldAlert = false;
    let activeSnoozeTimeLeft: number | null = null;

    alarm_times.forEach((alarmTime: string) => {
        const [hours, minutes] = alarmTime.split(':').map(Number);
        const alarmStart = new Date();
        alarmStart.setHours(hours, minutes, 0, 0);
        const alarmEnd = new Date(alarmStart.getTime() + 60 * 60 * 1000);

        if (now >= alarmStart && now < alarmEnd) {
            // Filter activities relevant to this specific alarm window
            const relevantActivities = activityHistory.filter((activity: AlarmActivity) => {
                const t = new Date(activity.timestamp);
                return t >= alarmStart && t < alarmEnd;
            }).sort((a: AlarmActivity, b: AlarmActivity) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

            if (relevantActivities.length === 0) {
                // No activity, should alert
                shouldAlert = true;
            } else {
                const lastActivity = relevantActivities[0];
                if (lastActivity.type === 'stop') {
                    // Stopped, handled
                } else if (lastActivity.type === 'snooze') {
                    const snoozeEnd = new Date(lastActivity.timestamp).getTime() + (snoozeTime * 60 * 1000);
                    if (now.getTime() < snoozeEnd) {
                        // Still snoozed
                        activeSnoozeTimeLeft = Math.ceil((snoozeEnd - now.getTime()) / 1000);
                    } else {
                        // Snooze expired, should alert again
                        shouldAlert = true;
                    }
                }
            }
        }
    });

    return { shouldAlert, activeSnoozeTimeLeft };
};

export const getNearestUpcomingAlarm = (
    alarm_times: string[],
    activityHistory: AlarmActivity[],
    currentTime: Date
) => {
    if (!Array.isArray(alarm_times)) return null;

    const oneHourLater = new Date(currentTime.getTime() + 60 * 60 * 1000);
    let nearest = null;

    for (const timeStr of alarm_times) {
        if (typeof timeStr !== 'string') continue;
        const [hours, minutes] = timeStr.split(':').map(Number);
        const alarmDate = new Date();
        alarmDate.setHours(hours, minutes, 0, 0);
        const alarmEndDate = new Date(alarmDate.getTime() + 60 * 60 * 1000);

        // Check if handling needed
        const isHandled = activityHistory.some((activity: AlarmActivity) => {
            const activityTime = new Date(activity.timestamp);
            return activityTime >= alarmDate && activityTime < alarmEndDate;
        });

        if (alarmDate > currentTime && alarmDate <= oneHourLater && !isHandled) {
            if (!nearest || alarmDate < nearest.time) {
                nearest = {
                    time: alarmDate,
                    minutesLeft: Math.ceil((alarmDate.getTime() - currentTime.getTime()) / 60000)
                };
            }
        }
    }
    return nearest;
};

export type AlarmStatus = 'pending' | 'active' | 'snoozed' | 'done' | 'dismissed' | 'missed';

export const getAlarmStatus = (
    alarmTimeStr: string,
    activityHistory: AlarmActivity[],
    currentTime: Date,
    isAlerting: boolean, // Pass isAlerting from widget state to know if THIS alarm is ringing
    snoozeTime: number = 10
): { status: AlarmStatus; details?: string } => {
    const [hours, minutes] = alarmTimeStr.split(':').map(Number);
    const alarmDate = new Date();
    alarmDate.setHours(hours, minutes, 0, 0);

    // Window is 1 hour
    const alarmEndDate = new Date(alarmDate.getTime() + 60 * 60 * 1000);

    // 1. Future Pending
    if (currentTime < alarmDate) {
        // Check if it was pre-dismissed (stopped with a timestamp matching the alarm time exactly or close)
        // Actually our dismiss logic adds a 'stop' activity at the alarm time. 
        // Since alarmDate > currentTime, that activity would be in the future? 
        // Ah, wait. If I dismiss a 14:00 alarm at 10:00.
        // I likely insert a 'stop' activity with timestamp = 14:00 ?? 
        // Yes, my previous code did: `timestamp: alarmTime.toISOString()`.
        // So `activityHistory` will contain a future timestamp.

        // Let's optimize: Check if there's any 'stop' activity targeting this alarm window
        const isDismissed = activityHistory.some((activity: AlarmActivity) => {
            const t = new Date(activity.timestamp);
            return activity.type === 'stop' && t >= alarmDate && t < alarmEndDate;
        });

        if (isDismissed) return { status: 'dismissed' };
        return { status: 'pending' };
    }

    // 2. Currently Ringing?
    // We rely on isAlerting passed in, BUT isAlerting is global for the widget.
    // We need to know if THIS specific alarm is the one ringing.
    // The widget logic alerts if `currentTime >= alarmDate && currentTime < alarmEndDate`.
    // So if isAlerting is true AND we are in this window... it's the active one.
    // (Assuming non-overlapping alarms for simplicity).
    if (isAlerting && currentTime >= alarmDate && currentTime < alarmEndDate) {
        return { status: 'active' };
    }

    // 3. Past / Active Window Logic
    if (currentTime >= alarmDate && currentTime < alarmEndDate) {
        // We are in the window.

        // Check activities
        const relevantActivities = activityHistory.filter((activity: AlarmActivity) => {
            const t = new Date(activity.timestamp);
            return t >= alarmDate && t < alarmEndDate;
        }).sort((a: AlarmActivity, b: AlarmActivity) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

        if (relevantActivities.length === 0) {
            // No activity, but time passed? 
            // If isAlerting was false (handled above), then maybe we missed it? 
            // Or the widget just hasn't ticked yet? 
            // Usually implies 'missed' if substantial time passed, or 'active' if just started.
            // Let's call it 'missed' if not alerting.
            return { status: 'missed' };
        }

        const lastActivity = relevantActivities[0];
        if (lastActivity.type === 'stop') {
            return { status: 'done' };
        }
        if (lastActivity.type === 'snooze') {
            const snoozeEnd = new Date(lastActivity.timestamp).getTime() + (snoozeTime * 60 * 1000);
            if (currentTime.getTime() < snoozeEnd) {
                const timeLeft = Math.ceil((snoozeEnd - currentTime.getTime()) / 1000);
                return { status: 'snoozed', details: formatSnoozeTime(timeLeft) };
            } else {
                // Snooze expired! Should be ringing. 
                // If not ringing (isAlerting false), it's weird.
                return { status: 'active' };
            }
        }
    }

    // 4. Past (outside window)
    // Check if it was handled
    const wasHandled = activityHistory.some((activity: AlarmActivity) => {
        const t = new Date(activity.timestamp);
        return t >= alarmDate && t < alarmEndDate; // Basic check
    });

    if (wasHandled) return { status: 'done' };

    return { status: 'missed' }; // or 'done' if we don't care to shame the user
};
