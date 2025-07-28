from typing import Dict, Any
import logging
from openai import AsyncOpenAI
from core.config import settings
from services.base_service import BaseService

logger = logging.getLogger(__name__)

class AISummarizationService(BaseService):
    """Service for AI-powered text summarization using OpenAI"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.default_ai_model
        self.max_tokens = settings.max_summary_tokens
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate summarization input"""
        content = data.get("content", "")
        query = data.get("query", "")
        return (
            isinstance(content, str) and len(content.strip()) > 0 and
            isinstance(query, str) and len(query.strip()) > 0
        )
    
    async def summarize(self, content: str, query: str) -> str:
        """Generate AI summary of content based on the query"""
        try:
            if not await self.validate_input({"content": content, "query": query}):
                raise ValueError("Invalid content or query for summarization")
            
            # Create a focused prompt for better summaries
            prompt = self._create_summary_prompt(content, query)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert summarizer. Create concise, informative summaries that focus on the key points relevant to the user's query."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary of {len(summary)} characters")
            
            return summary
            
        except Exception as e:
            logger.error(f"AI summarization failed: {str(e)}")
            # Return a fallback summary on failure
            return self._create_fallback_summary(content, query)
    
    def _create_summary_prompt(self, content: str, query: str) -> str:
        """Create an effective prompt for summarization"""
        prompt = f"""Please summarize the following web search results related to the query: "{query}"

Focus on:
- Key information directly relevant to the query
- Recent developments and important updates
- Actionable insights or conclusions
- Credible sources and facts

Web Search Results:
{content}

Provide a clear, concise summary in 2-3 paragraphs that answers the user's query."""
        
        return prompt
    
    def _create_fallback_summary(self, content: str, query: str) -> str:
        """Create a simple fallback summary when AI fails"""
        # Extract first few sentences from content as basic fallback
        sentences = content.split('. ')[:3]
        fallback = '. '.join(sentences)
        
        if len(fallback) > 200:
            fallback = fallback[:200] + "..."
        
        return f"Summary for '{query}': {fallback}"
