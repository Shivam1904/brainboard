import httpx
import openai
from typing import Dict, Any, List
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered features using OpenAI and Serper.dev"""
    
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            logger.warning("OpenAI API key not set. AI features will be limited.")
    
    async def search_web(self, query: str) -> Dict[str, Any]:
        """
        Search the web using Serper.dev API
        """
        if not settings.serper_api_key:
            logger.warning("Serper API key not set. Using mock data.")
            return self._mock_search_results(query)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": settings.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={"q": query, "num": 5}
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return self._mock_search_results(query)
    
    async def summarize_content(self, query: str, search_results: Dict[str, Any]) -> str:
        """
        Summarize search results using OpenAI GPT
        """
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not set. Using mock summary.")
            return self._mock_summary(query)
        
        try:
            # Extract relevant content from search results
            content_pieces = []
            
            for result in search_results.get('organic', []):
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                if title and snippet:
                    content_pieces.append(f"Title: {title}\nSnippet: {snippet}")
            
            if not content_pieces:
                return "No relevant content found for summarization."
            
            content = "\n\n".join(content_pieces[:5])  # Limit to top 5 results
            
            # Create OpenAI prompt
            prompt = f"""
            Please provide a comprehensive summary based on the following search results for the query: "{query}"
            
            Search Results:
            {content}
            
            Instructions:
            - Provide a clear, concise summary that answers the user's query
            - Include the most important and relevant information
            - Structure the response in a readable format
            - If there are conflicting information, mention it
            - Keep the summary between 150-300 words
            """
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate summaries based on search results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self._mock_summary(query)
    
    def _mock_search_results(self, query: str) -> Dict[str, Any]:
        """Mock search results for development"""
        return {
            "organic": [
                {
                    "title": f"Information about {query}",
                    "link": "https://example.com/result1",
                    "snippet": f"This is relevant information about {query}. It provides key insights and details that users are looking for."
                },
                {
                    "title": f"Complete guide to {query}",
                    "link": "https://example.com/result2", 
                    "snippet": f"A comprehensive overview of {query} including best practices, tips, and detailed explanations."
                },
                {
                    "title": f"Latest updates on {query}",
                    "link": "https://example.com/result3",
                    "snippet": f"Recent developments and news related to {query}. Stay informed with the latest trends and changes."
                }
            ]
        }
    
    def _mock_summary(self, query: str) -> str:
        """Mock summary for development"""
        return f"""Based on the available information about "{query}", here's a comprehensive summary:

        This topic encompasses several important aspects that are worth understanding. The key findings suggest that {query} involves multiple considerations and factors that influence its overall impact and relevance.

        Key points include:
        • Primary characteristics and defining features
        • Current trends and developments in this area
        • Practical applications and use cases
        • Potential challenges and considerations

        The information indicates that {query} continues to evolve, with new developments and insights emerging regularly. This makes it an important area to monitor for anyone interested in staying current with the latest information.

        For the most accurate and up-to-date information, it's recommended to consult multiple sources and verify findings through reliable channels."""
