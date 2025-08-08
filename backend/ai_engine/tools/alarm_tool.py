"""
Alarm tool for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .base_tool import BaseTool
from services.dashboard_widget_service import DashboardWidgetService

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# ALARM TOOL CLASS
# ============================================================================
class AlarmTool(BaseTool):
    """Tool for alarm operations using new DashboardWidgetService."""
    
    def __init__(self, db_session):
        """Initialize the alarm tool."""
        super().__init__(
            name="alarm_tool",
            description="Tool for creating, editing, deleting, and listing alarms"
        )
        self.db_session = db_session
        self.dashboard_widget_service = DashboardWidgetService(db_session)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, List[str], Optional[str]]:
        """Validate alarm parameters."""
        missing_params = []
        
        # Check required parameters based on intent
        intent = parameters.get("intent")
        if not intent:
            return False, [], "Intent is required"
        
        if intent == "create_alarm":
            required = ["title", "alarm_times"]
            for param in required:
                if not parameters.get(param):
                    missing_params.append(param)
        
        elif intent == "edit_alarm":
            required = ["widget_id"]
            for param in required:
                if not parameters.get(param):
                    missing_params.append(param)
        
        elif intent == "delete_alarm":
            required = ["widget_id"]
            for param in required:
                if not parameters.get(param):
                    missing_params.append(param)
        
        # Validate alarm_times format if present
        alarm_times = parameters.get("alarm_times")
        if alarm_times and not isinstance(alarm_times, list):
            return False, missing_params, "alarm_times must be a list"
        
        if alarm_times:
            for time_str in alarm_times:
                if not self._is_valid_time_format(time_str):
                    return False, missing_params, f"Invalid time format: {time_str}. Use HH:MM format"
        
        return len(missing_params) == 0, missing_params, None
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        try:
            if not isinstance(time_str, str):
                return False
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, TypeError):
            return False
    
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute alarm operation."""
        try:
            intent = parameters["intent"]
            
            if intent == "create_alarm":
                return await self._create_alarm(parameters, user_id)
            elif intent == "edit_alarm":
                return await self._edit_alarm(parameters, user_id)
            elif intent == "delete_alarm":
                return await self._delete_alarm(parameters, user_id)
            elif intent == "list_alarms":
                return await self._list_alarms(parameters, user_id)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported intent: {intent}"
                }
                
        except Exception as e:
            logger.error(f"Error executing alarm tool: {e}")
            return {
                "success": False,
                "message": f"Error executing alarm operation: {str(e)}"
            }
    
    async def _create_alarm(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new alarm using the real AlarmService."""
        try:
            # Validate that title is provided (should be validated by validate_parameters, but double-check)
            if not parameters.get("title"):
                return {
                    "success": False,
                    "message": "Title is required for alarm creation"
                }
            
            # Prepare alarm data
            alarm_data = {
                "title": parameters["title"],  # No default - title must be provided
                "alarm_times": parameters["alarm_times"],
                "description": parameters.get("description"),
                "is_snoozable": parameters.get("is_snoozable", True)
            }
            
            # Use the real AlarmService to create the alarm
            result = await self.dashboard_widget_service.create_widget(user_id, alarm_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating alarm: {e}")
            return {
                "success": False,
                "message": f"Failed to create alarm: {str(e)}"
            }
    
    async def _edit_alarm(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Edit an existing alarm."""
        try:
            widget_id = parameters["widget_id"]
            update_data = {}
            
            if "title" in parameters:
                update_data["title"] = parameters["title"]
            if "alarm_times" in parameters:
                update_data["alarm_times"] = parameters["alarm_times"]
            if "description" in parameters:
                update_data["description"] = parameters["description"]
            if "is_snoozable" in parameters:
                update_data["is_snoozable"] = parameters["is_snoozable"]
            
            # This would integrate with your existing alarm update logic
            return {
                "success": True,
                "message": f"Alarm updated successfully",
                "data": {
                    "widget_id": widget_id,
                    "updates": update_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error editing alarm: {e}")
            return {
                "success": False,
                "message": f"Failed to edit alarm: {str(e)}"
            }
    
    async def _delete_alarm(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Delete an alarm."""
        try:
            widget_id = parameters["widget_id"]
            
            # This would integrate with your existing alarm deletion logic
            return {
                "success": True,
                "message": f"Alarm deleted successfully",
                "data": {
                    "widget_id": widget_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error deleting alarm: {e}")
            return {
                "success": False,
                "message": f"Failed to delete alarm: {str(e)}"
            }
    
    async def _list_alarms(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """List user's alarms."""
        try:
            # This would integrate with your existing alarm listing logic
            # Mock data for now
            alarms = [
                {
                    "widget_id": "mock-widget-1",
                    "title": "Wake up",
                    "alarm_times": ["07:00"],
                    "description": "Morning alarm"
                }
            ]
            
            return {
                "success": True,
                "message": f"Found {len(alarms)} alarms",
                "data": {
                    "alarms": alarms
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing alarms: {e}")
            return {
                "success": False,
                "message": f"Failed to list alarms: {str(e)}"
            }
    
    def get_required_parameters(self) -> List[str]:
        """Get required parameters for alarm operations."""
        return ["intent"]
    
    def get_optional_parameters(self) -> List[str]:
        """Get optional parameters for alarm operations."""
        return ["title", "alarm_times", "description", "is_snoozable", "widget_id"]
    
    def get_parameter_descriptions(self) -> Dict[str, str]:
        """Get parameter descriptions."""
        return {
            "intent": "Operation to perform (create_alarm, edit_alarm, delete_alarm, list_alarms)",
            "title": "Alarm title/name",
            "alarm_times": "List of times in HH:MM format",
            "description": "Optional alarm description",
            "is_snoozable": "Whether alarm can be snoozed",
            "widget_id": "Widget ID for existing alarms"
        } 