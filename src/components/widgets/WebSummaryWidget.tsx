import { useState } from 'react'
import { Search, ExternalLink } from 'lucide-react'
import BaseWidget from './BaseWidget'

interface Summary {
  id: string
  query: string
  summary: string
  sources: string[]
  createdAt: string
}

interface WebSummaryWidgetProps {
  onRemove: () => void
}

const WebSummaryWidget = ({ onRemove }: WebSummaryWidgetProps) => {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentSummary, setCurrentSummary] = useState<Summary | null>(null)
  const [error, setError] = useState<string | null>(null)

  const searchAndSummarize = async () => {
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/summary', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ query })
      // })
      // const data = await response.json()

      // Mock response for now
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API delay
      
      const mockSummary: Summary = {
        id: Date.now().toString(),
        query,
        summary: `Here's a comprehensive summary about "${query}": This topic involves multiple aspects and considerations. Based on recent research and available information, the key findings suggest that this is an evolving area with significant implications for various stakeholders.`,
        sources: [
          'https://example.com/source1',
          'https://example.com/source2',
          'https://example.com/source3'
        ],
        createdAt: new Date().toISOString()
      }

      setCurrentSummary(mockSummary)
      setQuery('')
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
                  <button
                    onClick={clearSummary}
                    className="text-xs text-muted-foreground hover:text-foreground"
                  >
                    Clear
                  </button>
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
