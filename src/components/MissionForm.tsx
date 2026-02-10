import { useState } from 'react';
import { createPortal } from 'react-dom';
import { Save, Loader2 } from 'lucide-react';
import { getWidgetConfig } from '../config/widgets';
import { ApiWidgetType, ApiFrequency, ApiCategory } from '../types/widgets';
import { dashboardService } from '../services/dashboard';
import FrequencySection from './widgets/FrequencySection';
import { FrequencySettings } from '../types/frequency';
import { DashboardWidget } from '@/services/api';

interface MissionFormProps {
  onClose: () => void;
  onSuccess: () => void;
  editMode?: boolean;
  existingWidget?: DashboardWidget;
}

interface FormData {
  title: string;
  frequency_details: FrequencySettings;
  importance: number;
  category: ApiCategory;
  description?: string;
  is_permanent: boolean;
  widgetConfig: {
    // Progress fields
    streak_type?: string;
    streak_count?: number;
    milestones?: Array<{ text: string; due_date: string }>;
    include_progress_details?: boolean;
    selected_calendar?: string;

    // Alarm fields
    alarm_times?: string[];
    is_snoozable?: boolean;
    include_alarm_details?: boolean;

    // Tracker fields
    value_type?: string;
    value_unit?: string;
    target_value?: string;
    include_tracker_details?: boolean;

    // Web search fields
    search_query_detailed?: string;
    include_websearch_details?: boolean;

    [key: string]: unknown;
  };
}

