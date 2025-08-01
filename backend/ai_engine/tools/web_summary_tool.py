"""
Web Summary Tool for chat-based web summary generation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import Dict, Any
from .base_tool import BaseTool
from orchestrators.ai_orchestrator import AIOrchestrator

# ============================================================================
# WEB SUMMARY TOOL CLASS
# ============================================================================
class WebSummaryTool(BaseTool):
    """Tool for generating web summaries through chat interface."""
    
    def __init__(self, db_session):
        """Initialize the web summary tool."""
        super().__init__(
            name="web_summary_tool",
            description="Generate web summaries for user's websearch widgets",
            parameters={
                "target_date": {
                    "type": "string",
                    "description": "Date for summary generation (YYYY-MM-DD format, defaults to today)",
                    "required": False
                }
            }
        )
        self.ai_orchestrator = AIOrchestrator(db_session)
    
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute web summary generation.
        
        Args:
            parameters: Tool parameters including optional target_date
            user_id: User identifier
            
        Returns:
            Dictionary with operation result
        """
        try:
            result = await self.ai_orchestrator.generate_web_summaries_for_tool(parameters, user_id)
            
            if result["success"]:
                data = result["data"]
                return {
                    "success": True,
                    "message": f"✅ Web summaries generated successfully for {result['target_date']}",
                    "details": {
                        "summaries_generated": data.get("summaries_generated", 0),
                        "date": data.get("date", result["target_date"])
                    },
                    "summary": f"Generated {data.get('summaries_generated', 0)} web summaries for your websearch widgets."
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Failed to generate web summaries: {result['message']}",
                    "details": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error generating web summaries: {str(e)}",
                "details": None
            } 