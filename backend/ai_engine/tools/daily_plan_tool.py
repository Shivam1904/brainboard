"""
Daily Plan Tool for chat-based daily plan generation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any
from .base_tool import BaseTool
from orchestrators.ai_orchestrator import AIOrchestrator

# ============================================================================
# DAILY PLAN TOOL CLASS
# ============================================================================
class DailyPlanTool(BaseTool):
    """Tool for generating AI daily plans through chat interface."""
    
    def __init__(self, db_session):
        """Initialize the daily plan tool."""
        super().__init__(
            name="daily_plan_tool",
            description="Generate AI daily plans for user widgets",
            parameters={
                "target_date": {
                    "type": "string",
                    "description": "Date for plan generation (YYYY-MM-DD format, defaults to today)",
                    "required": False
                }
            }
        )
        self.ai_orchestrator = AIOrchestrator(db_session)
    
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute daily plan generation.
        
        Args:
            parameters: Tool parameters including optional target_date
            user_id: User identifier
            
        Returns:
            Dictionary with operation result
        """
        try:
            result = await self.ai_orchestrator.generate_daily_plan_for_tool(parameters, user_id)
            
            if result["success"]:
                data = result["data"]
                return {
                    "success": True,
                    "message": f"✅ Daily plan generated successfully for {result['target_date']}",
                    "details": {
                        "widgets_processed": data.get("widgets_processed", 0),
                        "permanent_widgets_added": data.get("permanent_widgets_added", 0),
                        "ai_widgets_processed": data.get("ai_widgets_processed", 0),
                        "date": data.get("date", result["target_date"])
                    },
                    "summary": f"Processed {data.get('widgets_processed', 0)} widgets: {data.get('permanent_widgets_added', 0)} permanent widgets added directly, {data.get('ai_widgets_processed', 0)} widgets processed by AI."
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Failed to generate daily plan: {result['message']}",
                    "details": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error generating daily plan: {str(e)}",
                "details": None
            } 