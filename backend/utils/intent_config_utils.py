"""
Intent Configuration Utilities
Handles intent configuration functionality.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IntentConfigUtils:
    """Utility class for handling intent configuration."""
    
    def __init__(self, variable_config: Dict[str, Any]):
        self.variable_config = variable_config
    
    def get_intent_configuration(self) -> Dict[str, Any]:
        """Get intent configuration with required and optional fields."""
        try:
            formatted_config = {}
            
            # Get all variables from variable_config.yaml
            variables = self.variable_config.get('variables', {})
            # Group variables by intent_type
            intent_groups = {}
            for var_name, var_config in variables.items():
                intent_type = var_config.get('intent_type')
                if intent_type:
                    if intent_type not in intent_groups:
                        intent_groups[intent_type] = []
                    intent_groups[intent_type].append((var_name, var_config))
            
            # Build formatted configuration for each intent
            for intent_name, intent_vars in intent_groups.items():
                formatted_intent = {
                    'name': intent_name,
                    'description': f"Intent for {intent_name} operations",
                    'required_fields': [],
                    'optional_fields': []
                }
                
                # Process variables for this intent
                for var_name, var_config in intent_vars:
                    field_info = {
                        'name': var_name,
                        'description': var_config.get('description', ''),
                        'structure': var_config.get('forEngine_structure', ''),
                        'fallback_suggestion_type': var_config.get('forAI_fallback_suggestion_type', ''),
                        'fallback_suggestion': var_config.get('forAI_fallback_suggestion', ''),
                    }
                    
                    if var_config.get('is_required', False):
                        formatted_intent['required_fields'].append(field_info)
                    else:
                        formatted_intent['optional_fields'].append(field_info)
                
                formatted_config[intent_name] = formatted_intent
            
            return formatted_config
            
        except Exception as e:
            logger.error(f"Failed to get intent configuration: {e}")
            return {}
    
    def format_intent_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Format intent configuration for prompt."""
        if not config:
            return None
        
        formatted = []
        for intent_name, intent_data in config.items():
            if isinstance(intent_data, dict):
                formatted.append(f"Intent: {intent_name}")
                # Format required fields
                if intent_data.get('required_fields'):
                    formatted.append("Required Fields:")
                    for field in intent_data['required_fields']:
                        formatted.append(f"  - {field.get('name', 'unknown')}: {field.get('description', 'no description')}")
                        if field.get('forAI_fallback_suggestion'):
                            formatted.append(f"    Fallback: {field.get('forAI_fallback_suggestion')}")
                
                # Format optional fields
                if intent_data.get('optional_fields'):
                    formatted.append("Optional Fields:")
                    for field in intent_data['optional_fields']:
                        formatted.append(f"  - {field.get('name', 'unknown')}: {field.get('description', 'no description')}")
                        if field.get('forAI_fallback_suggestion'):
                            formatted.append(f"    Fallback: {field.get('forAI_fallback_suggestion')}")
                
                formatted.append("")
        
        return "\n".join(formatted) 