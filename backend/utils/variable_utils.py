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
    
    def get_collected_variables(self, context: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get collected variables organized by required and optional fields."""
        try:
            collected = getattr(context, 'collected_variables', [])
            
            # Organize collected variables by required/optional
            required_fields = []
            optional_fields = []
            
            for var in collected:
                var_name = var.get('name')
                if var_name:
                    var_config = self._find_variable_config(var_name)
                    if var_config:
                        if var_config.get('is_required', False):
                            required_fields.append({var_name: var.get('value', '')})
                        else:
                            optional_fields.append({var_name: var.get('value', '')})
            
            return {
                'required_fields': required_fields,
                'optional_fields': optional_fields
            }
            
        except Exception as e:
            logger.error(f"Failed to get collected variables: {e}")
            return {'required_fields': [], 'optional_fields': []}
    
    def get_missing_variables(self, context: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get missing variables organized by required and optional fields with intent expectations."""
        try:
            missing = getattr(context, 'missing_variables', [])
            
            # Organize missing variables by required/optional
            required_fields = []
            optional_fields = []
            
            for var_name in missing:
                var_config = self._find_variable_config(var_name)
                if var_config:
                    field_info = {
                        'name': var_name,
                        'is_required': var_config.get('is_required', False),
                        'input_by': var_config.get('forAI_fallback_suggestion_type', 'ask'),
                        'suggestion': var_config.get('forAI_fallback_suggestion', '')
                    }
                    
                    if var_config.get('is_required', False):
                        required_fields.append(field_info)
                    else:
                        optional_fields.append(field_info)
            
            return {
                'required_fields': required_fields,
                'optional_fields': optional_fields
            }
            
        except Exception as e:
            logger.error(f"Failed to get missing variables: {e}")
            return {'required_fields': [], 'optional_fields': []}
    
    def format_collected_variables(self, data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Format collected variables for prompt."""
        if not data or not isinstance(data, dict):
            return None
        
        required_fields = data.get('required_fields', [])
        optional_fields = data.get('optional_fields', [])
        
        formatted = ["=== Collected Variables ==="]
        if required_fields:
            formatted.append("Required Fields:")
            for var in required_fields:
                formatted.append(f"- {var.get('name', 'unknown')}: {var.get('value', 'no value')}")
        
        if optional_fields:
            formatted.append("Optional Fields:")
            for var in optional_fields:
                formatted.append(f"- {var.get('name', 'unknown')}: {var.get('value', 'no value')}")
        
        return "\n".join(formatted)
    
    def format_missing_variables(self, data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Format missing variables for prompt."""
        if not data or not isinstance(data, dict):
            return None
        
        required_fields = data.get('required_fields', [])
        optional_fields = data.get('optional_fields', [])
        
        formatted = ["=== Missing Variables ==="]
        if required_fields:
            formatted.append("Required Fields:")
            for var in required_fields:
                formatted.append(f"- {var.get('name', 'unknown')}: {var.get('description', 'no description')}")
                if var.get('fallback_suggestion'):
                    formatted.append(f"  Fallback: {var.get('fallback_suggestion')}")
        
        if optional_fields:
            formatted.append("Optional Fields:")
            for var in optional_fields:
                formatted.append(f"- {var.get('name', 'unknown')}: {var.get('description', 'no description')}")
                if var.get('fallback_suggestion'):
                    formatted.append(f"  Fallback: {var.get('fallback_suggestion')}")
        
        return "\n".join(formatted) 