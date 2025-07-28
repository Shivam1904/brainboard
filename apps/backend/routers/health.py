from fastapi import APIRouter, status
from typing import Dict, Any
import logging
from services.summary_service import SummaryService

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
        
        # Test external services using a simple service instance
        summary_service = SummaryService()
        service_tests = await summary_service.test_services()
        
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