const MissionForm = ({ onClose, onSuccess, editMode = false, existingWidget }: MissionFormProps) => {
  const widgetConfig = getWidgetConfig('todo-task');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getInitialFormData = (): FormData => {
    if (editMode && existingWidget) {
      const saved = existingWidget.frequency_details as FrequencySettings | undefined;
      const hasValidFrequencyDetails = saved && typeof saved.frequencyPeriod === 'string' && typeof saved.frequency === 'number';
      return {
        title: existingWidget.title,
        description: existingWidget.description,
        is_permanent: false,
        frequency_details: hasValidFrequencyDetails ? {
          frequencySet: saved.frequencySet ?? 'BALANCED',
          frequencySetValue: saved.frequencySetValue ?? 0.6,
          frequency: saved.frequency,
          frequencyUnit: saved.frequencyUnit ?? 'TIMES',
          frequencyPeriod: saved.frequencyPeriod,
          isDailyHabit: saved.isDailyHabit ?? false
        } : {
          frequencySet: 'BALANCED',
          frequencySetValue: 0.6,
          frequency: 3,
          frequencyUnit: 'TIMES',
          frequencyPeriod: existingWidget.frequency === 'daily' ? 'DAILY' :
            existingWidget.frequency === 'weekly' ? 'WEEKLY' : 'MONTHLY',
          isDailyHabit: false
        },
        importance: existingWidget.importance,
        category: (existingWidget.category).toLowerCase() as ApiCategory,
        widgetConfig: {
          ...existingWidget.widget_config,
          streak_type: (existingWidget.widget_config?.streak_type as string) || 'none',
          streak_count: (existingWidget.widget_config?.streak_count as number) || 1,
          milestones: (existingWidget.widget_config?.milestones as Array<{ text: string; due_date: string }>) || [],
          include_progress_details: !!existingWidget.widget_config?.include_progress_details,
          selected_calendar: (existingWidget.widget_config?.selected_calendar as string) || '',
          alarm_times: (existingWidget.widget_config?.alarm_times as string[]) || [],
          is_snoozable: existingWidget.widget_config?.is_snoozable as boolean | undefined ?? true,
          include_alarm_details: !!existingWidget.widget_config?.include_alarm_details,
          include_tracker_details: !!existingWidget.widget_config?.include_tracker_details,
          include_websearch_details: !!existingWidget.widget_config?.include_websearch_details
        }
      };
    }

    return {
      title: '',
      description: '',
      is_permanent: false,
      frequency_details: {
        frequencySet: 'BALANCED',
        frequencySetValue: 0.6,
        frequency: 3,
        frequencyUnit: 'TIMES',
        frequencyPeriod: 'DAILY',
        isDailyHabit: false
      },
      importance: 0.7,
      category: 'productivity',
      widgetConfig: {
        streak_type: 'none',
        streak_count: 1,
        milestones: [],
        include_progress_details: false,
        selected_calendar: '',
        alarm_times: [],
        is_snoozable: true,
        include_alarm_details: false,
        value_type: 'number',
        value_unit: 'units',
        target_value: '',
        include_tracker_details: false,
        search_query_detailed: '',
        include_websearch_details: false
      }
    };
  };

  const [formData, setFormData] = useState<FormData>(getInitialFormData());
  const [newAlarmTime, setNewAlarmTime] = useState('');
  const [alarmInputTouched, setAlarmInputTouched] = useState(false);

  if (!widgetConfig) {
    return null;
  }

  const getCategoryColor = (category: string) => {
    // Used for visual accents (e.g. rhythm section), so return actual color values
    switch (category) {
      case 'productivity': return '#3B82F6'; // blue-500
      case 'health': return '#10B981'; // emerald-500
      case 'work': return '#8B5CF6'; // purple-500
      case 'research': return '#F59E0B'; // amber-500
      case 'entertainment': return '#EC4899'; // pink-500
      case 'utilities': return '#6B7280'; // gray-500
      default: return '#6B7280';
    }
  };

  const updateWidgetConfig = (key: string, value: unknown) => {
    setFormData(prev => ({
      ...prev,
      widgetConfig: {
        ...prev.widgetConfig,
        [key]: value
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const apiFrequency: ApiFrequency = formData.frequency_details.frequencyPeriod === 'DAILY' ? 'daily' :
        formData.frequency_details.frequencyPeriod === 'WEEKLY' ? 'weekly' : 'monthly';

      const apiData = {
        widget_type: widgetConfig.apiWidgetType as ApiWidgetType,
        title: formData.title.trim(),
        description: formData.description?.trim(),
        frequency: apiFrequency,
        frequency_details: formData.frequency_details as unknown as Record<string, unknown>,
        importance: formData.importance,
        category: formData.category,
        is_permanent: false,
        widget_config: formData.widgetConfig as Record<string, unknown>
      };

      if (editMode && existingWidget) {
        await dashboardService.updateWidget(existingWidget.id, apiData);
      } else {
        await dashboardService.createWidget(apiData);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error(editMode ? 'Failed to update widget:' : 'Failed to create widget:', err);
      setError(editMode ? 'Failed to update widget. Please try again.' : 'Failed to create widget. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sortedAlarmTimes = (formData.widgetConfig.alarm_times || []).slice().sort();

  const handleAddAlarm = () => {
    if (!newAlarmTime) return;

    setFormData(prev => {
      const existing = (prev.widgetConfig.alarm_times || []) as string[];
      if (existing.includes(newAlarmTime)) {
        return {
          ...prev,
          widgetConfig: {
            ...prev.widgetConfig,
            include_alarm_details: true
          }
        };
      }

      const updated = [...existing, newAlarmTime].sort();
      return {
        ...prev,
        widgetConfig: {
          ...prev.widgetConfig,
          alarm_times: updated,
          include_alarm_details: true
        }
      };
    });

    setNewAlarmTime('');
  };

  const modalContent = (
    <div className="fixed inset-0 z-[999] flex items-start justify-center bg-slate-950/70 px-4 py-6 sm:px-6 sm:py-10 overflow-y-auto">
      <div className="relative w-full w-full">
        <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-6 md:p-8 space-y-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-2xl md:text-3xl font-semibold text-slate-900">
                {editMode ? 'Refine your mission' : 'Design a new mission'}
              </h3>
              <p className="mt-2 text-sm text-slate-600 max-w-xl">
                Capture what you want to accomplish, then layer in gentle nudges and tracking when you are ready.
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="hidden md:inline-flex items-center text-xs font-medium text-slate-500 hover:text-slate-700"
            >
              Close
            </button>
          </div>

          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <div className="space-y-4">
              <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-4 md:p-5 space-y-4">
                <div className="space-y-1">
                  <label className="block text-xs font-medium uppercase tracking-wide text-slate-500">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="I want to accomplish.."
                    required
                  />
                  <p className="text-[11px] text-slate-500">
                    Phrase it like a promise to yourself. This becomes the headline of your mission.
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-medium uppercase tracking-wide text-slate-500">
                    Description
                  </label>
                  <textarea
                    value={formData.description || ''}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Motivate yourself.."
                    rows={3}
                  />
                  <p className="text-[11px] text-slate-500">
                    Remind future-you why this matters. A strong why makes it harder to drop.
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-xs font-semibold tracking-wide text-slate-600 uppercase">
                      Category *
                    </h4>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Choose the pillar this mission supports. It helps group your progress later.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { value: 'productivity', label: 'Productivity', color: 'from-blue-500 to-blue-600' },
                      { value: 'health', label: 'Health', color: 'from-emerald-500 to-emerald-600' },
                      { value: 'work', label: 'Work', color: 'from-purple-500 to-purple-600' },
                      { value: 'research', label: 'Research', color: 'from-amber-500 to-amber-600' },
                      { value: 'entertainment', label: 'Joy / Play', color: 'from-pink-500 to-pink-600' },
                      { value: 'utilities', label: 'Life admin', color: 'from-slate-500 to-slate-600' }
                    ].map((category) => (
                      <button
                        key={category.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, category: category.value as ApiCategory })}
                        className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                          formData.category === category.value
                            ? `bg-gradient-to-r ${category.color} text-white shadow-sm`
                            : 'bg-white text-slate-700 hover:bg-slate-100'
                        }`}
                      >
                        {category.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-4 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-xs font-semibold tracking-wide text-slate-600 uppercase">
                    Rhythm
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    Gentle structure for how often you show up
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mb-1">
                  Set a rhythm that feels sustainable. You can always tweak this later.
                </p>
                <div className="mt-2">
                  <FrequencySection
                    frequency={formData.frequency_details}
                    onChange={(frequency) => setFormData({ ...formData, frequency_details: frequency })}
                    pillarColor={getCategoryColor(formData.category)}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/40 p-4 space-y-2">
                <h4 className="text-xs font-semibold tracking-wide text-slate-600 uppercase">
                  Progress (coming soon)
                </h4>
                <p className="text-xs text-slate-500">
                  You&apos;ll soon be able to break this into milestones and streaks you can actually see.
                </p>
              </div>

              <div className="rounded-xl border border-amber-100 bg-amber-50/70 p-4 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-xs font-semibold tracking-wide text-amber-800 uppercase">
                    Alarms
                  </h4>
                  <span className="text-[11px] text-amber-700/80">
                    Optional gentle nudges
                  </span>
                </div>

                <div className="flex flex-col gap-2">
                  <div className="flex gap-2 items-center">
                    <input
                      type="time"
                      value={newAlarmTime}
                      onChange={(e) => {
                        setNewAlarmTime(e.target.value);
                        setAlarmInputTouched(true);
                      }}
                      className="flex-1 px-3 py-2 rounded-lg border border-amber-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      placeholder="Alarm"
                    />
                    <button
                      type="button"
                      onClick={handleAddAlarm}
                      disabled={!newAlarmTime}
                      className="px-3 py-2 rounded-lg text-xs font-semibold bg-amber-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-amber-700 transition-colors"
                    >
                      Add
                    </button>
                  </div>
                  {sortedAlarmTimes.length === 0 && !alarmInputTouched && (
                    <p className="text-xs text-amber-700/80 italic">No alarm</p>
                  )}
                </div>

                {sortedAlarmTimes.length > 0 && (
                  <div className="mt-2 space-y-2">
                    <div className="flex flex-wrap gap-2">
                      {sortedAlarmTimes.map((time) => (
                        <div
                          key={time}
                          className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs border border-amber-200"
                        >
                          <span className="font-medium text-amber-800">{time}</span>
                          <button
                            type="button"
                            onClick={() =>
                              setFormData(prev => {
                                const existing = (prev.widgetConfig.alarm_times || []) as string[];
                                const filtered = existing.filter(t => t !== time);
                                return {
                                  ...prev,
                                  widgetConfig: {
                                    ...prev.widgetConfig,
                                    alarm_times: filtered
                                  }
                                };
                              })
                            }
                            className="text-amber-500 hover:text-amber-700"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>

                    <label className="flex items-center gap-2 pt-1">
                      <input
                        type="checkbox"
                        checked={formData.widgetConfig.is_snoozable !== false}
                        onChange={(e) => updateWidgetConfig('is_snoozable', e.target.checked)}
                        className="rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                      />
                      <span className="text-xs font-medium text-amber-900">Allow snooze</span>
                    </label>
                  </div>
                )}
              </div>

              <div className="rounded-xl border border-dashed border-emerald-200 bg-emerald-50/60 p-4 space-y-2">
                <h4 className="text-xs font-semibold tracking-wide text-emerald-800 uppercase">
                  Tracker (coming soon)
                </h4>
                <p className="text-xs text-emerald-700/90">
                  Soon you&apos;ll be able to measure numbers, habits, or anything else that proves this is working.
                </p>
              </div>

              <div className="rounded-xl border border-dashed border-indigo-200 bg-indigo-50/60 p-4 space-y-2">
                <h4 className="text-xs font-semibold tracking-wide text-indigo-800 uppercase">
                  Web search &amp; ideas (coming soon)
                </h4>
                <p className="text-xs text-indigo-700/90">
                  Let Brainboard pull ideas, research, and examples for this mission automatically.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 mt-2 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="sm:w-auto w-full px-4 py-2.5 rounded-lg border border-slate-200 bg-white text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.title.trim()}
              className="sm:w-auto w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-sm font-semibold text-white shadow-md hover:from-blue-700 hover:to-purple-700 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {editMode ? 'Saving changes...' : 'Create mission'}
                </>
              ) : (
                <>
                  <Save size={16} />
                  {editMode ? 'Save mission' : 'Create mission'}
                </>
              )}
            </button>
          </div>
        </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default MissionForm;

