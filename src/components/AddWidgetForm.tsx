import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Save, Loader2 } from 'lucide-react';
import { getWidgetConfig } from '../config/widgets';
import { ApiWidgetType, ApiFrequency, ApiCategory } from '../types/widgets';
import { dashboardService } from '../services/dashboard';
import FrequencySection from './widgets/FrequencySection';
import { FrequencySettings } from '../types/frequency';
import { DashboardWidget } from '@/services/api';

interface AddWidgetFormProps {
  widgetId: string;
  onClose: () => void;
  onSuccess: () => void;
  editMode?: boolean;
  existingWidget?: DashboardWidget;
}

interface FormData {
  // Common fields
  title: string;
  frequency_details: FrequencySettings;
  importance: number;
  category: ApiCategory;
  description?: string;
  is_permanent: boolean;

  // All widget configuration fields (will be stored in widget_config)
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

    // Any other fields can be added here
    [key: string]: any;
  };
}

const AddWidgetForm = ({ widgetId, onClose, onSuccess, editMode = false, existingWidget }: AddWidgetFormProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [calendars, setCalendars] = useState<DashboardWidget[]>([]);
  const [showNewCalendarInput, setShowNewCalendarInput] = useState(false);
  const [newCalendarTitle, setNewCalendarTitle] = useState('');
  const [creatingCalendar, setCreatingCalendar] = useState(false);
  const widgetConfig = getWidgetConfig(widgetId);

  // Initialize form data with existing widget data if in edit mode
  const getInitialFormData = (): FormData => {
    if (editMode && existingWidget) {
      const saved = existingWidget.frequency_details as FrequencySettings | undefined;
      const hasValidFrequencyDetails = saved && typeof saved.frequencyPeriod === 'string' && typeof saved.frequency === 'number';
      return {
        title: existingWidget.title,
        description: existingWidget.description,
        is_permanent: existingWidget.is_permanent || false,
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
          streak_type: existingWidget.widget_config?.streak_type || 'none',
          streak_count: existingWidget.widget_config?.streak_count || 1,
          milestones: existingWidget.widget_config?.milestones || [],
          include_progress_details: existingWidget.widget_config?.include_progress_details ?? false,
          selected_calendar: existingWidget.widget_config?.selected_calendar || '',
          include_alarm_details: existingWidget.widget_config?.include_alarm_details ?? false,
          include_tracker_details: existingWidget.widget_config?.include_tracker_details ?? false,
          include_websearch_details: existingWidget.widget_config?.include_websearch_details ?? false
        }
      };
    }

    return {
      title: widgetConfig?.apiWidgetType === 'calendar' ? 'My Calendar' :
        widgetConfig?.apiWidgetType === 'yearCalendar' ? 'Yearly progress' :
          widgetConfig?.apiWidgetType === 'pillarsGraph' ? 'Pillars Graph' :
            widgetConfig?.apiWidgetType === 'habitTracker' ? 'Habit Tracker' :
              widgetConfig?.apiWidgetType === 'allSchedules' ? 'My Schedules' :
                widgetConfig?.apiWidgetType === 'aiChat' ? 'Brainy AI' : '',
      description: '',
      is_permanent: ['calendar', 'allSchedules', 'aiChat', 'yearCalendar', 'pillarsGraph', 'habitTracker'].includes(widgetConfig?.apiWidgetType as string) ? true : false,
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
        alarm_times: ['09:00'],
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

  // Fetch calendars on component mount
  useEffect(() => {
    const fetchCalendars = async () => {
      try {
        const calendarWidgets = await dashboardService.getWidgetsByType('calendar');
        setCalendars(calendarWidgets);
      } catch (err) {
        console.error('Failed to fetch calendars:', err);
      }
    };

    fetchCalendars();
  }, []);

  // Function to create a new calendar
  const createNewCalendar = async () => {
    if (!newCalendarTitle.trim()) return;

    setCreatingCalendar(true);
    try {
      const newCalendar = await dashboardService.createWidget({
        widget_type: 'calendar',
        title: newCalendarTitle.trim(),
        description: '',
        frequency: 'daily',
        importance: 0.7,
        category: 'productivity',
        is_permanent: true,
        widget_config: {}
      });

      setCalendars(prev => [...prev, newCalendar]);
      updateWidgetConfig('selected_calendar', newCalendar.id);
      setNewCalendarTitle('');
      setShowNewCalendarInput(false);
      onSuccess(); // Refresh the dashboard to show the new calendar
    } catch (err) {
      console.error('Failed to create calendar:', err);
      setError('Failed to create calendar. Please try again.');
    } finally {
      setCreatingCalendar(false);
    }
  };

  if (!widgetConfig) {
    return null;
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'productivity': return 'bg-blue-100 text-blue-800';
      case 'health': return 'bg-green-100 text-green-800';
      case 'work': return 'bg-purple-100 text-purple-800';
      case 'research': return 'bg-yellow-100 text-yellow-800';
      case 'entertainment': return 'bg-pink-100 text-pink-800';
      case 'utilities': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
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
      // Convert frequency settings to API format
      const apiFrequency: ApiFrequency = formData.frequency_details.frequencyPeriod === 'DAILY' ? 'daily' :
        formData.frequency_details.frequencyPeriod === 'WEEKLY' ? 'weekly' : 'monthly';

      // Prepare API data with common fields and widget_config (include full frequency_details for persistence)
      const apiData = {
        widget_type: widgetConfig.apiWidgetType as ApiWidgetType,
        title: formData.title.trim(),
        description: formData.description?.trim(),
        frequency: apiFrequency,
        frequency_details: formData.frequency_details as unknown as Record<string, any>,
        importance: formData.importance,
        category: formData.category,
        is_permanent: formData.is_permanent,
        widget_config: formData.widgetConfig
      };

      let response;
      if (editMode && existingWidget) {
        // Update existing widget
        response = await dashboardService.updateWidget(existingWidget.id, apiData);
        console.log('Widget updated successfully:', response);
      } else {
        // Create new widget
        response = await dashboardService.createWidget(apiData);
        console.log('Widget created successfully:', response);
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

  // Update widget configuration
  const updateWidgetConfig = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      widgetConfig: {
        ...prev.widgetConfig,
        [key]: value
      }
    }));
  };

  const modalContent = (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" aria-modal="true">
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
        style={{ position: 'fixed', left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-2xl font-bold">{editMode ? 'Edit Widget' : 'Add New Widget'}</h3>
              <p className="text-blue-100 mt-1">{widgetConfig.title} - {widgetConfig.description}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-blue-100 p-2 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Form Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {/* Basic Information Section */}
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
              <h4 className="text-lg font-bold text-gray-800 mb-4">Basic Information</h4>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Widget Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter widget title..."
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={formData.description || ''}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter widget description..."
                    rows={2}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">
                    Permanent Widget
                  </label>
                  <input
                    type="checkbox"
                    checked={formData.is_permanent}
                    onChange={(e) => setFormData({ ...formData, is_permanent: e.target.checked })}
                    className="rounded"
                  />
                </div>
              </div>
            </div>

            {/* Category Section */}
            {!formData.is_permanent && (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4">Category</h4>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'productivity', label: 'Productivity', color: 'bg-gradient-to-r from-blue-500 to-blue-600' },
                    { value: 'health', label: 'Health', color: 'bg-red-500' },
                    { value: 'work', label: 'Work', color: 'bg-gradient-to-r from-purple-500 to-purple-600' },
                    { value: 'research', label: 'Research', color: 'bg-gradient-to-r from-yellow-500 to-yellow-600' },
                    { value: 'entertainment', label: 'Entertainment', color: 'bg-gradient-to-r from-pink-500 to-pink-600' },
                    { value: 'utilities', label: 'Utilities', color: 'bg-gradient-to-r from-gray-500 to-gray-600' }
                  ].map((category) => (
                    <button
                      key={category.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, category: category.value as ApiCategory })}
                      className={`px-3 py-2 rounded-lg font-medium transition-all ${formData.category === category.value
                        ? `${category.color} text-white shadow-lg transform scale-105`
                        : 'bg-white/70 text-gray-700 hover:bg-gray-100 hover:scale-102'
                        }`}
                    >
                      {category.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Frequency Section */}
            {!formData.is_permanent && (
              <div className="bg-gradient-to-r from-teal-50 to-cyan-50 p-4 rounded-lg border border-teal-200">
                <h4 className="text-lg font-bold text-gray-800 mb-4">Frequency</h4>
                <FrequencySection
                  frequency={formData.frequency_details}
                  onChange={(frequency) => setFormData({ ...formData, frequency_details: frequency })}
                  pillarColor={getCategoryColor(formData.category)}
                />
              </div>
            )}
            {widgetConfig.apiWidgetType !== 'calendar'
              && widgetConfig.apiWidgetType !== 'allSchedules'
              && widgetConfig.apiWidgetType !== 'yearCalendar'
              && widgetConfig.apiWidgetType !== 'habitTracker'
              && widgetConfig.apiWidgetType !== 'pillarsGraph' && (
                <div className="">

                  <div className="bg-gradient-to-r from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">Progress Configuration</h4>

                    {/* Confirmation Question */}
                    <div className="mb-4 p-3 bg-orange-100 rounded-lg border border-orange-300">
                      <p className="text-sm font-medium text-orange-800 mb-2">Do you want to add it to your calendar?</p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_progress_details', true)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${formData.widgetConfig.include_progress_details
                            ? 'bg-orange-600 text-white shadow-lg'
                            : 'bg-white text-orange-700 hover:bg-orange-200'
                            }`}
                        >
                          Yes, add to calendar
                        </button>
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_progress_details', false)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!formData.widgetConfig.include_progress_details
                            ? 'bg-gray-600 text-white shadow-lg'
                            : 'bg-white text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                          No, skip calendar
                        </button>
                      </div>
                    </div>

                    {/* Progress Details (only show if user wants to include them) */}
                    {formData.widgetConfig.include_progress_details && (
                      <div className="space-y-4">
                        {/* Calendar Selection */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select Calendar
                          </label>
                          <select
                            value={formData.widgetConfig.selected_calendar || ''}
                            onChange={(e) => {
                              if (e.target.value === 'new') {
                                setShowNewCalendarInput(true);
                              } else {
                                updateWidgetConfig('selected_calendar', e.target.value);
                              }
                            }}
                            className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          >
                            <option value="">Select a calendar...</option>
                            {calendars.map((calendar) => (
                              <option key={calendar.id} value={calendar.id}>
                                {calendar.title}
                              </option>
                            ))}
                            <option value="new">+ Add New Calendar</option>
                          </select>
                        </div>

                        {/* New Calendar Input */}
                        {showNewCalendarInput && (
                          <div className="p-3 bg-white/50 rounded-lg border border-orange-200">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              New Calendar Title
                            </label>
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={newCalendarTitle}
                                onChange={(e) => setNewCalendarTitle(e.target.value)}
                                placeholder="Enter calendar title..."
                                className="flex-1 px-3 py-2 bg-white/70 border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                              />
                              <button
                                type="button"
                                onClick={createNewCalendar}
                                disabled={creatingCalendar || !newCalendarTitle.trim()}
                                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                {creatingCalendar ? 'Creating...' : 'Create'}
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  setShowNewCalendarInput(false);
                                  setNewCalendarTitle('');
                                }}
                                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}

                        {/* Maintain Streak Dropdown */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Maintain Streak
                          </label>
                          <select
                            value={formData.widgetConfig.streak_type || 'none'}
                            onChange={(e) => updateWidgetConfig('streak_type', e.target.value)}
                            className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          >
                            <option value="none">None</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                          </select>
                        </div>

                        {/* Streak Count (only show if streak type is selected) */}
                        {formData.widgetConfig.streak_type && formData.widgetConfig.streak_type !== 'none' && (
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              How many {formData.widgetConfig.streak_type}?
                            </label>
                            <input
                              type="number"
                              min="1"
                              value={formData.widgetConfig.streak_count || 1}
                              onChange={(e) => updateWidgetConfig('streak_count', parseInt(e.target.value) || 1)}
                              className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                            />
                          </div>
                        )}

                        {/* Milestones Section */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Milestones
                          </label>
                          <div className="space-y-3">
                            {(formData.widgetConfig.milestones || []).map((milestone: any, index: number) => (
                              <div key={index} className="flex items-center space-x-2 p-3 bg-white/50 rounded-lg border border-orange-200">
                                <div className="flex-1">
                                  <input
                                    type="text"
                                    value={milestone.text || ''}
                                    onChange={(e) => {
                                      const newMilestones = [...(formData.widgetConfig.milestones || [])];
                                      newMilestones[index] = { ...newMilestones[index], text: e.target.value };
                                      updateWidgetConfig('milestones', newMilestones);
                                    }}
                                    className="w-full px-3 py-2 bg-white/70 border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent mb-2"
                                    placeholder="Milestone description..."
                                  />
                                  <input
                                    type="date"
                                    value={milestone.due_date || ''}
                                    onChange={(e) => {
                                      const newMilestones = [...(formData.widgetConfig.milestones || [])];
                                      newMilestones[index] = { ...newMilestones[index], due_date: e.target.value };
                                      updateWidgetConfig('milestones', newMilestones);
                                    }}
                                    className="w-full px-3 py-2 bg-white/70 border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                                  />
                                </div>
                                <button
                                  type="button"
                                  onClick={() => {
                                    const newMilestones = (formData.widgetConfig.milestones || []).filter((_: any, i: number) => i !== index);
                                    updateWidgetConfig('milestones', newMilestones);
                                  }}
                                  className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                                >
                                  ×
                                </button>
                              </div>
                            ))}
                            <button
                              type="button"
                              onClick={() => {
                                const newMilestones = [...(formData.widgetConfig.milestones || []), { text: '', due_date: '' }];
                                updateWidgetConfig('milestones', newMilestones);
                              }}
                              className="w-full px-4 py-2 bg-orange-100 text-orange-800 rounded-lg hover:bg-orange-200 transition-colors"
                            >
                              + Add Milestone
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-200">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">Alarm Configuration</h4>

                    {/* Confirmation Question */}
                    <div className="mb-4 p-3 bg-yellow-100 rounded-lg border border-yellow-300">
                      <p className="text-sm font-medium text-yellow-800 mb-2">Would you like to add alarm details?</p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_alarm_details', true)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${formData.widgetConfig.include_alarm_details
                            ? 'bg-yellow-600 text-white shadow-lg'
                            : 'bg-white text-yellow-700 hover:bg-yellow-200'
                            }`}
                        >
                          Yes, add alarm details
                        </button>
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_alarm_details', false)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!formData.widgetConfig.include_alarm_details
                            ? 'bg-gray-600 text-white shadow-lg'
                            : 'bg-white text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                          No, skip alarm details
                        </button>
                      </div>
                    </div>

                    {/* Alarm Details (only show if user wants to include them) */}
                    {formData.widgetConfig.include_alarm_details && (
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Alarm Times
                          </label>
                          <div className="space-y-2">
                            {(formData.widgetConfig.alarm_times || ['09:00']).map((time: string, index: number) => (
                              <div key={index} className="flex items-center space-x-2">
                                <input
                                  type="time"
                                  value={time}
                                  onChange={(e) => {
                                    const newTimes = [...(formData.widgetConfig.alarm_times || ['09:00'])];
                                    newTimes[index] = e.target.value;
                                    updateWidgetConfig('alarm_times', newTimes);
                                  }}
                                  className="flex-1 px-4 py-3 bg-white/70 backdrop-blur-sm border border-yellow-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                                />
                                {(formData.widgetConfig.alarm_times || ['09:00']).length > 1 && (
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const newTimes = (formData.widgetConfig.alarm_times || ['09:00']).filter((_: any, i: number) => i !== index);
                                      updateWidgetConfig('alarm_times', newTimes);
                                    }}
                                    className="px-3 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600"
                                  >
                                    ×
                                  </button>
                                )}
                              </div>
                            ))}
                            <button
                              type="button"
                              onClick={() => {
                                const newTimes = [...(formData.widgetConfig.alarm_times || ['09:00']), '09:00'];
                                updateWidgetConfig('alarm_times', newTimes);
                              }}
                              className="w-full px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200"
                            >
                              + Add Another Alarm
                            </button>
                          </div>
                        </div>

                        <div>
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={formData.widgetConfig.is_snoozable !== false}
                              onChange={(e) => updateWidgetConfig('is_snoozable', e.target.checked)}
                              className="rounded"
                            />
                            <span className="text-sm font-medium text-gray-700">Allow snooze</span>
                          </label>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">Tracker Configuration</h4>

                    {/* Confirmation Question */}
                    <div className="mb-4 p-3 bg-green-100 rounded-lg border border-green-300">
                      <p className="text-sm font-medium text-green-800 mb-2">Would you like to add tracker details?</p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_tracker_details', true)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${formData.widgetConfig.include_tracker_details
                            ? 'bg-green-600 text-white shadow-lg'
                            : 'bg-white text-green-700 hover:bg-green-200'
                            }`}
                        >
                          Yes, add tracker details
                        </button>
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_tracker_details', false)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!formData.widgetConfig.include_tracker_details
                            ? 'bg-gray-600 text-white shadow-lg'
                            : 'bg-white text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                          No, skip tracker details
                        </button>
                      </div>
                    </div>

                    {/* Tracker Details (only show if user wants to include them) */}
                    {formData.widgetConfig.include_tracker_details && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Value Type
                          </label>
                          <select
                            value={formData.widgetConfig.value_type || 'number'}
                            onChange={(e) => updateWidgetConfig('value_type', e.target.value)}
                            className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          >
                            <option value="number">Number</option>
                            <option value="text">Text</option>
                            <option value="boolean">Boolean</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Value Unit
                          </label>
                          <input
                            type="text"
                            value={formData.widgetConfig.value_unit || ''}
                            onChange={(e) => updateWidgetConfig('value_unit', e.target.value)}
                            className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="e.g., kg, ml, steps"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Target Value
                          </label>
                          <input
                            type="text"
                            value={formData.widgetConfig.target_value || ''}
                            onChange={(e) => updateWidgetConfig('target_value', e.target.value)}
                            className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="e.g., 70, 8 glasses"
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">Web Search Configuration</h4>

                    {/* Confirmation Question */}
                    <div className="mb-4 p-3 bg-purple-100 rounded-lg border border-purple-300">
                      <p className="text-sm font-medium text-purple-800 mb-2">Would you like to add web search details?</p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_websearch_details', true)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${formData.widgetConfig.include_websearch_details
                            ? 'bg-purple-600 text-white shadow-lg'
                            : 'bg-white text-purple-700 hover:bg-purple-200'
                            }`}
                        >
                          Yes, add web search details
                        </button>
                        <button
                          type="button"
                          onClick={() => updateWidgetConfig('include_websearch_details', false)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!formData.widgetConfig.include_websearch_details
                            ? 'bg-gray-600 text-white shadow-lg'
                            : 'bg-white text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                          No, skip web search details
                        </button>
                      </div>
                    </div>

                    {/* Web Search Details (only show if user wants to include them) */}
                    {formData.widgetConfig.include_websearch_details && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Search Query
                        </label>
                        <textarea
                          value={formData.widgetConfig.search_query_detailed || ''}
                          onChange={(e) => updateWidgetConfig('search_query_detailed', e.target.value)}
                          className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Enter your search query..."
                          rows={3}
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}



            {/* Form Buttons */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 border-t border-gray-200 -mx-6 -mb-6">
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 hover:border-gray-400 transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.title.trim()}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all shadow-lg disabled:opacity-50 disabled:transform-none flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      {editMode ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      {editMode ? 'Update Widget' : 'Create Widget'}
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default AddWidgetForm; 