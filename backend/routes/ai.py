"""
AI routes for direct API access to AI operations.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from db.dependency import get_db_session_dependency
from orchestrators.ai_orchestrator import AIOrchestrator
from schemas.ai import (
    DailyPlanResponse, WebSummaryResponse, ActivityGenerationResponse,
    AIErrorResponse
)

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter(prefix="/api/v1/ai", tags=["AI Operations"])

# Default user ID for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_default_user_id() -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

# ============================================================================
# AI ENDPOINTS
# ============================================================================

@router.post("/generate_today_plan", response_model=DailyPlanResponse)
async def generate_today_plan(
    target_date: Optional[date] = Query(None, description="Date for plan generation (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Generate today's plan using AI.
    
    This endpoint:
    - Processes permanent widgets directly to daily widgets
    - Uses AI to select and prioritize non-permanent widgets
    - Stores AI outputs in the database
    - Returns summary of the operation
    """
    try:
        ai_orchestrator = AIOrchestrator(db)
        result = await ai_orchestrator.generate_daily_plan_for_api(user_id, target_date)
        
        return DailyPlanResponse(
            status=result["status"],
            message=result["message"],
            data=result["data"],
            target_date=result["target_date"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate today's plan: {str(e)}"
        )

@router.post("/generate_web_summary_list", response_model=WebSummaryResponse)
async def generate_web_summary_list(
    target_date: Optional[date] = Query(None, description="Date for summary generation (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Generate web summaries for user's websearch widgets.
    
    This endpoint:
    - Finds all websearch widgets for the user
    - Performs web searches using Serper API
    - Generates AI summaries using OpenAI
    - Stores summaries in the database
    - Returns summary of the operation
    """
    try:
        ai_orchestrator = AIOrchestrator(db)
        result = await ai_orchestrator.generate_web_summaries_for_api(user_id, target_date)
        
        return WebSummaryResponse(
            status=result["status"],
            message=result["message"],
            data=result["data"],
            target_date=result["target_date"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate web summaries: {str(e)}"
        )

@router.post("/generate_activity_from_plan", response_model=ActivityGenerationResponse)
async def generate_activity_from_plan(
    target_date: Optional[date] = Query(None, description="Date for activity generation (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Generate activities from AI outputs.
    
    This endpoint:
    - Retrieves AI outputs for the specified date
    - Creates daily widgets for selected widgets
    - Creates activity entries for each widget type
    - Returns summary of the operation
    """
    try:
        ai_orchestrator = AIOrchestrator(db)
        result = await ai_orchestrator.generate_activity_from_plan_for_api(user_id, target_date)
        
        return ActivityGenerationResponse(
            status=result["status"],
            message=result["message"],
            data=result["data"],
            target_date=result["target_date"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate activities from plan: {str(e)}"
        )

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get("/health")
async def ai_health_check(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Check the health of AI services.
    
    This endpoint:
    - Verifies AI orchestrator is operational
    - Checks database connectivity
    - Returns health status
    """
    try:
        ai_orchestrator = AIOrchestrator(db)
        health_result = await ai_orchestrator.health_check()
        
        return {
            "status": "healthy",
            "ai_orchestrator": health_result,
            "message": "AI services are operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "ai_orchestrator": {
                "status": "unhealthy",
                "message": f"AI orchestrator health check failed: {str(e)}"
            },
            "message": "AI services are not operational"
        } 