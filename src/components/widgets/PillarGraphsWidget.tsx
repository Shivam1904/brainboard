import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { DailyWidget, apiService } from '../../services/api';

export const categoryColors = {
  productivity: { value: 'productivity', label: 'Productivity', color: '#3B82F6' }, // blue
  health: { value: 'health', label: 'Health', color: '#EF4444' }, // red
  job: { value: 'job', label: 'Job', color: '#8B5CF6' }, // purple
  information: { value: 'information', label: 'Information', color: '#EAB308' }, // yellow
  entertainment: { value: 'entertainment', label: 'Entertainment', color: '#EC4899' }, // pink
  utilities: { value: 'utilities', label: 'Utilities', color: '#6B7280' }, // gray
  personal: { value: 'personal', label: 'Personal', color: '#10B981' } // green
};

interface TaskData {
  id: string;
  title: string;
  category: string;
  widget_id: string;
  date: string;
  activity_data?: Record<string, any>;
}

interface CategoryStats {
  category: string;
  totalAdded: number;
  totalCompleted: number;
  completionRate: number;
}

interface PillarGraphsData {
  year: number;
  month: number;
  tasks: TaskData[];
  categoryStats: CategoryStats[];
  totalTasks: number;
  totalCompleted: number;
  overallCompletionRate: number;
}

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

interface PillarGraphsWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
}

