"""
AI Prompt Preprocessing Service
Collects data from multiple sources and compiles it into comprehensive AI prompts.
"""

import logging
import pprint
import yaml
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_db_service import AIDatabaseService

logger = logging.getLogger(__name__)

class AIPromptPreprocessing:
    """Service for collecting and compiling AI prompt data from multiple sources."""
    
    def __init__(self, db_session: AsyncSession, config_path: str = "ai_preprocessing_config.yaml", variable_config_path: str = "variable_config.yaml"):
        self.db_session = db_session
        self.ai_db_service = AIDatabaseService(db_session)
        self.config_path = config_path
        self.variable_config_path = variable_config_path
        self.config = self._load_config()
        self.variable_config = self._load_variable_config()
        self.system_prompt = self._load_system_prompt()
        self.examples_prompt = self._load_examples_prompt()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(__file__).parent.parent / self.config_path
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    def _load_variable_config(self) -> Dict[str, Any]:
        """Load variable configuration from YAML file."""
        try:
            config_file = Path(__file__).parent.parent / self.variable_config_path
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load variable config: {e}")
            return {}
    def _load_examples_prompt(self) -> str:
        """Load examples prompt from file."""
        try:
            prompt_file = Path(__file__).parent.parent / "example_prompt.txt"
            with open(prompt_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load example prompt: {e}")
            return "You are an AI assistant that helps with task management and productivity."
    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        try:
            prompt_file = Path(__file__).parent.parent / "system_prompt.txt"
            with open(prompt_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return "You are an AI assistant that helps with task management and productivity."
    
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
    
    def get_collected_variables(self, context: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get collected variables organized by required and optional fields."""
        try:
            collected = getattr(context, 'collected_variables', [])
            missing = getattr(context, 'missing_variables', [])
            
            # Organize collected variables by required/optional
            required_fields = []
            optional_fields = []
            
            for var in collected:
                var_name = var.get('name')
                if var_name:
                    var_config = self._find_variable_config(var_name)
                    if var_config:
                        field_info = {
                            'name': var_name,
                            'value': var.get('value', ''),
                            'is_required': var_config.get('is_required', False)
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
    
    async def get_reference_data(self, context: Any) -> Dict[str, Any]:
        """Get general reference data from database and static config."""
        try:
            user_id = getattr(context, 'user_id', None)
            if not user_id:
                return {}
            
            # Get static categories and formats from config
            static_data = {
                "categories": self.config.get('validation_rules', {}).get('valid_category', {}).get('values', []),
                "date_format": self.config.get('global', {}).get('date_format_in', 'DD-MM-YYYY'),
                "time_format": self.config.get('global', {}).get('time_format_in', 'HH:MM')
            }
            
            # Get user-specific data from database
            db_data = await self.ai_db_service.fetch_user_reference_data(user_id)
            
            # Add today's date
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            static_data['today_date'] = today
            
            # Add task list if available
            if 'task_list' in db_data:
                static_data['task_list'] = db_data['task_list']
            
            return {**static_data, **db_data}
            
        except Exception as e:
            logger.error(f"Failed to get reference data: {e}")
            return {}
    
    def get_conversation_history(self, context: Any) -> List[Dict[str, str]]:
        """Get conversation history from context."""
        try:
            if hasattr(context, 'user_chats') and context.user_chats:
                # Ensure proper format with 'role' and 'msg' keys
                formatted_history = []
                for chat in context.user_chats:
                    if isinstance(chat, dict):
                        formatted_history.append({
                            'role': chat.get('role', 'unknown'),
                            'msg': chat.get('text', chat.get('msg', ''))
                        })
                print(f"🔍 Extracted {len(formatted_history)} messages from conversation history")
                return formatted_history
            print(f"🔍 No user_chats found in context")
            return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def compile_prompt_string(self, prompt_data: Dict[str, Any]) -> str:
        """
        Compile the collected data into a single input prompt string.
        
        Args:
            prompt_data: Dictionary containing all prompt data blocks
            
        Returns:
            Formatted prompt string ready for AI
        """
        try:
            # New prompt structure as requested - only include sections with data
            prompt_parts = []
            
            # System prompt is always included
            if prompt_data.get('system_prompt'):
                prompt_parts.append(prompt_data.get('system_prompt'))
            
            # Intent configuration
            intent_config = prompt_data.get('intent_config', {})
            if intent_config:
                print(f"DDDDDD DEBUG: Adding intent config")
                prompt_parts.append(f"All Intent specific fields are as follows: {self._format_intent_config(intent_config)}")
            
            # Reference data
            reference_data = prompt_data.get('reference_data', {})
            if reference_data:
                print(f"DDDDDD DEBUG: Adding reference data")
                prompt_parts.append(f"{self._format_reference_data(reference_data)}")
            
            # System prompt is always included
            if prompt_data.get('examples_prompt'):
                prompt_parts.append(prompt_data.get('examples_prompt'))
            
            # Collected variables
            collected_vars = prompt_data.get('collected_variables', {})
            if collected_vars:
                print(f"DDDDDD DEBUG: Adding collected variables")
                prompt_parts.append(f"************ We have already collected the variables {self._format_collected_variables(collected_vars)}")
                print(f"🟢🟢🟢🟢 DEBUG: collected_vars: {pprint.pformat(collected_vars)}")
            
            # Missing variables
            missing_vars = prompt_data.get('missing_variables', {})
            if missing_vars:
                print(f"DDDDDD DEBUG: Adding missing variables")
                prompt_parts.append(f"************ But these variables are missing: {self._format_missing_variables(missing_vars)}")
            
            # Context expectations
            context_expectations = prompt_data.get('context_expectations', '')
            if context_expectations:
                print(f"DDDDDD DEBUG: Adding context expectations")
                prompt_parts.append(f"You must try to find out more information based on the conversation with the user with the following things in mind. Ask user questions to accomplish: {context_expectations}")
            
            # Intent and variable specific data
            intent_specific = prompt_data.get('intent_specific_data', {})
            variable_specific = prompt_data.get('variable_specific_data', {})
            if intent_specific or variable_specific:
                data_parts = []
                if intent_specific:
                    data_parts.append(self._format_intent_specific_data(intent_specific))
                if variable_specific:
                    data_parts.append(self._format_variable_specific_data(variable_specific))
                if data_parts:
                    prompt_parts.append(f"Based on our chat, this data might help you in forming a reply, or filling in more fields: {' + '.join(data_parts)}")
            
            # Conversation history - always included since user_chats will never be empty
            conversation_history = prompt_data.get('conversation_history', [])
            prompt_parts.append(f"Finally, this is our current conversation that you must continue: {self._format_conversation_history(conversation_history)}")
            print(f"DDDDDD DEBUG: Adding conversation history")

            # print(f"🟢🟢🟢🟢 FINAL INPUT: {pprint.pformat(prompt_parts)}")

            return "\n\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Failed to compile prompt string: {e}")
            return prompt_data.get('system_prompt', 'Error compiling prompt')
    
    def get_system_prompt(self) -> str:
        """Get system prompt content."""
        return self.system_prompt
    
    def get_examples_prompt(self) -> str:
        """Get examples prompt content."""
        return self.examples_prompt
    
    async def compile_ai_prompt(self, context: Any) -> Dict[str, Any]:
        """
        Main function to compile AI prompt from multiple data sources.
        
        Args:
            user_message: The user's input message
            socket_session: WebSocket session object
            db_session: Database session object
            context: Context object containing session data
            
        Returns:
            Dictionary with all prompt data blocks
        """
        try:
            # Set current user ID for database operations
            user_id = getattr(context, 'user_id', None)
            if user_id:
                self.ai_db_service.set_user_id(user_id)
            
            # Collect all data blocks
            prompt_data = {
                "system_prompt": self.get_system_prompt(),
                "intent_config": self.get_intent_configuration(),
                "examples_prompt": self.get_examples_prompt(),
                "conversation_history": self.get_conversation_history(context),
                "reference_data": await self.get_reference_data(context),
                "collected_variables": self.get_collected_variables(context),
                "missing_variables": self.get_missing_variables(context),
                "intent_specific_data": await self.get_intent_specific_data(context),
                "variable_specific_data": await self.get_variable_specific_data(context),
                "context_expectations": self.get_context_expectations(context)
            }
            
            logger.info("Successfully compiled AI prompt data")
            return prompt_data
            
        except Exception as e:
            logger.error(f"Failed to compile AI prompt: {e}")
            return {
                "error": f"Failed to compile prompt: {str(e)}",
                "system_prompt": self.get_system_prompt()
            }
        
    def _find_variable_config(self, var_name: str) -> Optional[Dict[str, Any]]:
        """Find variable configuration in variable config file."""
        variables = self.variable_config.get('variables', {})
        return variables.get(var_name)
    
    async def get_intent_specific_data(self, context: Any) -> Dict[str, Any]:
        """Get intent-specific data from database based on missing variables."""
        try:
            missing_vars = getattr(context, 'missing_variables', [])
            intent_type = getattr(context, 'current_intent', 'unknown')
            
            data = {}
            for var_name in missing_vars:
                var_config = self._find_variable_config(var_name)
                if var_config and var_config.get('forDB_fetch_data_key'):
                    db_data = await self._fetch_intent_specific_data(intent_type, var_name, var_config)
                    if db_data:
                        data[var_name] = db_data
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get intent-specific data: {e}")
            return {}
    
    async def _fetch_intent_specific_data(self, intent_type: str, var_name: str, var_config: Dict[str, Any]) -> Optional[Any]:
        """Fetch intent-specific data from database based on variable config."""
        try:
            fetch_key = var_config.get('forDB_fetch_data_key')
            fetch_payload = var_config.get('forDB_fetch_data_payload', {})
            
            # Fetch data based on the specified key and payload
            db_data = await self.ai_db_service.fetch_data_by_key(fetch_key, fetch_payload)
            
            return {
                "intent_type": intent_type,
                "variable": var_name,
                "fetch_key": fetch_key,
                "fetch_payload": fetch_payload,
                "data": db_data
            }
        except Exception as e:
            logger.error(f"Failed to fetch intent-specific data: {e}")
            return None
    
    async def get_variable_specific_data(self, context: Any) -> Dict[str, Any]:
        """Get variable-specific data from database based on present variables."""
        try:
            collected_vars = getattr(context, 'collected_variables', [])
            intent_type = getattr(context, 'current_intent', 'unknown')
            
            data = {}
            for var in collected_vars:
                var_name = var.get('name')
                if var_name:
                    var_config = self._find_variable_config(var_name)
                    if var_config:
                        db_data = await self._fetch_variable_specific_data(intent_type, var_name, var_config)
                        if db_data:
                            data[var_name] = db_data
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get variable-specific data: {e}")
            return {}
    
    async def _fetch_variable_specific_data(self, intent_type: str, var_name: str, var_config: Dict[str, Any]) -> Optional[Any]:
        """Fetch variable-specific data from database based on variable config."""
        try:
            fetch_key = var_config.get('forDB_fetch_data_key')
            fetch_payload = var_config.get('forDB_fetch_data_payload', {})
            
            # Fetch data based on the specified key and payload
            db_data = await self.ai_db_service.fetch_data_by_key(fetch_key, fetch_payload)
            
            return {
                "intent_type": intent_type,
                "variable": var_name,
                "fetch_key": fetch_key,
                "fetch_payload": fetch_payload,
                "data": db_data
            }
        except Exception as e:
            logger.error(f"Failed to fetch variable-specific data: {e}")
            return None
    
    # Helper methods for formatting
    def _format_intent_config(self, config: Dict[str, Any]) -> Optional[str]:
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
    
    def _format_conversation_history(self, history: List[Dict[str, str]]) -> Optional[str]:
        """Format conversation history for prompt."""
        if not history:
            return None
        
        formatted = ["=== Conversation History ==="]
        formatted.append(f"--------------------------------")
        for i, entry in enumerate(history):
            if isinstance(entry, dict):
                role = entry.get('role', 'unknown')
                msg = entry.get('msg', entry.get('text', ''))
                if msg:
                    formatted.append(f"{role.capitalize()}: \"{msg}\"")
        
        if len(formatted) == 1:  # Only header
            formatted.append("No messages in conversation history")
        formatted.append(f"--------------------------------")
        
        return "\n".join(formatted)
    
    def _format_reference_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Format reference data for prompt."""
        if not data:
            return None
        
        formatted = ["=== Reference Data ==="]
        for key, value in data.items():
            if isinstance(value, list):
                if value:
                    formatted.append(f"{key}: {', '.join(map(str, value))}")
                else:
                    formatted.append(f"{key}: (empty list)")
            elif value is not None and value != "":
                formatted.append(f"{key}: {value}")
            else:
                formatted.append(f"{key}: (not set)")
        
        return "\n".join(formatted)
    
    def _format_collected_variables(self, data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
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
    
    def _format_missing_variables(self, data: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
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
    
    def _format_intent_specific_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Format intent-specific data for prompt."""
        if not data:
            return None
        
        formatted = ["=== Intent-Specific Data ==="]
        for key, value in data.items():
            if isinstance(value, dict):
                formatted.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    if sub_key == 'data' and isinstance(sub_value, (list, dict)):
                        formatted.append(f"  {sub_key}: {type(sub_value).__name__} with {len(sub_value) if isinstance(sub_value, list) else len(sub_value.keys())} items")
                    else:
                        formatted.append(f"  {sub_key}: {sub_value}")
            else:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)
    
    def _format_variable_specific_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Format variable-specific data for prompt."""
        if not data:
            return None
        
        formatted = ["=== Variable-Specific Data ==="]
        for key, value in data.items():
            if isinstance(value, dict):
                formatted.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    if sub_key == 'data' and isinstance(sub_value, (list, dict)):
                        formatted.append(f"  {sub_key}: {type(sub_value).__name__} with {len(sub_value) if isinstance(sub_value, list) else len(sub_value.keys())} items")
                    else:
                        formatted.append(f"  {sub_key}: {sub_value}")
            else:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted) 