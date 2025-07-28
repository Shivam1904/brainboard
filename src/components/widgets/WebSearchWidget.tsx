import { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
// import { buildApiUrl, apiCall } from '../../config/api'; // Uncomment when API is ready

// Types for the web search data
interface WebSearchResult {
  id: string;
  searchTerm: string;
  heading: string;
  subheading: string;
  text: string;
  images?: string[];
  chartData?: any;
  scheduleDate: string;
}

// interface ScheduledSearch {
//   id: string;
//   searchTerm: string;
//   scheduledTime: string;
// }

// Dummy data for development (no longer used with new architecture)
// const DUMMY_SCHEDULED_SEARCHES: ScheduledSearch[] = [
//   {
//     id: '1',
//     searchTerm: 'Latest AI developments',
//     scheduledTime: '09:00'
//   },
//   {
//     id: '2', 
//     searchTerm: 'Stock market trends',
//     scheduledTime: '14:00'
//   },
//   {
//     id: '3',
//     searchTerm: 'Weather forecast',
//     scheduledTime: '08:00'
//   }
// ];

const getDummyWebSearchResult = (searchQuery: string): WebSearchResult => {
  switch (searchQuery.toLowerCase()) {
    case 'latest football news and scores':
      return {
        id: 'football',
        searchTerm: searchQuery,
        heading: 'Football: Champions League Highlights',
        subheading: 'All the latest scores and news from Europe',
        text: 'Manchester United secured a dramatic win in the final minutes. Real Madrid and Barcelona both advanced to the next round. Stay tuned for more updates and analysis.',
        images: ['https://via.placeholder.com/300x200/2563EB/FFFFFF?text=Football'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    case 'artificial intelligence developments today':
      return {
        id: 'ai',
        searchTerm: searchQuery,
        heading: 'AI: New Breakthroughs in 2024',
        subheading: 'GPT-5 and robotics lead the way',
        text: 'Researchers have announced major advances in natural language processing and robotics. AI is now being used in healthcare, finance, and creative industries at an unprecedented scale.',
        images: ['https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=AI+News'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    case 'stock market trends and analysis':
      return {
        id: 'stocks',
        searchTerm: searchQuery,
        heading: 'Stocks: Market Trends & Analysis',
        subheading: 'Tech stocks rally, S&P 500 hits new high',
        text: 'The stock market saw a significant rally today, led by gains in the technology sector. Analysts predict continued growth as earnings season approaches.',
        images: ['https://via.placeholder.com/300x200/10B981/FFFFFF?text=Stocks'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
    default:
      return {
        id: 'default',
        searchTerm: searchQuery,
        heading: `Search Results for: ${searchQuery}`,
        subheading: `Latest information about ${searchQuery}`,
        text: `This is a sample result for the search query: "${searchQuery}". In a real implementation, this would contain actual search results from the web.`,
        images: ['https://via.placeholder.com/300x200/64748B/FFFFFF?text=Web+Search'],
        chartData: null,
        scheduleDate: new Date().toISOString().split('T')[0]
      };
  }
};

// const DUMMY_SEARCH_RESULTS: Record<string, WebSearchResult> = {
//   '1': {
//     id: '1',
//     searchTerm: 'Latest AI developments',
//     heading: 'AI Breakthrough: New Language Model Achieves Human-Level Understanding',
//     subheading: 'Revolutionary advances in natural language processing',
//     text: 'Researchers have developed a new AI model that demonstrates unprecedented understanding of human language. The model, called GPT-5, shows remarkable capabilities in reasoning, creativity, and problem-solving tasks that were previously thought to be beyond the reach of artificial intelligence.',
//     images: ['https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=AI+Breakthrough'],
//     scheduleDate: '2024-01-15'
//   },
//   '2': {
//     id: '2',
//     searchTerm: 'Stock market trends',
//     heading: 'Market Analysis: Tech Stocks Lead Recovery',
//     subheading: 'S&P 500 reaches new heights as technology sector surges',
//     text: 'Technology stocks have led a broad market rally, with the S&P 500 reaching new record levels. Major tech companies including Apple, Microsoft, and Google parent Alphabet have all posted strong quarterly results, driving investor confidence.',
//     images: ['https://via.placeholder.com/300x200/10B981/FFFFFF?text=Market+Trends'],
//     scheduleDate: '2024-01-15'
//   },
//   '3': {
//     id: '3',
//     searchTerm: 'Weather forecast',
//     heading: 'Weather Update: Sunny Skies Expected',
//     subheading: 'Perfect conditions for outdoor activities this weekend',
//     text: 'The weather forecast shows clear skies and mild temperatures throughout the weekend. Highs will reach 75°F with light winds, making it ideal for outdoor activities. No precipitation is expected for the next 7 days.',
//     images: ['https://via.placeholder.com/300x200/F59E0B/FFFFFF?text=Weather+Forecast'],
//     scheduleDate: '2024-01-15'
//   }
// };

interface EverydayWebSearchWidgetProps {
  onRemove: () => void;
  config?: Record<string, any>;
  scheduledItem?: {
    id: string;
    title: string;
    searchQuery?: string;
    category?: string;
  };
}

// Rename component
const WebSearchWidget = ({ onRemove, config, scheduledItem }: EverydayWebSearchWidgetProps) => {
  // Use config if provided (e.g., config.maxResults, config.showImages)
  const showImages = config?.showImages !== false;
  const searchQuery = scheduledItem?.searchQuery || config?.searchQuery || 'default search';
  const widgetTitle = scheduledItem?.title || config?.title || 'Web Search';
  const [searchResults, setSearchResults] = useState<WebSearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch search results for this specific search query
  const fetchSearchResults = async () => {
    try {
      // Use the new dummy function for unique results
      const dummyResult = getDummyWebSearchResult(searchQuery);
      setSearchResults([dummyResult]);
    } catch (err) {
      console.error('Failed to fetch search results:', err);
      setError('Failed to load search results');
      // Fallback to generic dummy data
      const dummyResult = getDummyWebSearchResult('default');
      setSearchResults([dummyResult]);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      await fetchSearchResults();
      
      setLoading(false);
    };

    loadData();
  }, [searchQuery]); // Re-fetch when search query changes

  if (loading) {
    return (
      <BaseWidget 
        title={widgetTitle} 
        icon="🔍" 
        onRemove={onRemove}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 mx-auto mb-2"></div>
            <p className="text-muted-foreground">Loading web searches...</p>
          </div>
        </div>
      </BaseWidget>
    );
  }

  if (error) {
    return (
      <BaseWidget 
        title={widgetTitle} 
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

  return (
    <BaseWidget 
      title={widgetTitle} 
      icon="🔍" 
      onRemove={onRemove}
    >
      <div className="space-y-4 h-full overflow-y-auto">
        {searchResults.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No web searches scheduled for today</p>
          </div>
        ) : (
          searchResults.map((result) => (
            <div 
              key={result.id} 
              className="bg-card/50 rounded-lg p-2 space-y-3"
            >
              {/* Search Term */}
              <div className="flex items-center gap-2">
                <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                  {result.searchTerm}
                </span>
                <span className="text-xs text-muted-foreground">
                  {result.scheduleDate}
                </span>
              </div>

              {/* Heading */}
              <h4 className="font-semibold text-card-foreground text-lg">
                {result.heading}
              </h4>

              {/* Subheading */}
              <p className="text-sm text-muted-foreground font-medium">
                {result.subheading}
              </p>

              {/* Main Text */}
              <p className="text-sm text-card-foreground leading-relaxed">
                {result.text}
              </p>

              {/* Images */}
              {showImages && result.images && result.images.length > 0 && (
                <div className="flex gap-2 overflow-x-auto">
                  {result.images.map((image, index) => (
                    <img
                      key={index}
                      src={image}
                      alt={`Search result ${index + 1}`}
                      className="h-20 w-auto rounded border border-border flex-shrink-0"
                    />
                  ))}
                </div>
              )}

              {/* Chart Data Placeholder */}
              {result.chartData && (
                <div className="bg-muted/30 rounded p-3">
                  <p className="text-xs text-muted-foreground mb-2">Chart Data Available</p>
                  <div className="h-16 bg-muted rounded flex items-center justify-center">
                    <span className="text-xs text-muted-foreground">Chart visualization would go here</span>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </BaseWidget>
  );
};

export default WebSearchWidget; 