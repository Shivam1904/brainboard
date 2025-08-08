import { useEffect, useState } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget } from '../../services/api';
import { dashboardService } from '../../services/dashboard';

interface MoodTrackerWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
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
];

const getTodayKey = () => new Date().toISOString().split('T')[0];

const MoodTrackerWidget = ({ onRemove, widget }: MoodTrackerWidgetProps) => {
  const [selectedMoodIds, setSelectedMoodIds] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [dailyWidgetId, setDailyWidgetId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate from today's daily widget if it exists; do not create automatically
  useEffect(() => {
    const ensureDailyWidget = async () => {
      console.log('widget', widget);
      if (!widget.widget_id) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const todayDw = await dashboardService.getTodayWidgetByWidgetId(widget.widget_id);
        if (todayDw && todayDw.id) {
          setDailyWidgetId(todayDw.id);
          const currentMoods: string[] = todayDw.activity_data?.selected_moods || [];
          setSelectedMoodIds(new Set(currentMoods));
          console.log('todayDw', todayDw);
        }
      } catch (err) {
        console.error('Failed to prepare mood tracker daily widget', err);
      } finally {
        setLoading(false);
      }
    };
    ensureDailyWidget();
  }, [widget]);

  const toggleMood = (moodId: string) => {
    setSelectedMoodIds(prev => {
      const next = new Set(prev);
      if (next.has(moodId)) {
        next.delete(moodId);
      } else {
        next.add(moodId);
      }
      return next;
    });
  };

  const clearSelection = () => {
    setSelectedMoodIds(new Set());
  };

  const saveSelection = async () => {
    if (!widget.widget_id) {
      alert('Mood widget is not properly configured.');
      return;
    }
    setSaving(true);
    try {
      let currentDailyWidgetId = dailyWidgetId;
      if (!currentDailyWidgetId) {
        // Create today's daily widget on first save
        const created = await dashboardService.addWidgetToToday(widget.widget_id);
        currentDailyWidgetId = created?.daily_widget_id || null;
        setDailyWidgetId(currentDailyWidgetId);
      }
      if (!currentDailyWidgetId) throw new Error('Failed to create daily widget.');

      await dashboardService.updateActivity(currentDailyWidgetId, {
        selected_moods: Array.from(selectedMoodIds),
        saved_at: new Date().toISOString(),
      });
      setSavedAt(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to save mood selection', err);
      alert('Failed to save selection.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <BaseWidget title={widget.title || 'Mood Tracker'} icon="😊" onRemove={onRemove}>
      <div className="h-full flex flex-col">
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">Loading…</div>
        ) : (
          <>
            <div className="p-3">
              <p className="text-sm text-muted-foreground">
                Select how you feel today. You can choose multiple moods.
              </p>
            </div>

            <div className="px-3">
              <div className="grid grid-cols-5 gap-2">
                {MOODS.map((mood) => {
                  const isSelected = selectedMoodIds.has(mood.id);
                  return (
                    <button
                      key={mood.id}
                      onClick={() => toggleMood(mood.id)}
                      className={
                        `flex flex-col items-center justify-center rounded-md border py-3 transition-colors select-none ` +
                        (isSelected
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'bg-card text-card-foreground border-border hover:bg-accent hover:text-accent-foreground')
                      }
                      title={mood.label}
                    >
                      <div className="text-xl mb-1">{mood.emoji}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="mt-auto p-3 flex items-center justify-between gap-2">
              <div className="text-xs text-muted-foreground">
                {savedAt ? `Saved at ${savedAt}` : 'Not saved yet'}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={clearSelection}
                  className="px-3 py-1 text-sm rounded border bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  disabled={saving}
                >
                  Clear
                </button>
                <button
                  onClick={saveSelection}
                  className="px-3 py-1 text-sm rounded bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
                  disabled={saving}
                >
                  {saving ? 'Saving…' : 'Save'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </BaseWidget>
  );
};

export default MoodTrackerWidget;

