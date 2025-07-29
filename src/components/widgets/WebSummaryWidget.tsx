import { useState } from 'react'
import { Search, ExternalLink } from 'lucide-react'
import BaseWidget from './BaseWidget'
import { dashboardService } from '../../services/dashboard'

interface Summary {
  id: string
  query: string
  summary: string
  sources: string[]
  createdAt: string
}

interface WebSummaryWidgetProps {
  onRemove: () => void
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

const WebSummaryWidget = ({ onRemove, widget }: WebSummaryWidgetProps) => {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentSummary, setCurrentSummary] = useState<Summary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isRead, setIsRead] = useState(false)
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
  } | null>(null)

  const searchAndSummarize = async () => {
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      // const response = await apiService.getWebSearchAISummary(widget.daily_widget_id, { query });
      
      // Mock response for now
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API delay
      
      // Create a mock summary for now
      const mockSummary: Summary = {
        id: Date.now().toString(),
        query: query,
        summary: "This is a mock summary for demonstration purposes. The real API would provide an AI-generated summary based on web search results.",
        sources: [
          "https://example.com/source1",
          "https://example.com/source2",
          "https://example.com/source3"
        ],
        createdAt: new Date().toISOString()
      };

      setCurrentSummary(mockSummary)
      setQuery('')
      
      // Fetch activity data for this widget
      try {
        const widgetId = widget.widget_ids[0];
        const activityResponse = await dashboardService.getWebSearchSummaryAndActivity(widgetId);
        setActivityData(activityResponse);
        setIsRead(activityResponse.activity.status === 'completed');
      } catch (activityErr) {
        console.error('Failed to fetch activity data:', activityErr);
        // Don't fail the whole operation if activity fetch fails
      }
    } catch (error) {
      setError('Failed to generate summary. Please try again.')
      console.error('Summary error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const clearSummary = () => {
    setCurrentSummary(null)
    setError(null)
    setActivityData(null)
    setIsRead(false)
  }

  // Update read status
  const updateReadStatus = async (read: boolean) => {
    if (!currentSummary || !activityData) return;
    
    try {
      // Update the activity status using the activity_id we already have
      await dashboardService.updateWebSearchActivity(activityData.activity.id, {
        status: read ? 'completed' : 'pending',
        reaction: read ? 'read' : 'unread',
        summary: currentSummary.summary,
        source_json: currentSummary.sources,
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
  }

  return (
    <BaseWidget
      title="Web Summary"
      icon="🔍"
      onRemove={onRemove}
    >
      <div className="h-full flex flex-col">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchAndSummarize()}
            placeholder="Ask anything..."
            className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
          <button
            onClick={searchAndSummarize}
            disabled={isLoading || !query.trim()}
            className="px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Search size={16} />
          </button>
        </div>



        <div className="flex-1 overflow-y-auto">
          {isLoading && (
            <div className="text-center text-muted-foreground py-8">
              <div className="animate-pulse">
                🧠 Searching the web and generating summary...
              </div>
            </div>
          )}

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3 mb-4">
              <p className="text-destructive text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs text-destructive/80 hover:text-destructive mt-1"
              >
                Dismiss
              </button>
            </div>
          )}

          {currentSummary && !isLoading && (
            <div className="space-y-4">
              <div className="bg-muted/50 rounded-md p-3">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-sm">Query:</h4>
                  <div className="flex items-center gap-2">
                    {/* Activity Status */}
                    {activityData && (
                      <span className={`text-xs px-2 py-1 rounded ${
                        activityData.activity.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {activityData.activity.status === 'completed' ? 'Read' : 'Unread'}
                      </span>
                    )}
                    {/* Read Checkbox */}
                    <div className="flex items-center gap-1">
                      <input
                        type="checkbox"
                        id="read-checkbox-summary"
                        checked={isRead}
                        onChange={(e) => updateReadStatus(e.target.checked)}
                        className="w-3 h-3 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-1"
                      />
                      <label htmlFor="read-checkbox-summary" className="text-xs text-gray-600">
                        Read
                      </label>
                    </div>
                    <button
                      onClick={clearSummary}
                      className="text-xs text-muted-foreground hover:text-foreground"
                    >
                      Clear
                    </button>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground italic">
                  "{currentSummary.query}"
                </p>
              </div>

              <div>
                <h4 className="font-medium text-sm mb-2">Summary:</h4>
                <p className="text-sm leading-relaxed">
                  {currentSummary.summary}
                </p>
              </div>

              {currentSummary.sources.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Sources:</h4>
                  <div className="space-y-1">
                    {currentSummary.sources.map((source, index) => (
                      <a
                        key={index}
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs text-primary hover:text-primary/80 transition-colors"
                      >
                        <ExternalLink size={12} />
                        {source}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-xs text-muted-foreground pt-2 border-t">
                Generated on {new Date(currentSummary.createdAt).toLocaleString()}
              </div>
            </div>
          )}

          {!currentSummary && !isLoading && !error && (
            <div className="text-center text-muted-foreground py-8">
              <p className="text-sm">Enter a query above to search and get an AI summary</p>
              <p className="text-xs mt-2">
                Powered by web search + OpenAI
              </p>
            </div>
          )}
        </div>
      </div>
    </BaseWidget>
  )
}

export default WebSummaryWidget
