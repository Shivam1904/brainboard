"""
Intent Configuration Utilities
Handles intent configuration functionality.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class IntentConfigUtils:
    """Utility class for handling intent configuration."""
    
    def __init__(self, variable_config: Dict[str, Any]):
        self.variable_config = variable_config
    
    def get_intent_configuration(self) -> List[Dict[str, Any]]:
        """Get intent configuration as a simple list."""
        try:
            intent_list = []
            
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
            
            # Build simple list for each intent
            for intent_name, intent_vars in intent_groups.items():
                intent_config = {
                    'intent': intent_name,
                    'required_fields': [],
                    'optional_fields': []
                }
                
                # Process variables for this intent
                for var_name, var_config in intent_vars:
                    field_info = {
                        'var_name': var_name,
                        'description': var_config.get('description', ''),
                        'structure': var_config.get('forEngine_structure', ''),
                        'is_required': var_config.get('is_required', False),
                        'suggestion': var_config.get('forAI_fallback_suggestion', ''),
                        'suggestion_type': var_config.get('forAI_fallback_suggestion_type', '')
                    }
                    
                    if var_config.get('is_required', False):
                        intent_config['required_fields'].append(field_info)
                    else:
                        intent_config['optional_fields'].append(field_info)
                
                intent_list.append(intent_config)
            
            return intent_list
            
        except Exception as e:
            logger.error(f"Failed to get intent configuration: {e}")
            return []
    
    def format_intent_config(self, config: List[Dict[str, Any]]) -> str:
        """Format intent configuration for prompt."""
        if not config:
            return ""
        
        formatted = []
        for intent_data in config:
            formatted.append(f"intent: \"{intent_data.get('intent', '')}\"")            
            # Format required fields
            if intent_data.get('required_fields'):
                formatted.append(f"  Required:")
                s= ''
                for field in intent_data['required_fields']:
                    s += f" \"{field.get('var_name', '')}\": {field.get('description', '')},"
                formatted.append(f"[{s}]")
            
            # Format optional fields
            if intent_data.get('optional_fields'):
                formatted.append(f"  Optional:")
                s= ''
                for field in intent_data['optional_fields']:
                    s += f" \"{field.get('var_name', '')}\": {field.get('description', '')},"
                formatted.append(f"[{s}]")
        formatted.append(f"")            
            
        
        return "\n".join(formatted) 