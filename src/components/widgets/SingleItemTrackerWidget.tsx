import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { TrendingUp, Target, Calendar, Plus, X, Save } from 'lucide-react';
import { buildApiUrl, apiCall, API_CONFIG } from '../../config/api';
import { SingleItemTrackerWidgetDataResponse, SingleItemTrackerResponse, SingleItemTrackerLog } from '../../types/widgets';
import { Widget } from '../../utils/dashboardUtils';

interface SingleItemTrackerWidgetProps {
  onRemove: () => void;
  widget: Widget;
}

import { getDummyTracker } from '../../data/widgetDummyData';

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
  const [widgetData, setWidgetData] = useState<SingleItemTrackerWidgetDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newValue, setNewValue] = useState('');
  const [notes, setNotes] = useState('');

  const fetchTracker = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const widgetId = widget.daily_widget_id;
      
      // Get the tracker data for this widget
      const response = await apiCall<SingleItemTrackerWidgetDataResponse>(
        buildApiUrl(API_CONFIG.singleItemTracker.getWidgetData.replace('{widget_id}', widgetId))
      );
      
      setWidgetData(response);
    } catch (err) {
      console.error('Error fetching tracker:', err);
      // Fallback to dummy data on error
      const widgetId = widget.daily_widget_id;
      const dummyTracker = getDummyTracker(widgetId);
      setWidgetData(dummyTracker);
      setError('Using offline data - API unavailable');
    } finally {
      setLoading(false);
    }
  };

  const updateValue = async () => {
    if (!widgetData || !newValue.trim()) return;
    
    try {
      const response = await apiCall<SingleItemTrackerResponse>(
        buildApiUrl(API_CONFIG.singleItemTracker.updateValue.replace('{tracker_id}', widgetData.tracker.id)),
        {
          method: 'PUT',
          body: JSON.stringify({
            value: newValue,
            notes: notes.trim() || undefined
          })
        }
      );
      
      // Update local state
      const updatedWidgetData = {
        ...widgetData,
        tracker: response,
        stats: {
          ...widgetData.stats,
          current_value: newValue
        }
      };
      setWidgetData(updatedWidgetData);
      setNewValue('');
      setNotes('');
      setShowAddForm(false);
    } catch (err) {
      console.error('Error updating value:', err);
      // Still update local state even if API fails
      if (widgetData) {
        const updatedWidgetData = {
          ...widgetData,
          tracker: {
            ...widgetData.tracker,
            current_value: newValue,
            updated_at: new Date().toISOString()
          },
          stats: {
            ...widgetData.stats,
            current_value: newValue
          },
          recent_logs: [
            {
              id: Date.now().toString(),
              value: newValue,
              date: new Date().toISOString().split('T')[0],
              notes: notes.trim() || undefined,
              created_at: new Date().toISOString()
            },
            ...widgetData.recent_logs.slice(0, 4) // Keep only 5 most recent
          ]
        };
        setWidgetData(updatedWidgetData);
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

  if (error && !widgetData) {
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

  if (!widgetData) {
    return (
      <BaseWidget title="Item Tracker" icon="📈" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32 text-center">
          <p className="text-gray-500">No tracker found for this widget</p>
        </div>
      </BaseWidget>
    );
  }

  const progressPercentage = widgetData.tracker.target_value && widgetData.tracker.current_value 
    ? Math.min((parseFloat(widgetData.tracker.current_value) / parseFloat(widgetData.tracker.target_value)) * 100, 100)
    : null;

  return (
    <BaseWidget title={widget.widgetData.title} icon="📈" onRemove={onRemove}>
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
            {widgetData.tracker.current_value || '0'}
            {widgetData.tracker.item_unit && <span className="text-lg text-gray-600 ml-1">{widgetData.tracker.item_unit}</span>}
          </div>
          <p className="text-sm text-gray-600">Current Value</p>
        </div>

        {/* Target and Progress */}
        {widgetData.tracker.target_value && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target size={16} className="text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Target</span>
              </div>
              <span className="text-sm text-gray-600">
                {widgetData.tracker.target_value}{widgetData.tracker.item_unit}
              </span>
            </div>
            {progressPercentage !== null && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(progressPercentage)}`}
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            )}
          </div>
        )}

        {/* Add Value Button */}
        <div className="mb-4">
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={16} />
            Add New Value
          </button>
        </div>

        {/* Recent Logs */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Entries</h4>
          {widgetData.recent_logs.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <p className="text-sm">No entries yet</p>
              <p className="text-xs">Add your first value to get started!</p>
            </div>
          ) : (
            widgetData.recent_logs.map((log: SingleItemTrackerLog) => (
              <div 
                key={log.id} 
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">
                      {log.value}{widgetData.tracker.item_unit}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(log.date).toLocaleDateString()}
                    </span>
                  </div>
                  {log.notes && (
                    <p className="text-xs text-gray-600 mt-1">{log.notes}</p>
                  )}
                </div>
                <TrendingUp size={14} className="text-green-600" />
              </div>
            ))
          )}
        </div>
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
                  <p className="text-blue-100 mt-1">Track your progress for {widgetData.tracker.item_name}</p>
                </div>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-white hover:text-blue-100 p-2 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
            
            {/* Form Content */}
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Value Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Value {widgetData.tracker.item_unit && `(${widgetData.tracker.item_unit})`}
                  </label>
                  <input
                    type={getValueTypeInput(widgetData.tracker.value_type)}
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={`Enter ${widgetData.tracker.item_name.toLowerCase()} value`}
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
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    placeholder="Add any notes about this entry..."
                    rows={3}
                  />
                </div>
              </form>
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
                  onClick={handleSubmit}
                  disabled={!newValue.trim()}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  <Save size={16} />
                  Save Value
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </BaseWidget>
  );
};

export default SingleItemTrackerWidget; 