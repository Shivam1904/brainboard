import { useEffect, useState, useCallback } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget } from '../../services/api';
import { dashboardService } from '../../services/dashboard';
import { useDashboardActions } from '@/stores/dashboardStore';

interface NotesWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
}

const NotesWidget = ({ onRemove, widget, targetDate }: NotesWidgetProps) => {
  const [notes, setNotes] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
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
          const currentNotes: string = todayDw.activity_data?.notes || '';
          setNotes(currentNotes);
        }
      } catch (err) {
        console.error('Failed to prepare notes widget daily widget', err);
      } finally {
        setLoading(false);
      }
    };
    ensureDailyWidget();
  }, [widget, targetDate]);

  const saveNotes = useCallback(async () => {
    if (!widget.widget_id) {
      alert('Notes widget is not properly configured.');
      return;
    }
    setSaving(true);
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
        notes: notes,
        saved_at: new Date().toISOString(),
      });
      setSavedAt(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to save notes', err);
      alert('Failed to save notes.');
    } finally {
      setSaving(false);
    }
  }, [widget.widget_id, dailyWidgetId, notes, targetDate, addWidgetToToday, updateWidgetActivity]);

  // Auto-save with debouncing when typing stops
  useEffect(() => {
    if (notes === '' || !dailyWidgetId) return;
    
    const timeoutId = setTimeout(() => {
      saveNotes();
    }, 1000); // Save 1 second after user stops typing

    return () => clearTimeout(timeoutId);
  }, [notes, dailyWidgetId, saveNotes]);

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotes(e.target.value);
  };

  return (
    <BaseWidget title={widget.title || 'Notes'} icon="📝" onRemove={onRemove}>
      <div className="h-full flex flex-col">
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">Loading…</div>
        ) : (
          <>
            <div className="p-3">
              <p className="text-sm text-muted-foreground">
                What's on your mind today?
              </p>
            </div>

            <div className="px-3 flex-1">
              <textarea
                value={notes}
                onChange={handleNotesChange}
                placeholder="Write your notes here..."
                className="w-full h-full min-h-[120px] p-3 text-sm border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onBlur={saveNotes}
              />
            </div>

            <div className="p-3 flex justify-end items-center">
              {saving && (
                <span className="text-xs text-muted-foreground">
                  Saving...
                </span>
              )}
              {savedAt && !saving && (
                <span className="text-xs text-muted-foreground">
                  Saved at {savedAt}
                </span>
              )}
            </div>
          </>
        )}
      </div>
    </BaseWidget>
  );
};

export default NotesWidget; 