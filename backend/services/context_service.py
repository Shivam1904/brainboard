"""
Context Service
Manages context variables and updates context with AI responses.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextService:
    """Service for managing context variables and updates."""
    
    def __init__(self):
        """Initialize the context service."""
        pass
    
    async def update_context(self, ai_response: Dict[str, Any], context: Any, user_message: str) -> Any:
        """
        Update context with AI response data.
        
        Args:
            ai_response: Validated AI response
            context: Current context object
            user_message: User's input message
            
        Returns:
            Updated context object
        """
        # Add user message to conversation history
        user_message_obj = {
            "role": "user",
            "msg": user_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if not hasattr(context, 'user_chats'):
            context.user_chats = []
        context.user_chats.append(user_message_obj)
        
        # Add AI response to conversation history
        ai_message_obj = {
            "role": "assistant", 
            "msg": str(ai_response),
            "timestamp": datetime.now().isoformat()
        }
        context.user_chats.append(ai_message_obj)
        
        # Store entire AI response
        context.ai_response = ai_response
        
        # Update timestamps
        if hasattr(context, 'last_updated'):
            context.last_updated = datetime.now().isoformat()
        
        logger.info(f"Context updated for connection: {getattr(context, 'connection_id', 'unknown')}")
        return context
    
    async def update_conversation_history(self, user_message: str, context: Any) -> Any:
        """
        Update conversation history in context with user message.
        
        Args:
            user_message: User's input message
            context: Current context object
            
        Returns:
            Updated context object
        """
        user_message_obj = {
            "role": "user",
            "msg": user_message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure user_chats is always a list
        if not hasattr(context, 'user_chats'):
            context.user_chats = []
        elif not isinstance(context.user_chats, list):
            logger.warning(f"user_chats was not a list, resetting. Type: {type(context.user_chats)}, content: {context.user_chats}")
            context.user_chats = []
        
        context.user_chats.append(user_message_obj)
        
        # Update timestamps
        if hasattr(context, 'last_updated'):
            context.last_updated = datetime.now().isoformat()
        
        logger.info(f"Conversation history updated for connection: {getattr(context, 'connection_id', 'unknown')}")
        logger.info(f"user_chats now has {len(context.user_chats)} messages")
        return context
    
    async def update_with_ai_response(self, ai_response: Dict[str, Any], context: Any, variable_config: Dict[str, Any] = None) -> Any:
        """
        Update context with AI response, extracting collected and missing variables.
        
        Args:
            ai_response: Validated AI response containing variables and metadata
            context: Current context object
            variable_config: Optional variable configuration (if not provided, skips variable extraction)
            
        Returns:
            Updated context object
        """
        try:
            # Extract response text more robustly
            res_text = None
            if 'ai_response' in ai_response and ai_response['ai_response']:
                res_text = ai_response['ai_response']
            else:
                # Fallback: use the entire response as string
                res_text = str(ai_response)
            
            # Add AI response to conversation history
            ai_message_obj = {
                "role": "assistant",
                "msg": res_text,  # Convert response to string for storage
                "timestamp": datetime.now().isoformat()
            }
            
            # Ensure user_chats is always a list
            if not hasattr(context, 'user_chats'):
                context.user_chats = []
            elif not isinstance(context.user_chats, list):
                logger.warning(f"user_chats was not a list in update_with_ai_response, resetting. Type: {type(context.user_chats)}, content: {context.user_chats}")
                context.user_chats = []
            
            context.user_chats.append(ai_message_obj)
            
            # Store entire AI response
            context.ai_response = ai_response
            
            # Extract intent if present
            if 'intent' in ai_response:
                context.current_intent = ai_response['intent']
                logger.info(f"Intent updated to: {ai_response['intent']}")
            
            # Extract collected variables from AI response if config is available
            collected_vars = {}
            missing_vars = []
            
            if variable_config and hasattr(context, 'current_intent') and context.current_intent != 'unknown':
                try:
                    from utils.context_utils import ContextUtils
                    
                    context_utils = ContextUtils(variable_config)
                    
                    # Get all variables for this intent
                    intent_variables = context_utils._get_variables_for_intent(context.current_intent)
                    
                    logger.info(f"Found {len(intent_variables)} variables for intent {context.current_intent}")
                    logger.info(f"Intent variables: {intent_variables}")
                    logger.info(f"AI response keys: {list(ai_response.keys())}")
                    
                    # Check which variables are present in AI response
                    for var_name, var_config in intent_variables.items():
                        logger.info(f"Checking variable: {var_name}")
                        if var_name in ai_response and ai_response[var_name] is not None:
                            # Variable is collected
                            collected_vars[var_name] = ai_response[var_name]
                            logger.info(f"Collected variable: {var_name} = {ai_response[var_name]}")
                        else:
                            # Variable is missing
                            missing_var_info = {
                                'name': var_name,
                                'description': var_config.get('description', ''),
                                'is_required': var_config.get('is_required', False),
                                'ai_must': var_config.get('forAI_intent_expectation_text', '')
                            }
                            missing_vars.append(missing_var_info)
                            logger.info(f"Missing variable: {var_name}")
                    
                    # Update context with collected and missing variables
                    context.collected_variables = collected_vars
                    context.missing_variables = missing_vars
                    
                    logger.info(f"Updated context with {len(collected_vars)} collected and {len(missing_vars)} missing variables")
                    logger.info(f"Final collected_variables: {context.collected_variables}")
                    logger.info(f"Final missing_variables: {context.missing_variables}")
                    
                except Exception as config_error:
                    logger.error(f"Failed to process variables for intent {context.current_intent}: {config_error}")
                    # Fallback: just store the AI response without variable extraction
                    context.collected_variables = {}
                    context.missing_variables = []
            else:
                # No config available or no intent, set empty variables
                context.collected_variables = {}
                context.missing_variables = []
                if not variable_config:
                    logger.info("No variable config provided, skipping variable extraction")
                elif not hasattr(context, 'current_intent') or context.current_intent == 'unknown':
                    logger.info("No current intent, skipping variable extraction")
            
            # Update timestamps
            if hasattr(context, 'last_updated'):
                context.last_updated = datetime.now().isoformat()
            
            logger.info(f"AI response processed for connection: {getattr(context, 'connection_id', 'unknown')}")
            logger.info(f"Conversation history now has {len(context.user_chats)} messages")
            return context
            
        except Exception as e:
            logger.error(f"Failed to update context with AI response: {e}")
            # Ensure context is still updated with basic info even if variable extraction fails
            if not hasattr(context, 'ai_response'):
                context.ai_response = ai_response
            if hasattr(context, 'last_updated'):
                context.last_updated = datetime.now().isoformat()
            return context
    
    def get_context_summary(self, context: Any) -> Dict[str, Any]:
        """Get a summary of the current context."""
        # If context has a to_dict method, use it
        if hasattr(context, 'to_dict') and callable(context.to_dict):
            summary = context.to_dict()
            # Add variable_status if the method exists
            if hasattr(self, 'get_variable_status'):
                summary['variable_status'] = self.get_variable_status(context)
            return summary
        
        # Fallback to manual attribute extraction
        summary = {
            "connection_id": getattr(context, 'connection_id', 'unknown'),
            "session_id": getattr(context, 'session_id', 'unknown'),
            "user_chats": getattr(context, 'user_chats', []),
            "collected_variables": getattr(context, 'collected_variables', {}),
            "missing_variables": getattr(context, 'missing_variables', []),
            "current_intent": getattr(context, 'current_intent', 'unknown'),
            "variable_status": self.get_variable_status(context) if hasattr(self, 'get_variable_status') else {}
        }
        
        return summary
    
    def reset_context(self, context: Any) -> Any:
        """Reset context to initial state."""
        # Clear conversation history
        if hasattr(context, 'user_chats'):
            context.user_chats = []
        
        # Clear AI response
        if hasattr(context, 'ai_response'):
            context.ai_response = {}
        
        # Reset variables
        if hasattr(context, 'collected_variables'):
            context.collected_variables = {}
        
        if hasattr(context, 'missing_variables'):
            context.missing_variables = []
        
        # Reset intent
        if hasattr(context, 'current_intent'):
            context.current_intent = 'unknown'
        
        # Update timestamp
        if hasattr(context, 'last_updated'):
            context.last_updated = datetime.now().isoformat()
        
        logger.info(f"Context reset for connection: {getattr(context, 'connection_id', 'unknown')}")
        return context
    
    def merge_context(self, target_context: Any, source_context: Any) -> Any:
        """Merge source context into target context."""
        # Merge conversation history
        if hasattr(source_context, 'user_chats') and hasattr(target_context, 'user_chats'):
            target_context.user_chats.extend(source_context.user_chats)
        
        # Merge variables (source takes precedence)
        if hasattr(source_context, 'collected_variables') and hasattr(target_context, 'collected_variables'):
            target_context.collected_variables.update(source_context.collected_variables)
        
        # Merge missing variables (source takes precedence)
        if hasattr(source_context, 'missing_variables') and hasattr(target_context, 'missing_variables'):
            # Remove duplicates based on variable name
            existing_names = {var.get('name', '') for var in target_context.missing_variables}
            for var in source_context.missing_variables:
                if var.get('name', '') not in existing_names:
                    target_context.missing_variables.append(var)
        
        # Update timestamp
        if hasattr(target_context, 'last_updated'):
            target_context.last_updated = datetime.now().isoformat()
        
        logger.info(f"Contexts merged for connection: {getattr(target_context, 'connection_id', 'unknown')}")
        return target_context
    
    def update_collected_variable(self, context: Any, var_name: str, value: Any) -> None:
        """
        Update a single collected variable and remove it from missing variables.
        
        Args:
            context: Context object to update
            var_name: Name of the variable
            value: Value of the variable
        """
        try:
            if not hasattr(context, 'collected_variables'):
                context.collected_variables = {}
            
            # Add to collected variables
            context.collected_variables[var_name] = value
            
            # Remove from missing variables
            if hasattr(context, 'missing_variables'):
                context.missing_variables = [
                    var for var in context.missing_variables 
                    if var.get('name') != var_name
                ]
            
            # Update timestamp
            if hasattr(context, 'last_updated'):
                context.last_updated = datetime.now().isoformat()
            
            logger.info(f"Updated collected variable: {var_name} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to update collected variable: {e}")
    
    def get_variable_status(self, context: Any) -> Dict[str, Any]:
        """
        Get current status of variables in context.
        
        Returns:
            Dictionary with collected and missing variable counts and details
        """
        try:
            collected_count = len(getattr(context, 'collected_variables', {}))
            missing_count = len(getattr(context, 'missing_variables', []))
            required_missing = len([
                var for var in getattr(context, 'missing_variables', [])
                if var.get('is_required', False)
            ])
            
            return {
                'collected_count': collected_count,
                'missing_count': missing_count,
                'required_missing_count': required_missing,
                'total_variables': collected_count + missing_count,
                'intent': getattr(context, 'current_intent', 'unknown'),
                'is_complete': required_missing == 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get variable status: {e}")
            return {
                'collected_count': 0,
                'missing_count': 0,
                'required_missing_count': 0,
                'total_variables': 0,
                'intent': 'unknown',
                'is_complete': False
            }
            
    def get_intent_variables(self, context: Any, variable_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get all variables for the current intent.
        
        Args:
            context: Context object
            variable_config: Variable configuration (if not provided, returns empty dict)
            
        Returns:
            Dictionary with intent variables information
        """
        try:
            if not variable_config or not hasattr(context, 'current_intent') or context.current_intent == 'unknown':
                return {}
            
            from utils.context_utils import ContextUtils
            context_utils = ContextUtils(variable_config)
            
            intent_variables = context_utils._get_variables_for_intent(context.current_intent)
            
            return {
                'intent': context.current_intent,
                'variables': intent_variables,
                'total_count': len(intent_variables),
                'required_count': len([v for v in intent_variables.values() if v.get('is_required', False)]),
                'optional_count': len([v for v in intent_variables.values() if not v.get('is_required', False)])
            }
            
        except Exception as e:
            logger.error(f"Failed to get intent variables: {e}")
            return {}
            