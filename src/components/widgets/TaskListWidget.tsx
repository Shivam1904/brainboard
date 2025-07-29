import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { CheckCircle, Circle, Plus, X } from 'lucide-react';
import FrequencySection from './FrequencySection';
import { buildApiUrl, apiCall, API_CONFIG } from '../../config/api';
import { TodoTask, TodoTodayResponse } from '../../types/widgets';
import { Widget } from '../../utils/dashboardUtils'

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  category?: string;
  dueDate?: string;
  createdAt: string;
}

import { FrequencySettings } from '../../types/frequency';

interface MissionFormData {
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
  dueDate: string;
  frequency: FrequencySettings;
}

const getDummyTasks = (): Task[] => [
  {
    id: '1',
    title: 'Complete project documentation',
    description: 'Finish the API documentation for the new features',
    completed: false,
    priority: 'High',
    category: 'work',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T09:00:00Z'
  },
  {
    id: '2',
    title: 'Review code changes',
    description: 'Go through the pull requests and provide feedback',
    completed: true,
    priority: 'Medium',
    category: 'work',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T10:00:00Z'
  },
  {
    id: '3',
    title: 'Exercise routine',
    description: 'Complete 30 minutes of cardio and strength training',
    completed: false,
    priority: 'High',
    category: 'health',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T07:00:00Z'
  },
  {
    id: '4',
    title: 'Read technical articles',
    description: 'Read 2-3 articles about React performance optimization',
    completed: false,
    priority: 'Low',
    category: 'learning',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T14:00:00Z'
  },
  {
    id: '5',
    title: 'Plan weekend activities',
    description: 'Organize activities for the upcoming weekend',
    completed: false,
    priority: 'Medium',
    category: 'personal',
    dueDate: '2024-01-15',
    createdAt: '2024-01-10T16:00:00Z'
  }
];

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'High': return 'text-red-600 bg-red-50';
    case 'Medium': return 'text-yellow-600 bg-yellow-50';
    case 'Low': return 'text-green-600 bg-green-50';
    default: return 'text-gray-600 bg-gray-50';
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'work': return 'bg-blue-100 text-blue-800';
    case 'health': return 'bg-green-100 text-green-800';
    case 'learning': return 'bg-purple-100 text-purple-800';
    case 'personal': return 'bg-pink-100 text-pink-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getPriorityFromNumber = (priority: number): 'High' | 'Medium' | 'Low' => {
  switch (priority) {
    case 3: return 'High';
    case 2: return 'Medium';
    case 1: return 'Low';
    default: return 'Medium';
  }
};

interface TaskListWidgetProps {
  onRemove: () => void;
  widget: Widget
}

