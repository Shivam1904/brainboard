"""
OpenAI LLM client wrapper with configuration and error handling.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "gpt-3.5-turbo"  # Most cost-effective model
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500  # Reduced for small tasks
DEFAULT_RETRY_ATTEMPTS = 3

# ============================================================================
# LLM CLIENT CLASS
# ============================================================================
class LLMClient:
    """OpenAI API client with configuration and error handling."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", DEFAULT_TEMPERATURE))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", DEFAULT_MAX_TOKENS))
        self.retry_attempts = int(os.getenv("OPENAI_RETRY_ATTEMPTS", DEFAULT_RETRY_ATTEMPTS))
        
        self.client = OpenAI(api_key=self.api_key)
        
    async def call_openai(
        self, 
        messages: list, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_attempts: Optional[int] = None
    ) -> Optional[str]:
        """
        Make a call to OpenAI API with retry logic.
        
        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Override default max tokens
            retry_attempts: Override default retry attempts
            
        Returns:
            Response content or None if failed
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        retries = retry_attempts if retry_attempts is not None else self.retry_attempts
        
        for attempt in range(retries):
            try:
                response: ChatCompletion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens
                )
                
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    logger.warning(f"Empty response from OpenAI on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"OpenAI API call failed on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    logger.error("All retry attempts failed")
                    return None
                    
        return None
    
    def get_token_count(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4 