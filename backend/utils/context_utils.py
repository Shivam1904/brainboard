"""
Context Utilities
Handles context expectations functionality and variable management.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ContextUtils:
    """Utility class for handling context expectations and variable management."""
    
    def __init__(self, variable_config: Dict[str, Any]):
        self.variable_config = variable_config
    
    
    def _get_variables_for_intent(self, intent_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all variables for a specific intent type."""
        try:
            variables = self.variable_config.get('variables', {})
            intent_variables = {}
            
            for var_name, var_config in variables.items():
                if var_config.get('intent_type') == intent_type:
                    intent_variables[var_name] = var_config
            
            return intent_variables
            
        except Exception as e:
            logger.error(f"Failed to get variables for intent {intent_type}: {e}")
            return {}
    