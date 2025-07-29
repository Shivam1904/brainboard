import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { TrendingUp, Target, Calendar, Plus, X, Save } from 'lucide-react';
import { TrackerDetailsAndActivityResponse, TrackerDetails, TrackerActivity } from '../../types';
import { dashboardService } from '../../services/dashboard';

interface SingleItemTrackerWidgetProps {
  onRemove: () => void;
  widget: {
    widget_ids: string[];
    daily_widget_id: string;
    widget_type: string;
    priority: string;
    reasoning: string;
    date: string;
    created_at: string;
  };
}

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

const getProgressColor = (percentage: number) => {
  if (percentage >= 80) return 'bg-green-500';
  if (percentage >= 60) return 'bg-blue-500';
  if (percentage >= 40) return 'bg-yellow-500';
  return 'bg-red-500';
};

const SingleItemTrackerWidget = ({ onRemove, widget }: SingleItemTrackerWidgetProps) => {
  const [trackerData, setTrackerData] = useState<TrackerDetailsAndActivityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newValue, setNewValue] = useState('');
  const [notes, setNotes] = useState('');

  const fetchTracker = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get the widget_id from the widget_ids array (first one for singleitemtracker widgets)
      const widgetId = widget.widget_ids[0];
      
      // Call the real API
      const response = await dashboardService.getTrackerDetailsAndActivity(widgetId);
      setTrackerData(response);
    } catch (err) {
      console.error('Failed to fetch tracker:', err);
      setError('Failed to load tracker data');
      // Fallback to empty state
      setTrackerData(null);
    } finally {
      setLoading(false);
    }
  };

  const updateValue = async () => {
    if (!trackerData || !newValue.trim()) return;
    
    try {
      // Update tracker activity using the real API
      await dashboardService.updateTrackerActivity(trackerData.activity.id, {
        value: newValue,
        time_added: new Date().toISOString(),
        updated_by: 'user'
      });
      
      // Refresh tracker data
      await fetchTracker();
      setNewValue('');
      setNotes('');
      setShowAddForm(false);
    } catch (err) {
      console.error('Failed to update value:', err);
      // Still update local state even if API fails
      if (trackerData) {
        const updatedTrackerData = {
          ...trackerData,
          activity: {
            ...trackerData.activity,
            value: newValue,
            time_added: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        };
        setTrackerData(updatedTrackerData);
        setNewValue('');
        setNotes('');
        setShowAddForm(false);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateValue();
  };

  useEffect(() => {
    fetchTracker();
  }, []);

  if (loading) {
    return (
      <BaseWidget title="Item Tracker" icon="📈" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error && !trackerData) {
    return (
      <BaseWidget title="Item Tracker" icon="📈" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-orange-600 mb-2">{error}</p>
          <button 
            onClick={fetchTracker}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  if (!trackerData) {
    return (
      <BaseWidget title="Item Tracker" icon="📈" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32 text-center">
          <p className="text-gray-500">No tracker found for this widget</p>
        </div>
      </BaseWidget>
    );
  }

  const progressPercentage = trackerData.tracker_details.target_value && trackerData.activity.value 
    ? Math.min((parseFloat(trackerData.activity.value) / parseFloat(trackerData.tracker_details.target_value)) * 100, 100)
    : null;

  return (
    <BaseWidget title={trackerData.tracker_details.title} icon="📈" onRemove={onRemove}>
      <div className="p-4 h-full overflow-y-auto">
        {/* Offline Indicator */}
        {error && (
          <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-xs text-orange-700 text-center">{error}</p>
          </div>
        )}
        


        {/* Current Value Display */}
        <div className="mb-4 text-center">
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {trackerData.activity.value || '0'}
            {trackerData.tracker_details.value_unit && <span className="text-lg text-gray-600 ml-1">{trackerData.tracker_details.value_unit}</span>}
          </div>
          <p className="text-sm text-gray-600">Current Value</p>
        </div>

        {/* Target and Progress */}
        {trackerData.tracker_details.target_value && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Target</span>
              </div>
              <span className="text-sm text-gray-600">
                {trackerData.tracker_details.target_value}{trackerData.tracker_details.value_unit}
              </span>
            </div>
            
            {progressPercentage !== null && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${getProgressColor(progressPercentage)}`}
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            )}
          </div>
        )}

        {/* Recent Entries */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Entries</h4>
          <div className="text-center py-4 text-gray-500">
            <p className="text-sm">No entries yet</p>
            <p className="text-xs">Add your first value to get started!</p>
          </div>
        </div>

        {/* Add Value Button */}
        <div className="mt-4">
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Value
          </button>
        </div>

        {/* Add Value Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-xl">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-bold">Add New Value</h3>
                    <p className="text-blue-100 mt-1">Track your progress for {trackerData.tracker_details.title}</p>
                  </div>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="text-white hover:text-blue-100 p-2 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              {/* Form Content */}
              <div className="p-6">
                <div className="space-y-4">
                  {/* Value Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Value {trackerData.tracker_details.value_unit && `(${trackerData.tracker_details.value_unit})`}
                    </label>
                    <input
                      type={getValueTypeInput(trackerData.tracker_details.value_type)}
                      value={newValue}
                      onChange={(e) => setNewValue(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={`Enter ${trackerData.tracker_details.title.toLowerCase()} value`}
                      required
                    />
                  </div>
                  
                  {/* Notes Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes (Optional)
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Add any notes about this entry..."
                      rows={3}
                    />
                  </div>
                </div>
              </div>
              
              {/* Footer */}
              <div className="bg-gray-50 p-6 rounded-b-xl">
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 hover:border-gray-400 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={updateValue}
                    disabled={!newValue.trim()}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Value
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </BaseWidget>
  );
};

export default SingleItemTrackerWidget; 