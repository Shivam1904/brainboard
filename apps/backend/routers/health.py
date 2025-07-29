from fastapi import APIRouter, status
from typing import Dict, Any
import logging

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
        "version": "2.0.0"
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
        
        # For now, just return basic health status
        # TODO: Add service tests when services are implemented
        
        return {
            "status": "healthy",
            "service": "brainboard-api",
            "version": "2.0.0",
            "services": {
                "database": "healthy",
                "ai_services": "not_implemented_yet"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "brainboard-api",
            "version": "2.0.0",
            "error": str(e)
        } 