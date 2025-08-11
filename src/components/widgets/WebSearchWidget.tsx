import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget } from '../../services/api';
import { useTodayWidgetsData } from '../../hooks/useDashboardData';
import { useDashboardActions } from '../../stores/dashboardStore';

interface WebSearchWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
  targetDate: string;
}

const WebSearchWidget = ({ onRemove, widget, targetDate }: WebSearchWidgetProps) => {
  const { todayWidgets, isLoading, error } = useTodayWidgetsData(targetDate);
  const { updateWidgetActivity } = useDashboardActions();
  
  const [webSearchData, setWebSearchData] = useState<any | null>(null);
  const [isRead, setIsRead] = useState(false);

  // Use the passed widget prop directly - it already contains the widget data
  // const webSearchWidget = todayWidgets.find(w => w.widget_type === 'websearch');

  // Update read status
  const updateReadStatus = async (read: boolean) => {
    if (!widget || !webSearchData) return;
    
    try {
      // Update the activity status
      await updateWidgetActivity(widget.daily_widget_id, {
        status: read ? 'completed' : 'pending',
        reaction: read ? 'read' : 'unread',
        summary: webSearchData.summary,
        source_json: webSearchData.sources,
      });
      
      setIsRead(read);
    } catch (err) {
      console.error('Error updating read status:', err);
      // Still update local state even if API fails
      setIsRead(read);
    }
  };

  // Set initial data when widget is found
  useEffect(() => {
    if (widget) {
      setWebSearchData(widget);
      setIsRead(widget.activity_data?.status === 'completed');
    }
  }, [widget]);

  // Show loading state
  if (isLoading) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 mx-auto mb-2"></div>
            <p className="text-gray-600">Loading web search...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  // Show error state
  if (error) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-red-600 mb-2">Failed to load web search</p>
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </div>
      </BaseWidget>
    );
  }

  // Show no data state
  if (!widget || !webSearchData) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-gray-600 mb-2">No web search data available</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget 
      title={webSearchData.title || "Web Search"} 
      icon="🔍" 
      onRemove={onRemove}
    >
      <div className="space-y-4 h-full overflow-y-auto">

        
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-3">
            {/* Title */}
            <h3 className="font-medium text-sm mb-2">Web Search</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {webSearchData.title}
            </p>

            {/* Status and Read Checkbox */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  webSearchData.search_successful ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {webSearchData.search_successful ? 'Search Successful' : 'Search Failed'}
                </span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {webSearchData.results_count} results
                </span>
              </div>
              
              {/* Read Checkbox */}
              <div className="flex flex-col items-center gap-2">
                <input
                  type="checkbox"
                  id="read-checkbox"
                  checked={isRead}
                  onChange={(e) => updateReadStatus(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 cursor-pointer border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                />
                <label htmlFor="read-checkbox" className="text-xs text-gray-600">
                  Read
                </label>
              </div>
            </div>

            {/* Summary */}
            {webSearchData.summary && (
              <div>
                <h3 className="font-medium text-sm mb-2">AI Summary</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {webSearchData.summary}
                </p>
              </div>
            )}

            {/* Sources */}
            {webSearchData.sources && webSearchData.sources.length > 0 && (
              <div>
                <h3 className="font-medium text-sm mb-2">Sources</h3>
                <div className="space-y-1">
                  {webSearchData.sources.map((source: any, index: number) => (
                    <div key={index} className="text-xs">
                      <a 
                        href={source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline break-all"
                      >
                        {source.title}
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Model Info */}
            <div className="text-xs text-muted-foreground pt-2 border-t">
              <div>AI Model: {webSearchData.ai_model_used}</div>
              <div>Generated: {new Date(webSearchData.created_at).toLocaleDateString()}</div>
              {webSearchData.activity_data && (
                <div>Last Activity: {new Date(webSearchData.activity_data?.updated_at).toLocaleDateString()}</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </BaseWidget>
  );
};

export default WebSearchWidget; 