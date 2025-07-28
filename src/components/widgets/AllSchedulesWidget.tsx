import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ScheduledItem } from '../../types/dashboard';

interface AllSchedulesWidgetProps {
  onRemove: () => void;
  config?: Record<string, any>;
}

interface EditFormData {
  id: string;
  title: string;
  type: string;
  frequency: string;
  category?: string;
  importance?: 'High' | 'Medium' | 'Low';
  alarm?: string;
  searchQuery?: string;
}

const AllSchedulesWidget = ({ onRemove }: AllSchedulesWidgetProps) => {
  const [scheduledItems, setScheduledItems] = useState<ScheduledItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingItem, setEditingItem] = useState<EditFormData | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // Load scheduled items
  useEffect(() => {
    const loadScheduledItems = async () => {
      try {
        setLoading(true);
        // In real implementation, fetch from API
        // const response = await fetch('/api/schedules');
        // const data = await response.json();
        
        // For now, use empty array since we removed the dummy data
        setScheduledItems([]);
      } catch (err) {
        console.error('Failed to load scheduled items:', err);
        setError('Failed to load schedules');
      } finally {
        setLoading(false);
      }
    };

    loadScheduledItems();
  }, []);

  // Handle item update
  const handleUpdateItem = async (updatedItem: EditFormData) => {
    try {
      // In real implementation, call API to update
      // await fetch(`/api/schedules/${updatedItem.id}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(updatedItem)
      // });

      // For now, update local state
      setScheduledItems(prev => 
        prev.map(item => 
          item.id === updatedItem.id 
            ? { ...item, ...updatedItem }
            : item
        )
      );
      setEditingItem(null);
    } catch (err) {
      console.error('Failed to update item:', err);
      setError('Failed to update schedule');
    }
  };

  // Handle item deletion
  const handleDeleteItem = async (itemId: string) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;

    try {
      // In real implementation, call API to delete
      // await fetch(`/api/schedules/${itemId}`, { method: 'DELETE' });

      // For now, update local state
      setScheduledItems(prev => prev.filter(item => item.id !== itemId));
    } catch (err) {
      console.error('Failed to delete item:', err);
      setError('Failed to delete schedule');
    }
  };

  // Handle item addition
  const handleAddItem = async (newItem: Omit<EditFormData, 'id'>) => {
    try {
      // In real implementation, call API to create
      // const response = await fetch('/api/schedules', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(newItem)
      // });
      // const createdItem = await response.json();

      // For now, add to local state
      const createdItem: ScheduledItem = {
        ...newItem,
        id: Date.now().toString()
      };
      setScheduledItems(prev => [...prev, createdItem]);
      setShowAddForm(false);
    } catch (err) {
      console.error('Failed to add item:', err);
      setError('Failed to add schedule');
    }
  };

  // Get widget type display name
  const getWidgetTypeDisplayName = (type: string): string => {
    const typeNames: Record<string, string> = {
      'userTask': 'Task',
      'userHabit': 'Habit',
      'itemTracker': 'Item Tracker',
      'webSearch': 'Web Search',
      'aiWebChart': 'Web Chart',
      'weatherWig': 'Weather',
      'calendar': 'Calendar',
      'alarm': 'Alarm',
      'statsWidget': 'Stats',
      'newsWidget': 'News'
    };
    return typeNames[type] || type;
  };

  // Get category color
  const getCategoryColor = (category?: string): string => {
    const colors: Record<string, string> = {
      'health': 'bg-red-100 text-red-800',
      'self-imp': 'bg-blue-100 text-blue-800',
      'finance': 'bg-green-100 text-green-800',
      'awareness': 'bg-purple-100 text-purple-800'
    };
    return colors[category || ''] || 'bg-gray-100 text-gray-800';
  };

  // Render edit form based on widget type
  const renderEditForm = (item: EditFormData) => {
    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      handleUpdateItem(item);
    };

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Edit Schedule</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Common fields */}
            <div>
              <label className="block text-sm font-medium mb-1">Title</label>
              <input
                type="text"
                value={item.title}
                onChange={(e) => setEditingItem({ ...item, title: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <select
                value={item.type}
                onChange={(e) => setEditingItem({ ...item, type: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              >
                <option value="userTask">Task</option>
                <option value="userHabit">Habit</option>
                <option value="itemTracker">Item Tracker</option>
                <option value="webSearch">Web Search</option>
                <option value="alarm">Alarm</option>
                <option value="calendar">Calendar</option>
                <option value="weatherWig">Weather</option>
                <option value="statsWidget">Stats</option>
                <option value="newsWidget">News</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Frequency</label>
              <input
                type="text"
                value={item.frequency}
                onChange={(e) => setEditingItem({ ...item, frequency: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="daily, weekly-2, hourly, etc."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <input
                type="text"
                value={item.category || ''}
                onChange={(e) => setEditingItem({ ...item, category: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="health, finance, etc."
              />
            </div>

            {/* Type-specific fields */}
            {item.type === 'webSearch' && (
              <div>
                <label className="block text-sm font-medium mb-1">Search Query</label>
                <input
                  type="text"
                  value={item.searchQuery || ''}
                  onChange={(e) => setEditingItem({ ...item, searchQuery: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Enter search query"
                  required
                />
              </div>
            )}

            {(item.type === 'userTask' || item.type === 'userHabit') && (
              <div>
                <label className="block text-sm font-medium mb-1">Importance</label>
                <select
                  value={item.importance || ''}
                  onChange={(e) => setEditingItem({ ...item, importance: e.target.value as any })}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Select importance</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            )}

            {(item.type === 'alarm' || item.type === 'userHabit') && (
              <div>
                <label className="block text-sm font-medium mb-1">Alarm</label>
                <input
                  type="text"
                  value={item.alarm || ''}
                  onChange={(e) => setEditingItem({ ...item, alarm: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="[7am], [every 2 hr], etc."
                />
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => setEditingItem(null)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Render add form
  const renderAddForm = () => {
    const [newItem, setNewItem] = useState<Omit<EditFormData, 'id'>>({
      title: '',
      type: 'userTask',
      frequency: 'daily',
      category: '',
      importance: undefined,
      alarm: '',
      searchQuery: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      handleAddItem(newItem);
    };

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Add New Schedule</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Title</label>
              <input
                type="text"
                value={newItem.title}
                onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <select
                value={newItem.type}
                onChange={(e) => setNewItem({ ...newItem, type: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              >
                <option value="userTask">Task</option>
                <option value="userHabit">Habit</option>
                <option value="itemTracker">Item Tracker</option>
                <option value="webSearch">Web Search</option>
                <option value="alarm">Alarm</option>
                <option value="calendar">Calendar</option>
                <option value="weatherWig">Weather</option>
                <option value="statsWidget">Stats</option>
                <option value="newsWidget">News</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Frequency</label>
              <input
                type="text"
                value={newItem.frequency}
                onChange={(e) => setNewItem({ ...newItem, frequency: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="daily, weekly-2, hourly, etc."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <input
                type="text"
                value={newItem.category}
                onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="health, finance, etc."
              />
            </div>

            {newItem.type === 'webSearch' && (
              <div>
                <label className="block text-sm font-medium mb-1">Search Query</label>
                <input
                  type="text"
                  value={newItem.searchQuery}
                  onChange={(e) => setNewItem({ ...newItem, searchQuery: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Enter search query"
                  required
                />
              </div>
            )}

            {(newItem.type === 'userTask' || newItem.type === 'userHabit') && (
              <div>
                <label className="block text-sm font-medium mb-1">Importance</label>
                <select
                  value={newItem.importance || ''}
                  onChange={(e) => setNewItem({ ...newItem, importance: e.target.value as any })}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Select importance</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            )}

            {(newItem.type === 'alarm' || newItem.type === 'userHabit') && (
              <div>
                <label className="block text-sm font-medium mb-1">Alarm</label>
                <input
                  type="text"
                  value={newItem.alarm}
                  onChange={(e) => setNewItem({ ...newItem, alarm: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="[7am], [every 2 hr], etc."
                />
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <BaseWidget title="All Schedules" icon="⚙️" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading schedules...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="All Schedules" icon="⚙️" onRemove={onRemove}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-destructive mb-2">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title="All Schedules" icon="⚙️" onRemove={onRemove}>
      <div className="h-full flex flex-col">
        {/* Header with add button */}
        <div className="flex justify-between items-center mb-4 pb-2 border-b">
          <h3 className="font-semibold">Scheduled Items ({scheduledItems.length})</h3>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90"
          >
            + Add Schedule
          </button>
        </div>

        {/* Schedule list */}
        <div className="flex-1 overflow-y-auto space-y-2">
          {scheduledItems.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No schedules found</p>
              <p className="text-sm">Click "Add Schedule" to create your first schedule</p>
            </div>
          ) : (
            scheduledItems.map((item) => (
              <div
                key={item.id}
                className="bg-card/50 border border-border rounded-lg p-3 hover:bg-card/70 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium truncate">{item.title}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getCategoryColor(item.category)}`}>
                        {getWidgetTypeDisplayName(item.type)}
                      </span>
                      {item.category && (
                        <span className="text-xs text-muted-foreground">
                          {item.category}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div>Frequency: {item.frequency}</div>
                      {item.importance && (
                        <div>Importance: {item.importance}</div>
                      )}
                      {item.alarm && (
                        <div>Alarm: {item.alarm}</div>
                      )}
                      {item.searchQuery && (
                        <div>Query: "{item.searchQuery}"</div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-1 ml-2">
                    <button
                      onClick={() => setEditingItem(item)}
                      className="p-1 text-muted-foreground hover:text-foreground"
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="p-1 text-muted-foreground hover:text-destructive"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Modals */}
      {editingItem && renderEditForm(editingItem)}
      {showAddForm && renderAddForm()}
    </BaseWidget>
  );
};

export default AllSchedulesWidget; 