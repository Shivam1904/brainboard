from typing import Dict, Any, List
import logging
from datetime import datetime
from services.base_service import BaseService
from services.web_search_service import WebSearchService, SearchResult
from services.ai_summarization_service import AISummarizationService
from models.schemas import SummaryResponse

logger = logging.getLogger(__name__)

class SummaryService(BaseService):
    """Orchestrates web search + AI summarization for complete summary generation"""
    
    def __init__(self, web_search: WebSearchService = None, ai_service: AISummarizationService = None):
        self.web_search = web_search or WebSearchService()
        self.ai_service = ai_service or AISummarizationService()
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate summary generation input"""
        query = data.get("query", "")
        return isinstance(query, str) and len(query.strip()) > 0
    
    async def generate_summary(self, query: str, summary_id: str) -> SummaryResponse:
        """
        Generate a complete summary by:
        1. Searching the web for relevant content
        2. Extracting and processing the content
        3. Using AI to create a focused summary
        4. Returning structured response
        """
        try:
            if not await self.validate_input({"query": query}):
                raise ValueError("Invalid query for summary generation")
            
            logger.info(f"Starting summary generation for query: {query}")
            
            # Step 1: Search the web
            search_results = await self.web_search.search(query)
            
            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                return self._create_empty_summary(query, summary_id)
            
            # Step 2: Extract content from search results
            content = self.web_search.extract_content_from_results(search_results)
            
            # Step 3: Generate AI summary
            summary_text = await self.ai_service.summarize(content, query)
            
            # Step 4: Extract source URLs
            sources = [result.url for result in search_results]
            
            # Step 5: Create structured response
            summary_response = SummaryResponse(
                id=summary_id,
                query=query,
                summary=summary_text,
                sources=sources,
                createdAt=datetime.utcnow().isoformat() + "Z"
            )
            
            logger.info(f"Successfully generated summary for query: {query}")
            return summary_response
            
        except Exception as e:
            logger.error(f"Summary generation failed for query '{query}': {str(e)}")
            return self._create_error_summary(query, summary_id, str(e))
    
    def _create_empty_summary(self, query: str, summary_id: str) -> SummaryResponse:
        """Create a summary response when no search results are found"""
        return SummaryResponse(
            id=summary_id,
            query=query,
            summary=f"No recent information found for '{query}'. Please try a different search term or check back later.",
            sources=[],
            createdAt=datetime.utcnow().isoformat() + "Z"
        )
    
    def _create_error_summary(self, query: str, summary_id: str, error_message: str) -> SummaryResponse:
        """Create a summary response when an error occurs"""
        return SummaryResponse(
            id=summary_id,
            query=query,
            summary=f"Sorry, we encountered an issue generating a summary for '{query}'. Please try again later.",
            sources=[],
            createdAt=datetime.utcnow().isoformat() + "Z"
        )
    
    async def test_services(self) -> Dict[str, Any]:
        """Test both web search and AI services for health check"""
        test_results = {
            "web_search": False,
            "ai_summarization": False,
            "overall": False
        }
        
        try:
            # Test web search
            search_results = await self.web_search.search("test query")
            test_results["web_search"] = True
            logger.info("Web search service is working")
        except Exception as e:
            logger.error(f"Web search service test failed: {str(e)}")
        
        try:
            # Test AI summarization with dummy content
            summary = await self.ai_service.summarize("This is test content.", "test")
            test_results["ai_summarization"] = len(summary) > 0
            logger.info("AI summarization service is working")
        except Exception as e:
            logger.error(f"AI summarization service test failed: {str(e)}")
        
        test_results["overall"] = test_results["web_search"] and test_results["ai_summarization"]
        return test_results