const TaskListWidget = ({ onRemove, widget }: TaskListWidgetProps) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<MissionFormData>({
    title: '',
    description: '',
    priority: 'Medium',
    category: 'personal',
    dueDate: new Date().toISOString().split('T')[0],
    frequency: {
      frequencySet: 'BALANCED',
      frequencySetValue: 0.6,
      frequency: 3,
      frequencyUnit: 'TIMES',
      frequencyPeriod: 'WEEKLY',
      isDailyHabit: false
    }
  });

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get widget_id from config or use the centralized mapping
      const widgetId = widget.id;
      const targetDate = new Date().toISOString().split('T')[0];
      
      const response = await apiCall<TodoTodayResponse>(
        buildApiUrl(API_CONFIG.tasks.getTodayTasks, {
          widget_id: widgetId,
          target_date: targetDate
        })
      );
      
      // Transform API response to local Task format
      const transformedTasks: Task[] = response.tasks.map((apiTask: TodoTask) => ({
        id: apiTask.id,
        title: apiTask.content,
        description: '', // API doesn't provide description field
        completed: apiTask.is_done,
        priority: getPriorityFromNumber(apiTask.priority),
        category: apiTask.category,
        dueDate: apiTask.due_date || undefined,
        createdAt: apiTask.created_at
      }));
      
      setTasks(transformedTasks);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      // Fallback to dummy data on error
      const dummyTasks = getDummyTasks();
      setTasks(dummyTasks);
      setError('Using offline data - API unavailable');
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: string, completed: boolean) => {
    try {
      // TODO: Replace with real API call when endpoint is available
      // await apiCall(buildApiUrl(`/api/tasks/update`), {
      //   method: 'PUT',
      //   body: JSON.stringify({ id: taskId, completed })
      // });
      
      // Update local state for now
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, completed } : task
        )
      );
    } catch (err) {
      console.error('Error updating task:', err);
      // Still update local state even if API fails
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, completed } : task
        )
      );
    }
  };

  const addMission = async (missionData: MissionFormData) => {
    try {
      // TODO: Replace with real API call when endpoint is available
      // await apiCall(buildApiUrl('/api/tasks/mission'), {
      //   method: 'POST',
      //   body: JSON.stringify(missionData)
      // });
      
      // Add to local state (simulating API response)
      const newTask: Task = {
        id: Date.now().toString(),
        title: missionData.title,
        description: missionData.description,
        completed: false,
        priority: missionData.priority,
        category: missionData.category,
        dueDate: missionData.dueDate,
        createdAt: new Date().toISOString()
      };
      
      setTasks(prevTasks => [newTask, ...prevTasks]);
      setShowAddForm(false);
      setFormData({
        title: '',
        description: '',
        priority: 'Medium',
        category: 'personal',
        dueDate: new Date().toISOString().split('T')[0],
        frequency: {
          frequencySet: 'BALANCED',
          frequencySetValue: 0.6,
          frequency: 3,
          frequencyUnit: 'TIMES',
          frequencyPeriod: 'WEEKLY',
          isDailyHabit: false
        }
      });
    } catch (err) {
      console.error('Error adding mission:', err);
      // Still add to local state even if API fails
      const newTask: Task = {
        id: Date.now().toString(),
        title: missionData.title,
        description: missionData.description,
        completed: false,
        priority: missionData.priority,
        category: missionData.category,
        dueDate: missionData.dueDate,
        createdAt: new Date().toISOString()
      };
      
      setTasks(prevTasks => [newTask, ...prevTasks]);
      setShowAddForm(false);
      setFormData({
        title: '',
        description: '',
        priority: 'Medium',
        category: 'personal',
        dueDate: new Date().toISOString().split('T')[0],
        frequency: {
          frequencySet: 'BALANCED',
          frequencySetValue: 0.6,
          frequency: 3,
          frequencyUnit: 'TIMES',
          frequencyPeriod: 'WEEKLY',
          isDailyHabit: false
        }
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;
    addMission(formData);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const completedTasks = tasks.filter(task => task.completed);
  const pendingTasks = tasks.filter(task => !task.completed);
  const progressPercentage = tasks.length > 0 ? (completedTasks.length / tasks.length) * 100 : 0;

  if (loading) {
    return (
      <BaseWidget title="Today's Tasks" icon="📋" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error && tasks.length === 0) {
    return (
      <BaseWidget title="Today's Tasks" icon="📋" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-orange-600 mb-2">{error}</p>
          <button 
            onClick={fetchTasks}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget title="Today's Tasks" icon="📋" onRemove={onRemove}>
      <div className="p-4 h-full overflow-y-auto">
        {/* Offline Indicator */}
        {error && (
          <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-xs text-orange-700 text-center">{error}</p>
          </div>
        )}
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-500">{completedTasks.length}/{tasks.length} completed</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Add Task Button */}
        <div className="mb-4">
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={16} />
            Add Mission
          </button>
        </div>

        {/* Tasks List */}
        <div className="space-y-3 ">
          {tasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No tasks for today</p>
              <p className="text-sm">Add a mission to get started!</p>
            </div>
          ) : (
            tasks.map(task => (
              <div 
                key={task.id} 
                className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${
                  task.completed 
                    ? 'bg-gray-50 border-gray-200' 
                    : 'bg-white border-gray-200 hover:border-blue-300'
                }`}
              >
                <button
                  onClick={() => updateTaskStatus(task.id, !task.completed)}
                  className="mt-0.5 flex-shrink-0"
                >
                  {task.completed ? (
                    <CheckCircle size={20} className="text-green-600" />
                  ) : (
                    <Circle size={20} className="text-gray-400 hover:text-blue-600" />
                  )}
                </button>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className={`font-medium text-sm ${
                      task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                    }`}>
                      {task.title}
                    </h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                  
                  {task.description && (
                    <p className={`text-xs mt-1 ${
                      task.completed ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {task.description}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-2 mt-2">
                    {task.category && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(task.category)}`}>
                        {task.category}
                      </span>
                    )}
                    {task.dueDate && (
                      <span className="text-xs text-gray-500">
                        Due: {new Date(task.dueDate).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Mission Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold">Create New Mission</h3>
                  <p className="text-blue-100 mt-1">Set your goals and track your progress</p>
                </div>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-white hover:text-blue-100 p-2 rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
            </div>
            
            {/* Form Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Mission Title Section */}
                <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-4 border border-orange-200">
                  <label className="block text-lg font-bold text-gray-800 mb-2">
                    MISSION TITLE
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-lg"
                    placeholder="What do you want to achieve?"
                    required
                  />
                </div>
                
                {/* Description Section */}
                <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-4 border border-pink-200">
                  <label className="block text-lg font-bold text-gray-800 mb-2">
                    DESCRIPTION
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-pink-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
                    placeholder="Describe your mission in detail..."
                    rows={3}
                  />
                </div>
                
                {/* Priority & Category Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Priority Section */}
                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-4 border border-yellow-200">
                    <label className="block text-lg font-bold text-gray-800 mb-3">
                      PRIORITY LEVEL
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {['Low', 'Medium', 'High'].map((priority) => (
                        <button
                          key={priority}
                          type="button"
                          onClick={() => setFormData({...formData, priority: priority as 'High' | 'Medium' | 'Low'})}
                          className={`px-4 py-3 rounded-lg font-medium transition-all ${
                            formData.priority === priority
                              ? 'bg-orange-500 text-white shadow-lg transform scale-105'
                              : 'bg-white/70 text-gray-700 hover:bg-orange-100 hover:scale-102'
                          }`}
                        >
                          {priority}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Category Section */}
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-4 border border-green-200">
                    <label className="block text-lg font-bold text-gray-800 mb-3">
                      CATEGORY
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { value: 'work', label: 'Work', color: 'from-blue-500 to-blue-600' },
                        { value: 'health', label: 'Health', color: 'from-green-500 to-green-600' },
                        { value: 'learning', label: 'Learning', color: 'from-purple-500 to-purple-600' },
                        { value: 'personal', label: 'Personal', color: 'from-pink-500 to-pink-600' }
                      ].map((category) => (
                        <button
                          key={category.value}
                          type="button"
                          onClick={() => setFormData({...formData, category: category.value})}
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
                  </div>
                </div>
                
                {/* Due Date Section */}
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
                  <label className="block text-lg font-bold text-gray-800 mb-2">
                    DUE DATE
                  </label>
                  <input
                    type="date"
                    value={formData.dueDate}
                    onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                    className="w-full px-4 py-3 bg-white/70 backdrop-blur-sm border border-indigo-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
                
                {/* Frequency Section */}
                <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl p-4 border border-teal-200">
                  <label className="block text-lg font-bold text-gray-800 mb-3">
                    FREQUENCY
                  </label>
                  <FrequencySection
                    frequency={formData.frequency}
                    onChange={(frequency) => setFormData({...formData, frequency})}
                    pillarColor={getCategoryColor(formData.category)}
                  />
                </div>
              </form>
            </div>
            
            {/* Footer */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 border-t border-gray-200">
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 hover:border-gray-400 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all shadow-lg"
                >
                  Create Mission
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </BaseWidget>
  );
};

export default TaskListWidget; 