from fastapi import APIRouter, Depends, status
from typing import Dict, Any
import logging
from services.summary_service import SummaryService
from factories.service_factory import ServiceFactory

logger = logging.getLogger(__name__)

router = APIRouter()

def get_summary_service() -> SummaryService:
    """Get summary service for health checks"""
    return ServiceFactory.create_summary_service()

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
async def detailed_health_check(
    summary_service: SummaryService = Depends(get_summary_service)
) -> Dict[str, Any]:
    """
    Detailed health check that tests external services
    """
    try:
        logger.info("Running detailed health check")
        
        # Test external services
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
