import { useEffect, useState } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget } from '../../services/api';
import { dashboardService } from '../../services/dashboard';
import { useDashboardActions } from '@/stores/dashboardStore';

interface MoodTrackerWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
  hideTitle?: boolean;
}

type MoodOption = {
  id: string;
  label: string;
  emoji: string;
};

const MOODS: MoodOption[] = [
  { id: 'happy', label: 'Happy', emoji: '😊' },
  { id: 'sad', label: 'Sad', emoji: '😔' },
  { id: 'calm', label: 'Calm', emoji: '😌' },
  { id: 'anxious', label: 'Anxious', emoji: '😟' },
  { id: 'energetic', label: 'Energetic', emoji: '⚡️' },
  { id: 'tired', label: 'Tired', emoji: '🥱' },
  { id: 'focused', label: 'Focused', emoji: '🎯' },
  { id: 'stressed', label: 'Stressed', emoji: '😣' },
  { id: 'grateful', label: 'Grateful', emoji: '🙏' },
  { id: 'angry', label: 'Angry', emoji: '😠' },
  { id: 'excited', label: 'Excited', emoji: '🤩' },
  { id: 'motivated', label: 'Motivated', emoji: '💪' },
];

const MoodTrackerWidget = ({ onRemove, widget, targetDate, hideTitle }: MoodTrackerWidgetProps) => {
  const [selectedMoodIds, setSelectedMoodIds] = useState<Set<string>>(new Set());
  const [dailyWidgetId, setDailyWidgetId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { addWidgetToToday, updateWidgetActivity } = useDashboardActions();
  // Hydrate from today's daily widget if it exists; do not create automatically
  useEffect(() => {
    const ensureDailyWidget = async () => {
      if (!widget.widget_id) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const todayDw = await dashboardService.getTodayWidgetByWidgetId(widget.widget_id, targetDate);
        if (todayDw && todayDw.id) {
          setDailyWidgetId(todayDw.id);
          const currentMoods: string[] = (todayDw.activity_data as Record<string, unknown>)?.selected_moods as string[] || [];
          setSelectedMoodIds(new Set(currentMoods));
        }
      } catch (err) {
        console.error('Failed to prepare mood tracker daily widget', err);
      } finally {
        setLoading(false);
      }
    };
    ensureDailyWidget();
  }, [widget, targetDate]);

  const toggleMood = async (moodId: string) => {
    const next = new Set(selectedMoodIds);
    if (next.has(moodId)) {
      next.delete(moodId);
    } else {
      next.add(moodId);
    }
    setSelectedMoodIds(next);
    // Auto-save on every change
    saveSelection(Array.from(next));
  };



  const saveSelection = async (moodsOverride?: string[]) => {
    if (!widget.widget_id) {
      alert('Mood widget is not properly configured.');
      return;
    }
    try {
      let currentDailyWidgetId = dailyWidgetId;
      if (!currentDailyWidgetId) {
        // Create today's daily widget on first save
        const created = await addWidgetToToday(widget.widget_id, targetDate);
        currentDailyWidgetId = created?.daily_widget_id || null;
        setDailyWidgetId(currentDailyWidgetId);
      }
      if (!currentDailyWidgetId) throw new Error('Failed to create daily widget.');

      await updateWidgetActivity(currentDailyWidgetId, {
        selected_moods: moodsOverride ?? Array.from(selectedMoodIds),
        saved_at: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Failed to save mood selection', err);
      alert('Failed to save selection.');
    }
  };

  return (
    <BaseWidget title={widget.title || 'Mood Tracker'} icon="😊" onRemove={onRemove} hideTitle={hideTitle}>
      <div className="h-full flex flex-col">
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">Loading…</div>
        ) : (
          <>
            <div className="p-3">
              <p className="text-sm text-muted-foreground">
                How am I feeling today?
              </p>
            </div>

            <div className="px-3">
              <div className="grid grid-cols-4 ">
                {MOODS.map((mood) => {
                  const isSelected = selectedMoodIds.has(mood.id);
                  return (
                    <button
                      key={mood.id}
                      onClick={() => toggleMood(mood.id)}
                      className={
                        `flex flex-col items-center justify-center select-none `}
                      title={mood.label}
                    >
                      <div className={`rounded-full border p-2 px-3 transition-colors text-4xl
                         ${isSelected ? 'bg-blue-300'
                          : 'bg-card text-card-foreground opacity-50 border-border hover:bg-accent hover:text-accent-foreground'}`}>
                        {mood.emoji}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </BaseWidget>
  );
};

export default MoodTrackerWidget;

