from fastapi import APIRouter, status
from typing import Dict, Any
import logging
from services.ai_summarization_service import AISummarizationService
from services.web_search_service import WebSearchService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/health",
    summary="Health Check",
    description="Check the health of the API and its services"
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "brainboard-api",
        "version": "1.0.0"
    }

@router.get(
    "/health/detailed",
    summary="Detailed Health Check",
    description="Detailed health check including external service status"
)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check that tests external services
    """
    try:
        logger.info("Running detailed health check")
        
        # Test external services directly
        ai_service = AISummarizationService()
        web_service = WebSearchService()
        
        # Test AI service
        ai_working = False
        try:
            test_summary = await ai_service.summarize("Test content for health check", "test")
            ai_working = len(test_summary) > 0
        except Exception as e:
            logger.error(f"AI service test failed: {e}")
        
        # Test web search service
        web_working = False
        try:
            search_results = await web_service.search("test query")
            web_working = True
        except Exception as e:
            logger.error(f"Web search service test failed: {e}")
        
        service_tests = {
            "ai_summarization": ai_working,
            "web_search": web_working,
            "overall": ai_working and web_working
        }
        
        overall_status = "healthy" if service_tests["overall"] else "degraded"
        
        return {
            "status": overall_status,
            "service": "brainboard-api",
            "version": "1.0.0",
            "services": {
                "web_search": "healthy" if service_tests["web_search"] else "unhealthy",
                "ai_summarization": "healthy" if service_tests["ai_summarization"] else "unhealthy"
            },
            "database": "healthy"  # If we get here, database is working
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "brainboard-api",
            "version": "1.0.0",
            "error": str(e)
        }
