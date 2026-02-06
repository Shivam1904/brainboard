"""
Variable Utilities
Handles collected and missing variables functionality.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class VariableUtils:
    """Utility class for handling collected and missing variables."""
    
    def __init__(self, variable_config: Dict[str, Any]):
        self.variable_config = variable_config
    
    def _find_variable_config(self, var_name: str) -> Optional[Dict[str, Any]]:
        """Find variable configuration in variable config file."""
        variables = self.variable_config.get('variables', {})
        return variables.get(var_name)
    
    def get_collected_variables(self, context: Any) -> Dict[str, Any]:
        """Get collected variables from context."""
        try:
            collected = getattr(context, 'collected_variables', {})
            # Include current intent in collected variables if available
            if hasattr(context, 'current_intent') and getattr(context, 'current_intent'):
                collected = collected.copy()  # Create a copy to avoid modifying the original
                collected['intent'] = getattr(context, 'current_intent')
            return collected
        except Exception as e:
            logger.error(f"Failed to get collected variables: {e}")
            return {}
    
    def get_missing_variables(self, context: Any) -> List[Dict[str, Any]]:
        """Get missing variables from context."""
        try:
            return getattr(context, 'missing_variables', [])
        except Exception as e:
            logger.error(f"Failed to get missing variables: {e}")
            return []
    
    def format_collected_variables(self, context_or_data: Any) -> Optional[str]:
        """Format collected variables for prompt."""
        try:
            # Handle both context objects and direct data dictionaries
            if hasattr(context_or_data, 'collected_variables'):
                collected = getattr(context_or_data, 'collected_variables', {})
            else:
                # Assume it's the data dictionary itself
                collected = context_or_data if isinstance(context_or_data, dict) else {}
            
            if not collected:
                return None
            
            # print(f"🔍 Formatting collected variables: {collected}")
            
            formatted = ["CTX: Collected Variables"]
            for var_name, value in collected.items():
                if value is not None and value != "":
                    formatted.append(f" - {var_name}: \"{value}\"")
            
            # If no valid variables, return None
            if len(formatted) == 1:  # Only header
                return None
            
            result = "\n".join(formatted)
            # print(f"🔍 Formatted collected variables result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to format collected variables: {e}")
            return None
    
    def format_missing_variables(self, context_or_data: Any) -> Optional[str]:
        """Format missing variables for prompt."""
        try:
            # Handle both context objects and direct data dictionaries
            if hasattr(context_or_data, 'missing_variables'):
                missing = getattr(context_or_data, 'missing_variables', [])
            else:
                # Assume it's the data list itself
                missing = context_or_data if isinstance(context_or_data, list) else []
            
            if not missing:
                return None
            
            formatted = ["CTX: Missing"]
            for var_info in missing:
                var_name = var_info.get('name', '')
                description = var_info.get('description', '')
                is_required = var_info.get('is_required', False)
                required_text = "(REQUIRED)" if is_required else ""
                intent_text = var_info.get('ai_must', '')
                
                formatted.append(f" - {var_name} {required_text} {': ' + description if description else ''} {'*' + intent_text + '*' if intent_text else ''}")
                
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Failed to format missing variables: {e}")
            return None
    
    def get_intent_text(self, context_or_data: Any) -> Optional[str]:
        """Get intent text from collected variables."""
        try:
            # Handle both context objects and direct data dictionaries
            if hasattr(context_or_data, 'collected_variables'):
                collected = getattr(context_or_data, 'collected_variables', {})
            else:
                # Assume it's the data dictionary itself
                collected = context_or_data if isinstance(context_or_data, dict) else {}
            
            if not collected:
                return None
            
            # print(f"🔍 Formatting collected variables: {collected}")
            
            for var_name, value in collected.items():
                if value is not None and value != "":
                    if var_name == 'intent':
                        return value
                    
            return None
        except Exception as e:
            logger.error(f"Failed to format intent text: {e}")
            return None
    
    def validate_variable_value(self, var_name: str, value: Any) -> bool:
        """Validate a variable value against its configuration."""
        try:
            var_config = self._find_variable_config(var_name)
            if not var_config:
                return False
            
            validation_type = var_config.get('forEngine_validation')
            if not validation_type:
                return True
            
            # Basic validation based on validation type
            if validation_type == 'non_empty_string':
                return isinstance(value, str) and value.strip() != ''
            elif validation_type == 'valid_date':
                # Basic date validation - could be enhanced
                return isinstance(value, str) and len(value) > 0
            elif validation_type == 'integer_0_to_100':
                return isinstance(value, int) and 0 <= value <= 100
            elif validation_type == 'milestone_list':
                return isinstance(value, list) and all(isinstance(item, dict) for item in value)
            elif validation_type == 'time_list':
                return isinstance(value, list) and all(isinstance(item, str) for item in value)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate variable {var_name}: {e}")
            return False 