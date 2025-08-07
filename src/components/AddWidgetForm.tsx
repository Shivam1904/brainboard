import { useState } from 'react';
import { X, Save, Loader2 } from 'lucide-react';
import { getWidgetConfig } from '../config/widgets';
import { ApiWidgetType, ApiFrequency, ApiCategory } from '../types';
import { dashboardService } from '../services/dashboard';
import FrequencySection from './widgets/FrequencySection';
import { FrequencySettings } from '../types/frequency';

interface AddWidgetFormProps {
  widgetId: string;
  onClose: () => void;
  onSuccess: () => void;
  editMode?: boolean;
  existingWidget?: {
    id: string;
    title: string;
    widget_type: string;
    frequency: string;
    importance: number;
    category: string;
    is_permanent?: boolean;
    // Widget-specific fields that come from API calls
    todo_type?: string;
    due_date?: string;
    description?: string;
    alarm_times?: string[];
    target_value?: string;
    is_snoozable?: boolean;
    value_type?: string;
    value_unit?: string;
  };
}

interface FormData {
  // Common fields
  title: string;
  frequency: FrequencySettings;
  importance: number;
  category: ApiCategory;
  is_permanent: boolean;
  
  // Todo-specific fields
  todoType?: 'habit' | 'task' | 'event';
  dueDate?: string;
  
  // Alarm-specific fields
  alarmTime?: string;
  
  // Single item tracker-specific fields
  valueDataType?: string;
  valueDataUnit?: string;
  targetValue?: string;
}