const PillarGraphsWidget = ({ onRemove, widget, targetDate }: PillarGraphsWidgetProps) => {
  const [currentDate, setCurrentDate] = useState(new Date(targetDate));
  const [graphData, setGraphData] = useState<PillarGraphsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGraphData = async (year: number, month: number) => {
    try {
      setLoading(true);
      setError(null);

      // Compute start and end of month
      const startOfMonth = new Date(year, month - 1, 1);
      const endOfMonth = new Date(year, month, 0);

      // Fetch all widgets for the month
      const items = await apiService.getWidgetActivityForCalendar({
        calendar_id: widget.widget_id,
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: endOfMonth.toISOString().split('T')[0],
        calendar_type: 'pillarsGraph'
      });

      // Process tasks data
      const tasks = items.filter((todo: DailyWidget) =>
        !['calendar', 'allSchedules', 'aiChat', 'moodTracker', 'notes', 'habitTracker', 'yearCalendar', 'pillarsGraph'].includes(todo.widget_type)).map(item => ({
        id: item.daily_widget_id || item.id,
        title: item.title,
        category: item.category,
        widget_id: item.widget_id,
        date: item.date || new Date().toISOString().split('T')[0],
        activity_data: item.activity_data,
      }));

      // Calculate category statistics
      const categoryMap = new Map<string, { added: number; completed: number }>();
      
      tasks.forEach(task => {
        const category = task.category || 'personal';
        const current = categoryMap.get(category) || { added: 0, completed: 0 };
        
        current.added += 1;
        if (task.activity_data?.status === 'completed') {
          current.completed += 1;
        }
        
        categoryMap.set(category, current);
      });

      // Convert to array format
      const categoryStats: CategoryStats[] = Array.from(categoryMap.entries()).map(([category, stats]) => ({
        category,
        totalAdded: stats.added,
        totalCompleted: stats.completed,
        completionRate: stats.added > 0 ? (stats.completed / stats.added) * 100 : 0
      }));

      // Sort by completion rate descending
      categoryStats.sort((a, b) => b.completionRate - a.completionRate);

      // Calculate overall statistics
      const totalTasks = tasks.length;
      const totalCompleted = tasks.filter(task => task.activity_data?.status === 'completed').length;
      const overallCompletionRate = totalTasks > 0 ? (totalCompleted / totalTasks) * 100 : 0;

      setGraphData({
        year,
        month,
        tasks,
        categoryStats,
        totalTasks,
        totalCompleted,
        overallCompletionRate
      });
    } catch (err) {
      setError('Failed to load graph data');
      console.error('Error fetching graph data:', err);
    } finally {
      setLoading(false);
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
    fetchGraphData(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    fetchGraphData(today.getFullYear(), today.getMonth() + 1);
  };

  useEffect(() => {
    fetchGraphData(currentDate.getFullYear(), currentDate.getMonth() + 1);
  }, []);

  if (loading) {
    return (
      <BaseWidget title="Pillar Graphs" icon="📊" onRemove={onRemove}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget title="Pillar Graphs" icon="📊" onRemove={onRemove}>
        <div className="flex flex-col items-center justify-center h-32 text-center">
          <p className="text-red-600 mb-2">{error}</p>
          <button
            onClick={() => fetchGraphData(currentDate.getFullYear(), currentDate.getMonth() + 1)}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </BaseWidget>
    );
  }

  if (!graphData) {
    return (
      <BaseWidget title="Pillar Graphs" icon="📊" onRemove={onRemove}>
        <div className="text-center py-8 text-gray-500">
          <p>No graph data available</p>
        </div>
      </BaseWidget>
    );
  }

  // Find the maximum value for scaling
  const maxValue = Math.max(
    ...graphData.categoryStats.map(stat => Math.max(stat.totalAdded, stat.totalCompleted))
  );

  return (
    <BaseWidget title={widget.title || "Pillar Graphs"} icon="📊" onRemove={onRemove}>
      <div className="flex flex-col px-4 pt-4 h-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronLeft size={16} />
            </button>
            <h3 className="font-semibold text-lg mx-2">
              {monthNames[graphData.month - 1]} {graphData.year}
            </h3>
            <button
              onClick={() => navigateMonth('next')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronRight size={16} />
            </button>
          </div>
          <button
            onClick={goToToday}
            className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            Today
          </button>
        </div>

        {/* Summary Stats */}
        {false && (<div className="grid grid-cols-3 gap-2 mb-4 text-center">
          <div className="bg-blue-50 p-2 rounded">
            <div className="text-lg font-bold text-blue-600">{graphData?.totalTasks}</div>
            <div className="text-xs text-blue-500">Total Tasks</div>
          </div>
          <div className="bg-green-50 p-2 rounded">
            <div className="text-lg font-bold text-green-600">{graphData?.totalCompleted}</div>
            <div className="text-xs text-green-500">Completed</div>
          </div>
          <div className="bg-purple-50 p-2 rounded">
            <div className="text-lg font-bold text-purple-600">{graphData?.overallCompletionRate.toFixed(1)}%</div>
            <div className="text-xs text-purple-500">Success Rate</div>
          </div>
        </div>)}

        {/* Bar Charts */}
        <div className="flex-1 overflow-y-auto">
          <div className="flex items-end justify-between space-x-2 h-[200px] px-2">
            {graphData.categoryStats.map((stat) => {
              const color = categoryColors[stat.category as keyof typeof categoryColors]?.color || '#6B7280';
              const addedWidth = maxValue > 0 ? ((stat.totalAdded-stat.totalCompleted) / maxValue) * 50 : 0;
              const completedWidth = maxValue > 0 ? (stat.totalCompleted / maxValue) * 50 : 0;
              const completionRate: number = stat.totalCompleted / stat.totalAdded * 100;
              return (
                <div key={stat.category} className="flex flex-col items-center space-y-2">
                  {/* Single Horizontal Bar with Stacked Sections */}
                  <div className="relative" style={{  width: `50px` }}>
                    <div 
                      className="h-full bg-gray-300 transition-all duration-300"
                      style={{ height: `${100-completionRate}px` }}
                    />
                    <div 
                      className="h-full transition-all duration-300"
                      style={{ 
                        height: `${completionRate}px`, 
                        backgroundColor: color
                      }}
                    />
                  </div>
                  
                  {/* Category Label */}
                  <div className="text-xs font-medium text-gray-700 text-center">
                    {categoryColors[stat.category as keyof typeof categoryColors]?.label || stat.category}
                  </div>
                  
                  {/* Task Count */}
                  <div className="text-xs text-gray-500 text-center">
                    {stat.totalCompleted}/{stat.totalAdded}
                  </div>
                  
                  {/* Completion Rate */}
                  <div className="text-xs text-gray-500 text-center">
                    {stat.completionRate.toFixed()}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 pt-2 border-t border-gray-200">
          <div className="flex items-center justify-center space-x-4 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-gray-300 rounded"></div>
              <span>Total Tasks</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-blue-500 rounded"></div>
              <span>Completed Tasks</span>
            </div>
          </div>
        </div>
      </div>
    </BaseWidget>
  );
};

export default PillarGraphsWidget; 