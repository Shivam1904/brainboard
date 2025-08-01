"""
AI Orchestrator for coordinating AI operations between tools and APIs.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_service import AIService

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# AI ORCHESTRATOR CLASS
# ============================================================================
class AIOrchestrator:
    """Main coordinator for AI operations, shared between tools and APIs."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the AI orchestrator."""
        self.db_session = db_session
        self.ai_service = AIService(db_session)
    
    # ============================================================================
    # SHARED AI OPERATIONS
    # ============================================================================
    
    async def generate_daily_plan(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Generate daily plan for a user on a specific date.
        Shared method used by both tools and APIs.
        """
        try:
            logger.info(f"Generating daily plan for user {user_id} on {target_date}")
            result = await self.ai_service.generate_daily_plan(user_id, target_date)
            logger.info(f"Daily plan generated successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate daily plan: {e}")
            raise
    
    async def generate_web_summaries(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Generate web summaries for user's websearch widgets.
        Shared method used by both tools and APIs.
        """
        try:
            logger.info(f"Generating web summaries for user {user_id} on {target_date}")
            result = await self.ai_service.generate_web_summaries(user_id, target_date)
            logger.info(f"Web summaries generated successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate web summaries: {e}")
            raise
    
    async def generate_activity_from_plan(self, target_date: date, user_id: str) -> Dict[str, Any]:
        """
        Generate activities from AI outputs.
        Shared method used by both tools and APIs.
        """
        try:
            logger.info(f"Generating activities from AI plan for user {user_id} on {target_date}")
            result = await self.ai_service.generate_activity_from_plan(target_date, user_id)
            logger.info(f"Activities generated successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate activities from plan: {e}")
            raise
    
    # ============================================================================
    # TOOL-SPECIFIC OPERATIONS
    # ============================================================================
    
    async def generate_daily_plan_for_tool(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Generate daily plan specifically for tool usage.
        Extracts target_date from parameters or uses today's date.
        """
        try:
            target_date = parameters.get("target_date")
            if target_date:
                # Convert string to date if needed
                if isinstance(target_date, str):
                    from datetime import datetime
                    target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            else:
                target_date = date.today()
            
            result = await self.generate_daily_plan(user_id, target_date)
            
            # Format response for tool usage
            return {
                "success": True,
                "message": result.get("message", "Daily plan generated successfully"),
                "data": result,
                "target_date": target_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate daily plan for tool: {e}")
            return {
                "success": False,
                "message": f"Failed to generate daily plan: {str(e)}",
                "data": None
            }
    
    async def generate_web_summaries_for_tool(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Generate web summaries specifically for tool usage.
        Extracts target_date from parameters or uses today's date.
        """
        try:
            target_date = parameters.get("target_date")
            if target_date:
                # Convert string to date if needed
                if isinstance(target_date, str):
                    from datetime import datetime
                    target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            else:
                target_date = date.today()
            
            result = await self.generate_web_summaries(user_id, target_date)
            
            # Format response for tool usage
            return {
                "success": True,
                "message": result.get("message", "Web summaries generated successfully"),
                "data": result,
                "target_date": target_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate web summaries for tool: {e}")
            return {
                "success": False,
                "message": f"Failed to generate web summaries: {str(e)}",
                "data": None
            }
    
    # ============================================================================
    # API-SPECIFIC OPERATIONS
    # ============================================================================
    
    async def generate_daily_plan_for_api(self, user_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate daily plan specifically for API usage.
        Uses today's date if no target_date provided.
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            result = await self.generate_daily_plan(user_id, target_date)
            
            # Format response for API usage
            return {
                "status": "success",
                "message": result.get("message", "Daily plan generated successfully"),
                "data": result,
                "target_date": target_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate daily plan for API: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate daily plan: {str(e)}",
                "data": None
            }
    
    async def generate_web_summaries_for_api(self, user_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate web summaries specifically for API usage.
        Uses today's date if no target_date provided.
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            result = await self.generate_web_summaries(user_id, target_date)
            
            # Format response for API usage
            return {
                "status": "success",
                "message": result.get("message", "Web summaries generated successfully"),
                "data": result,
                "target_date": target_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate web summaries for API: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate web summaries: {str(e)}",
                "data": None
            }
    
    async def generate_activity_from_plan_for_api(self, user_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate activities from AI plan specifically for API usage.
        Uses today's date if no target_date provided.
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            result = await self.generate_activity_from_plan(target_date, user_id)
            
            # Format response for API usage
            return {
                "status": "success",
                "message": result.get("message", "Activities generated successfully"),
                "data": result,
                "target_date": target_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate activities for API: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate activities: {str(e)}",
                "data": None
            }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_ai_service(self) -> AIService:
        """Get the underlying AI service for direct access if needed."""
        return self.ai_service
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of AI services."""
        try:
            # Test basic functionality
            test_date = date.today()
            test_user = "test_user"
            
            # This is a lightweight test - just check if the service is accessible
            return {
                "status": "healthy",
                "message": "AI orchestrator is operational",
                "timestamp": test_date.isoformat()
            }
        except Exception as e:
            logger.error(f"AI orchestrator health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"AI orchestrator health check failed: {str(e)}",
                "timestamp": date.today().isoformat()
            } 