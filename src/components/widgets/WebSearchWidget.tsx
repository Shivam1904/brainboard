import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { getDummyWebSearchSummaryAndActivity } from '../../data/widgetDummyData';
import { WebSearchAISummaryResponse } from '../../types';
import { apiService } from '../../services/api';

interface WebSearchWidgetProps {
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

const WebSearchWidget = ({ onRemove, widget }: WebSearchWidgetProps) => {
  const [webSearchData, setWebSearchData] = useState<WebSearchAISummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUsingDummyData, setIsUsingDummyData] = useState(false);

  // Fetch web search data for this specific widget
  const fetchWebSearchData = async () => {
    try {
      setIsUsingDummyData(false);
      
      // Get the widget_id from the widget_ids array (first one for websearch widgets)
      const widgetId = widget.widget_ids[0];
      
      // Call the real API
      const response = await apiService.getWebSearchAISummary(widgetId);
      setWebSearchData(response);
    } catch (err) {
      console.error('Failed to fetch web search data:', err);
      setError('Failed to load web search data');
      setIsUsingDummyData(true);
      // Fallback to dummy data
      const dummyData = getDummyWebSearchSummaryAndActivity(widget.daily_widget_id);
      setWebSearchData(dummyData as any); // Type assertion for fallback
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
        {/* Dummy Data Indicator */}
        {isUsingDummyData && (
          <div className="p-2 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-700 text-center">
              🔍 Showing sample data - API not connected
            </p>
          </div>
        )}
        
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-3">
            {/* Status */}
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
            </div>
          </div>
        </div>
      </div>
    </BaseWidget>
  );
};

export default WebSearchWidget; 