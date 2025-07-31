"""
Abstract base tool interface for AI chat functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# ============================================================================
# BASE TOOL CLASS
# ============================================================================
class BaseTool(ABC):
    """Abstract base class for all AI chat tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize the base tool."""
        self.name = name
        self.description = description
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, List[str], Optional[str]]:
        """
        Validate parameters for tool execution.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, missing_parameters, error_message)
        """
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            parameters: Validated parameters
            user_id: User identifier
            
        Returns:
            Execution result
        """
        pass
    
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameters for this tool."""
        return []
    
    def get_optional_parameters(self) -> List[str]:
        """Get list of optional parameters for this tool."""
        return []
    
    def get_parameter_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all parameters."""
        return {} 