"""
Tool registry for managing and executing AI chat tools.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging
from typing import Dict, Any, Optional
from .base_tool import BaseTool

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# TOOL REGISTRY CLASS
# ============================================================================
class ToolRegistry:
    """Registry for managing and executing AI chat tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not found"
            }
        
        try:
            # Validate parameters
            is_valid, missing_params, error_msg = tool.validate_parameters(parameters)
            if not is_valid:
                return {
                    "success": False,
                    "message": error_msg or f"Missing parameters: {missing_params}",
                    "missing_parameters": missing_params
                }
            
            # Execute tool
            result = await tool.execute(parameters, user_id)
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "message": f"Error executing tool: {str(e)}"
            }
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool."""
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "required_parameters": tool.get_required_parameters(),
            "optional_parameters": tool.get_optional_parameters(),
            "parameter_descriptions": tool.get_parameter_descriptions()
        }
    
    def get_all_tool_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered tools."""
        return {
            tool_name: self.get_tool_info(tool_name)
            for tool_name in self.list_tools()
        } 