const AddWidgetForm = ({ widgetId, onClose, onSuccess, editMode = false, existingWidget }: AddWidgetFormProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const widgetConfig = getWidgetConfig(widgetId);
  
  // Initialize form data with existing widget data if in edit mode
  const getInitialFormData = (): FormData => {
    
    if (editMode && existingWidget) {
      return {
        title: existingWidget.title,
        is_permanent: existingWidget.is_permanent || false,
        frequency: {
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
        todoType: existingWidget.todo_type as 'habit' | 'task' | 'event',
        dueDate: existingWidget.due_date || new Date().toISOString().split('T')[0],
        alarmTime: existingWidget.alarm_times?.[0] || '09:00', // Use first alarm time
        valueDataType: existingWidget.value_type || 'number',
        valueDataUnit: existingWidget.value_unit || 'units',
        targetValue: existingWidget.target_value || ''
      };
    }
    
    return {
      title: 'calendar'==widgetConfig?.apiWidgetType  ? 'My Calendar' : 'allSchedules'==widgetConfig?.apiWidgetType  ? 'My Schedules' : 'aiChat'==widgetConfig?.apiWidgetType  ? 'Brainy AI' : '',
      is_permanent: ['calendar', 'allSchedules', 'aiChat'].includes(widgetConfig?.apiWidgetType as string) ? true : false,
      frequency: {
        frequencySet: 'BALANCED',
        frequencySetValue: 0.6,
        frequency: 3,
        frequencyUnit: 'TIMES',
        frequencyPeriod: 'WEEKLY',
        isDailyHabit: false
      },
      importance: 0.7,
      category: 'productivity',
      todoType: widgetConfig?.apiWidgetType =='todo-event' ? 'event' : widgetConfig?.apiWidgetType =='todo-task' ? 'task' : 'habit',
      dueDate: new Date().toISOString().split('T')[0],
      alarmTime: '09:00',
      valueDataType: 'number',
      valueDataUnit: 'units',
      targetValue: ''
    };
  };
  
  const [formData, setFormData] = useState<FormData>(getInitialFormData());

  if (!widgetConfig) {
    return null;
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'productivity': return 'bg-blue-100 text-blue-800';
      case 'health': return 'bg-green-100 text-green-800';
      case 'job': return 'bg-purple-100 text-purple-800';
      case 'information': return 'bg-yellow-100 text-yellow-800';
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
      const apiFrequency: ApiFrequency = formData.frequency.frequencyPeriod === 'DAILY' ? 'daily' : 
                                       formData.frequency.frequencyPeriod === 'WEEKLY' ? 'weekly' : 'monthly';

      // Prepare API data with widget-specific fields
      const apiData: any = {
        widget_type: widgetConfig.apiWidgetType as ApiWidgetType,
        frequency: apiFrequency,
        importance: formData.importance,
        title: formData.title.trim(),
        category: formData.category
      };

      // Add widget-specific fields based on widget type
      if (widgetConfig.apiWidgetType.startsWith('todo-')) {
        apiData.todo_type = formData.todoType;
        apiData.due_date = formData.dueDate;
      } else if (widgetConfig.apiWidgetType === 'alarm') {
        apiData.alarm_time = formData.alarmTime;
      } else if (widgetConfig.apiWidgetType === 'singleitemtracker') {
        apiData.value_data_type = formData.valueDataType;
        apiData.value_data_unit = formData.valueDataUnit;
        apiData.target_value = formData.targetValue;
      }

      let response;
      if (editMode && existingWidget) {
        // Update existing widget
        if (widgetConfig.apiWidgetType === 'singleitemtracker') {
          // For SingleItemTracker, we need to update both basic widget properties and tracker details
          
          // First, update basic widget properties
          const basicWidgetData = {
            widget_type: widgetConfig.apiWidgetType as ApiWidgetType,
            frequency: apiFrequency,
            importance: formData.importance,
            title: formData.title.trim(),
            category: formData.category
          };
          
          const basicResponse = await dashboardService.updateWidget(existingWidget.id, basicWidgetData);
          console.log('Basic widget updated successfully:', basicResponse);
          
          // Then, update SingleItemTracker-specific details
          try {
            // Get the tracker details to get the tracker_details_id
            const trackerDetails = await dashboardService.getTrackerDetails(existingWidget.id);
            
            const trackerData = {
              title: formData.title.trim(),
              value_type: formData.valueDataType || 'number',
              value_unit: formData.valueDataUnit || 'units',
              target_value: formData.targetValue || ''
            };
            
            const trackerResponse = await dashboardService.updateSingleItemTrackerDetails(trackerDetails.id, trackerData);
            console.log('Tracker details updated successfully:', trackerResponse);
            
            response = { ...basicResponse, trackerDetails: trackerResponse };
          } catch (trackerError) {
            console.error('Failed to update tracker details:', trackerError);
            // Still return the basic widget update response
            response = basicResponse;
          }
        } else {
          // For other widget types, use the regular updateWidget method
          response = await dashboardService.updateWidget(existingWidget.id, apiData);
        }
        console.log('Widget updated successfully:', response);
      } else {
        // Create new widget
        response = await dashboardService.addNewWidget(apiData);
        console.log('Widget added successfully:', response);
      }
      
      onSuccess();
      onClose();
      
    } catch (err) {
      console.error(editMode ? 'Failed to update widget:' : 'Failed to add widget:', err);
      setError(editMode ? 'Failed to update widget. Please try again.' : 'Failed to add widget. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderTodoFields = () => {
    if (!widgetConfig.apiWidgetType.startsWith('todo-')) return null;

    return (
      <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-2 border border-orange-200">
        <label className="block text-lg font-bold text-gray-800 mb-3">
          TODO TYPE
        </label>
        <div className="grid grid-cols-3 gap-2 mb-4">
          {[
            { value: 'habit', label: 'Habit', icon: '🔄' },
            { value: 'task', label: 'Task', icon: '📋' },
            { value: 'event', label: 'Event', icon: '📅' }
          ].map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => setFormData({...formData, todoType: type.value as 'habit' | 'task' | 'event'})}
              className={`px-4 py-3 rounded-lg font-medium transition-all ${
                formData.todoType === type.value
                  ? 'bg-orange-500 text-white shadow-lg transform scale-105'
                  : 'bg-white/70 text-gray-700 hover:bg-orange-100 hover:scale-102'
              }`}
            >
              <div className="text-lg mb-1">{type.icon}</div>
              {type.label}
            </button>
          ))}
        </div>
        
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Due Date
        </label>
        <input
          type="date"
          value={formData.dueDate}
          onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
          className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
        />
      </div>
    );
  };

  const renderAlarmFields = () => {
    if (widgetConfig.apiWidgetType !== 'alarm') return null;

    return (
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-2 border border-yellow-200">
        <label className="block text-lg font-bold text-gray-800 mb-2">
          ALARM TIME
        </label>
        <input
          type="time"
          value={formData.alarmTime}
          onChange={(e) => setFormData({...formData, alarmTime: e.target.value})}
          className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-yellow-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent text-lg"
        />
      </div>
    );
  };

  const renderTrackerFields = () => {
    if (widgetConfig.apiWidgetType !== 'singleitemtracker') return null;

    return (
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-2 border border-green-200">
        <label className="block text-lg font-bold text-gray-800 mb-3">
          TRACKER SETTINGS
        </label>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Value Data Type
            </label>
            <select
              value={formData.valueDataType}
              onChange={(e) => setFormData({...formData, valueDataType: e.target.value})}
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
              value={formData.valueDataUnit}
              onChange={(e) => setFormData({...formData, valueDataUnit: e.target.value})}
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
              value={formData.targetValue}
              onChange={(e) => setFormData({...formData, targetValue: e.target.value})}
              className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., 70, 8 glasses"
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
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
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
            
            {/* Widget Title Section */}
            <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-2 border border-orange-200">
              <label className="block text-lg font-bold text-gray-800 mb-2">
                WIDGET TITLE
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-lg"
                placeholder={`Enter ${widgetConfig.title} title...`}
                required
              />
            </div>
            {/* Add a permanent widget checkbox */}
            {(<div className="flex justify-end gap-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-2 border border-purple-200">
              <label className="block text-lg font-bold text-gray-800">
                PERMANENT WIDGET
              </label>
              <input className="ml-2 " type="checkbox" checked={formData.is_permanent} onChange={(e) => setFormData({...formData, is_permanent: e.target.checked})} />
            </div>)}
            
            {/* Category Section */}
            {(!formData.is_permanent && <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-2 border border-green-200">
              <label className="block text-lg font-bold text-gray-800 mb-3">
                CATEGORY
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'productivity', label: 'Productivity', color: 'from-blue-500 to-blue-600' },
                  { value: 'health', label: 'Health', color: 'from-green-500 to-green-600' },
                  { value: 'job', label: 'Job', color: 'from-purple-500 to-purple-600' },
                  { value: 'information', label: 'Information', color: 'from-yellow-500 to-yellow-600' },
                  { value: 'entertainment', label: 'Entertainment', color: 'from-pink-500 to-pink-600' },
                  { value: 'utilities', label: 'Utilities', color: 'from-gray-500 to-gray-600' }
                ].map((category) => (
                  <button
                    key={category.value}
                    type="button"
                    onClick={() => setFormData({...formData, category: category.value as ApiCategory})}
                    className={`px-4 py-3 rounded-lg font-medium transition-all ${
                      formData.category === category.value
                        ? `bg-gradient-to-r ${category.color} text-white shadow-lg transform scale-105`
                        : 'bg-white/70 text-gray-700 hover:bg-gray-100 hover:scale-102'
                    }`}
                  >
                    {category.label}
                  </button>
                ))}
              </div>
            </div>)}
            
            {/* Importance Section */}
            {(!formData.is_permanent && <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-2 border border-purple-200">
              <label className="block text-lg font-bold text-gray-800 mb-3">
                IMPORTANCE LEVEL
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.importance}
                  onChange={(e) => setFormData({...formData, importance: parseFloat(e.target.value)})}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <span className="text-lg font-bold text-gray-700 min-w-[60px]">
                  {Math.round(formData.importance * 100)}%
                </span>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>)}
            
            {/* Frequency Section */}
            {(!formData.is_permanent && <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl p-2 border border-teal-200">
              <label className="block text-lg font-bold text-gray-800 mb-3">
                FREQUENCY
              </label>
              <FrequencySection
                frequency={formData.frequency}
                onChange={(frequency) => setFormData({...formData, frequency})}
                pillarColor={getCategoryColor(formData.category)}
              />
            </div>)}
            
            {/* Widget-specific fields */}
            {renderTodoFields()}
            {renderAlarmFields()}
            {renderTrackerFields()}
            
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
                      {editMode ? 'Updating...' : 'Adding...'}
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      {editMode ? 'Update Widget' : 'Add Widget'}
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
};

export default AddWidgetForm; 