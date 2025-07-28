from typing import List, Dict, Any
import httpx
import logging
from core.config import settings
from services.base_service import BaseService

logger = logging.getLogger(__name__)

class SearchResult:
    """Data class for search results"""
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet

class WebSearchService(BaseService):
    """Service for web search using Serper.dev API"""
    
    def __init__(self):
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate search input"""
        query = data.get("query", "")
        return isinstance(query, str) and len(query.strip()) > 0
    
    async def search(self, query: str) -> List[SearchResult]:
        """Search the web using Serper.dev API"""
        try:
            if not await self.validate_input({"query": query}):
                raise ValueError("Invalid search query")
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": settings.max_search_results
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return self._parse_search_results(data)
                
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            # Return empty results on failure for graceful degradation
            return []
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[SearchResult]:
        """Parse Serper.dev API response into SearchResult objects"""
        results = []
        
        # Get organic search results
        organic_results = data.get("organic", [])
        
        for result in organic_results:
            title = result.get("title", "")
            url = result.get("link", "")
            snippet = result.get("snippet", "")
            
            if title and url:
                results.append(SearchResult(title=title, url=url, snippet=snippet))
        
        logger.info(f"Found {len(results)} search results")
        return results
    
    def extract_content_from_results(self, results: List[SearchResult]) -> str:
        """Extract text content from search results for summarization"""
        content_parts = []
        
        for result in results:
            content_part = f"Title: {result.title}\nURL: {result.url}\nContent: {result.snippet}\n"
            content_parts.append(content_part)
        
        combined_content = "\n---\n".join(content_parts)
        logger.info(f"Extracted {len(combined_content)} characters of content")
        
        return combined_content
