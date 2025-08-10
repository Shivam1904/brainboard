import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { CheckCircle, Circle, Plus, X } from 'lucide-react';
import FrequencySection from './FrequencySection';
import { dashboardService } from '../../services/dashboard';
import { DailyWidget } from '../../services/api';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
  dueDate?: string;
  createdAt: string;
}

import { FrequencySettings } from '../../types/frequency';
import { categoryColors } from './CalendarWidget';

interface MissionFormData {
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
  dueDate: string;
  frequency: FrequencySettings;
}


const getCategoryColor = (category: string) => {
  console.log(category, categoryColors[category as keyof typeof categoryColors]);
  return categoryColors[category as keyof typeof categoryColors].color;
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
  widget: DailyWidget;
  onHeightChange: (dailyWidgetId: string, height: number) => void;
  targetDate: string;
}

const TaskListWidget = ({  onRemove, widget, onHeightChange, targetDate }: TaskListWidgetProps) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [progressText, setProgressText] = useState<string>('');
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

      // Use real API call
      const response = await dashboardService.getTodayWidgets(targetDate);

      // Convert API response to internal Task format
      const allTasksToCount = response.filter((todo: DailyWidget) =>
        !['calendar', 'allSchedules', 'aiChat', 'moodTracker'].includes(todo.widget_type)
      ).length;
      // Convert API response to internal Task format
      const allTasksCompleted = response.filter((todo: DailyWidget) =>
        !['calendar', 'allSchedules', 'aiChat', 'moodTracker'].includes(todo.widget_type) && todo.activity_data?.status === 'completed'
      ).length;

      setProgressText(`${allTasksCompleted} / ${allTasksToCount} `);

      // Convert API response to internal Task format
      const convertedTasks: Task[] = response.filter((todo: DailyWidget) =>
        !['calendar', 'allSchedules', 'aiChat', 'websearch', 'moodTracker'].includes(todo.widget_type)
        && !(todo.widget_config?.include_alarm_details || todo.widget_config?.include_tracker_details))
        .map((todo: DailyWidget) => ({
          id: todo.daily_widget_id,
          title: todo.title,
          category: todo.category,
          description: todo.description || '',
          completed: todo.activity_data?.status === 'completed',
          priority: getPriorityFromNumber(todo.activity_data?.progress / 25), // Convert progress to priority
          dueDate: todo.activity_data?.due_date || '',
          createdAt: todo.created_at || ''
        }));

      setTasks(convertedTasks);
      onHeightChange(widget.daily_widget_id, convertedTasks.length * 2 + 2);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to load tasks');
      // Fallback to empty array
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: string, completed: boolean) => {
    try {
      // Use real API call to update task status
      await dashboardService.updateTodoActivity(taskId, {
        status: completed ? 'completed' : 'pending',
        progress: completed ? 100 : 0
      });

      // Update local state
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
        category: 'productivity',
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
        category: 'productivity',
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
  }, [targetDate]);

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
      <div className={`p-4 h-full overflow-y-auto `}>
        {/* Offline Indicator */}
        {error && (
          <div className="mb-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-xs text-orange-700 text-center">{error}</p>
          </div>
        )}



        {/* Progress Bar */}
        {false && (<div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-500">{progressText} completed</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>)}

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
                className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${task.completed
                    ? `bg-${getCategoryColor(task.category)}-100 border border-${getCategoryColor(task.category)}-200 rounded-lg border-gray-200`
                    : `bg-${getCategoryColor(task.category)}-100 border border-${getCategoryColor(task.category)}-200 rounded-lg hover:border-${getCategoryColor(task.category)}-300`
                  }`}
              >
                <button
                  onClick={() => updateTaskStatus(task.id, !task.completed)}
                  className="mt-0.5 flex-shrink-0"
                >
                  {task.completed ? (
                    '✅'
                  ) : (
                    '◻️'
                  )}
                </button>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className={`font-medium text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                      }`}>
                      {task.title}
                    </h4>
                    <span className={`px-2 py-1 text-xs font-medium}`}>
                      {task.description}
                    </span>
                    {task.category && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium text-${getCategoryColor(task.category)}-800 bg-${getCategoryColor(task.category)}-100`}>
                        {task.category}
                      </span>
                    )}
                    {task.dueDate && (
                      <span className="text-xs text-gray-500">
                        Due: {new Date(task.dueDate).toLocaleDateString()}
                      </span>
                    )}
                  </div>

                  {task.description && (
                    <p className={`text-xs mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'
                      }`}>
                      {task.description}
                    </p>
                  )}

                  <div className="flex items-center gap-2 mt-2">
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
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
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
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
                          onClick={() => setFormData({ ...formData, priority: priority as 'High' | 'Medium' | 'Low' })}
                          className={`px-4 py-3 rounded-lg font-medium transition-all ${formData.priority === priority
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
                          onClick={() => setFormData({ ...formData, category: category.value })}
                          className={`px-4 py-3 rounded-lg font-medium transition-all ${formData.category === category.value
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
                    onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
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
                    onChange={(frequency) => setFormData({ ...formData, frequency })}
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