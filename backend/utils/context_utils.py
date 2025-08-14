"""
Context Utilities
Handles context expectations functionality.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ContextUtils:
    """Utility class for handling context expectations."""
    
    def __init__(self, variable_config: Dict[str, Any]):
        self.variable_config = variable_config
    
    def get_context_expectations(self, context: Any) -> str:
        """Get context expectations based on intent and variables."""
        try:
            intent_type = getattr(context, 'current_intent', 'unknown')
            collected_vars = getattr(context, 'collected_variables', [])
            missing_vars = getattr(context, 'missing_variables', [])
            context_round = getattr(context, 'round', 'normal')
            
            expectations = []
            
            # Check if this is a try_harder round and intent is found
            if context_round == 'try_harder' and intent_type != 'unknown':
                # Get intent-specific expectations from variable config for all missing variables
                for var_name in missing_vars:
                    var_config = self._find_variable_config(var_name)
                    if var_config and var_config.get('forAI_intent_expectation_text'):
                        expectations.append(f"{var_name}: {var_config['forAI_intent_expectation_text']}")
            
            # Add general intent expectations
            if intent_type == "discussing":
                expectations.append("When discussing, AI should do google searches and create summary of the topic and try to find gameplan for the user on the topic in mind and make some suggestions to the user. Try to organize the conversation in a way that is easy to follow and understand. Try to help the user with his thoughts and half baked ideas. Try to be helpful and supportive. Try to be concise and to the point.")
            
            if collected_vars:
                expectations.append("Here is some more data about the habits of the user and what activity he has done.")
            
            if expectations:
                return "\n".join(expectations)
            
            return f"Context expectations for {intent_type} intent"
            
        except Exception as e:
            logger.error(f"Failed to get context expectations: {e}")
            return "Unable to determine context expectations"
    
    def _find_variable_config(self, var_name: str) -> Optional[Dict[str, Any]]:
        """Find variable configuration in variable config file."""
        variables = self.variable_config.get('variables', {})
        return variables.get(var_name) 