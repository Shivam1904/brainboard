import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { WebSearchAISummaryResponse } from '../../types/widgets';
import { dashboardService } from '../../services/dashboard';
import { DailyWidget } from '../../services/api';

interface WebSearchWidgetProps {
  onRemove: () => void;
  widget: DailyWidget;
}

const WebSearchWidget = ({ onRemove, widget }: WebSearchWidgetProps) => {
  const [webSearchData, setWebSearchData] = useState<WebSearchAISummaryResponse | null>(null);
  const [activityData, setActivityData] = useState<{
    websearch_details: {
      id: string;
      widget_id: string;
      title: string;
      created_at: string;
      updated_at: string;
    };
    activity: {
      id: string;
      status: 'pending' | 'completed' | 'failed';
      reaction: string;
      summary: string;
      source_json: any;
      created_at: string;
      updated_at: string;
    };
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRead, setIsRead] = useState(false);

  // Fetch web search data for this specific widget
  const fetchWebSearchData = async () => {
    try {
      // Get the widget_id from the widget_ids array (first one for websearch widgets)
      const widgetId = widget.widget_ids[0];
      
      // Call both APIs in parallel
      const [aiSummaryResponse, activityResponse] = await Promise.all([
        dashboardService.getWebSearchAISummary(widgetId),
        dashboardService.getWebSearchSummaryAndActivity(widgetId)
      ]);
      
      setWebSearchData(aiSummaryResponse);
      setActivityData(activityResponse);
      
      // Set initial read status based on activity data
      setIsRead(activityResponse.activity.status === 'completed');
    } catch (err) {
      console.error('Failed to fetch web search data:', err);
      setError('Failed to load web search data');
      // Fallback to empty state
      setWebSearchData(null);
      setActivityData(null);
    }
  };

  // Update read status
  const updateReadStatus = async (read: boolean) => {
    if (!webSearchData || !activityData) return;
    
    try {
      // Update the activity status using the activity_id we already have
      await dashboardService.updateWebSearchActivity(activityData.activity.id, {
        status: read ? 'completed' : 'pending',
        reaction: read ? 'read' : 'unread',
        summary: webSearchData.summary,
        source_json: webSearchData.sources,
        updated_by: 'user'
      });
      
      // Update local activity data
      setActivityData(prev => prev ? {
        ...prev,
        activity: {
          ...prev.activity,
          status: read ? 'completed' : 'pending',
          reaction: read ? 'read' : 'unread',
          updated_at: new Date().toISOString()
        }
      } : null);
      
      setIsRead(read);
    } catch (err) {
      console.error('Error updating read status:', err);
      // Still update local state even if API fails
      setIsRead(read);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      await fetchWebSearchData();
      
      setLoading(false);
    };

    loadData();
  }, [widget.widget_ids[0]]); // Changed dependency to widget_ids[0]

  if (loading) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading web search...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-destructive mb-2">{error}</p>
            <p className="text-sm text-muted-foreground">Showing dummy data for development</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (!webSearchData) {
    return (
      <BaseWidget 
        title="Web Search" 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-muted-foreground">No web search data available</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget 
      title={webSearchData.query || "Web Search"} 
      icon="🔍" 
      onRemove={onRemove}
    >
      <div className="space-y-4 h-full overflow-y-auto">

        
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-3">
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
                  {webSearchData.sources.map((source, index) => (
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
              {activityData && (
                <div>Last Activity: {new Date(activityData.activity.updated_at).toLocaleDateString()}</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </BaseWidget>
  );
};

export default WebSearchWidget; 