import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { CheckCircle, Circle, Plus, X } from 'lucide-react';
// import { buildApiUrl, apiCall } from '../../config/api'; // Uncomment when API is ready

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

interface MissionFormData {
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
  dueDate: string;
  frequency: string;
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

interface TaskListWidgetProps {
  onRemove: () => void;
  config?: Record<string, any>;
  scheduledItem?: {
    id: string;
    title: string;
    category?: string;
  };
}

const TaskListWidget = ({ onRemove, config, scheduledItem }: TaskListWidgetProps) => {
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
    frequency: 'daily'
  });

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with real API call
      // const response = await apiCall<Task[]>(buildApiUrl('/api/tasks/today'));
      // setTasks(response);
      
      // Using dummy data for now
      const dummyTasks = getDummyTasks();
      setTasks(dummyTasks);
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: string, completed: boolean) => {
    try {
      // TODO: Replace with real API call
      // await apiCall(buildApiUrl(`/api/tasks/update`), {
      //   method: 'PUT',
      //   body: JSON.stringify({ id: taskId, completed })
      // });
      
      // Update local state
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, completed } : task
        )
      );
    } catch (err) {
      setError('Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const addMission = async (missionData: MissionFormData) => {
    try {
      // TODO: Replace with real API call
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
        frequency: 'daily'
      });
    } catch (err) {
      setError('Failed to add mission');
      console.error('Error adding mission:', err);
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

  if (error) {
    return (
      <BaseWidget title="Today's Tasks" icon="📋" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-red-600 mb-2">{error}</p>
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
      <div className="p-4">
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
        <div className="space-y-3 max-h-64 overflow-y-auto">
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Add New Mission</h3>
              <button
                onClick={() => setShowAddForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter mission title"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter mission description"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value as 'High' | 'Medium' | 'Low'})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="work">Work</option>
                    <option value="health">Health</option>
                    <option value="learning">Learning</option>
                    <option value="personal">Personal</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    value={formData.dueDate}
                    onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Frequency
                  </label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="once">Once</option>
                  </select>
                </div>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Save Mission
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </BaseWidget>
  );
};

export default TaskListWidget; 