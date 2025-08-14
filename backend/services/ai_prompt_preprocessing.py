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
from utils.variable_utils import VariableUtils
from utils.data_fetch_utils import DataFetchUtils
from utils.static_content_utils import StaticContentUtils
from utils.intent_config_utils import IntentConfigUtils
from utils.context_utils import ContextUtils
from utils.conversation_utils import ConversationUtils

logger = logging.getLogger(__name__)

class AIPromptPreprocessing:
    """Service for collecting and compiling AI prompt data from multiple sources."""
    
    def __init__(self, db_session: AsyncSession, config_path: str = "ai_preprocessing_config.yaml", variable_config_path: str = "variable_config.yaml"):
        self.db_session = db_session
        self.ai_db_service = AIDatabaseService(db_session)
        self.config_path = config_path
        self.variable_config_path = variable_config_path
        self.variable_config = self._load_variable_config()
        
        # Initialize utility classes
        self.variable_utils = VariableUtils(self.variable_config)
        self.data_fetch_utils = DataFetchUtils(self.ai_db_service)
        self.static_content_utils = StaticContentUtils(config_path)
        self.intent_config_utils = IntentConfigUtils(self.variable_config)
        self.context_utils = ContextUtils(self.variable_config)
        self.conversation_utils = ConversationUtils()
    
    def _load_variable_config(self) -> Dict[str, Any]:
        """Load variable configuration from YAML file."""
        try:
            config_file = Path(__file__).parent.parent / self.variable_config_path
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load variable config: {e}")
            return {}
    
    def get_context_expectations(self, context: Any) -> str:
        """Get context expectations based on intent and variables."""
        return self.context_utils.get_context_expectations(context)
    
    def get_intent_configuration(self) -> Dict[str, Any]:
        """Get intent configuration with required and optional fields."""
        return self.intent_config_utils.get_intent_configuration()
    
    def get_collected_variables(self, context: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get collected variables organized by required and optional fields."""
        return self.variable_utils.get_collected_variables(context)
    
    def get_missing_variables(self, context: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get missing variables organized by required and optional fields with intent expectations."""
        return self.variable_utils.get_missing_variables(context)
    
    async def get_reference_data(self, context: Any) -> Dict[str, Any]:
        """Get general reference data from database and static config."""
        return await self.static_content_utils.get_reference_data(self.ai_db_service, context)
    
    def get_conversation_history(self, context: Any) -> List[Dict[str, str]]:
        """Get conversation history from context."""
        return self.conversation_utils.get_conversation_history(context)
    
    def get_system_prompt(self) -> str:
        """Get system prompt content."""
        return self.static_content_utils.get_system_prompt()
    
    def get_examples_prompt(self) -> str:
        """Get examples prompt content."""
        return self.static_content_utils.get_examples_prompt()
    
    async def get_intent_specific_data(self, context: Any) -> Dict[str, Any]:
        """Get intent-specific data from database based on missing variables."""
        return await self.data_fetch_utils.get_intent_specific_data(context, self.variable_config)
    
    async def get_variable_specific_data(self, context: Any) -> Dict[str, Any]:
        """Get variable-specific data from database based on present variables."""
        return await self.data_fetch_utils.get_variable_specific_data(context, self.variable_config)
    
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
                prompt_parts.append(f"All Intent specific fields are as follows: {self.intent_config_utils.format_intent_config(intent_config)}")
            
            # Reference data
            reference_data = prompt_data.get('reference_data', {})
            if reference_data:
                print(f"DDDDDD DEBUG: Adding reference data")
                prompt_parts.append(f"{self.static_content_utils.format_reference_data(reference_data)}")
            
            # System prompt is always included
            if prompt_data.get('examples_prompt'):
                prompt_parts.append(prompt_data.get('examples_prompt'))
            
            # Collected variables
            collected_vars = prompt_data.get('collected_variables', {})
            if collected_vars:
                print(f"DDDDDD DEBUG: Adding collected variables")
                prompt_parts.append(f"************ We have already collected the variables {self.variable_utils.format_collected_variables(collected_vars)}")
                print(f"🟢🟢🟢🟢 DEBUG: collected_vars: {pprint.pformat(collected_vars)}")
            
            # Missing variables
            missing_vars = prompt_data.get('missing_variables', {})
            if missing_vars:
                print(f"DDDDDD DEBUG: Adding missing variables")
                prompt_parts.append(f"************ But these variables are missing: {self.variable_utils.format_missing_variables(missing_vars)}")
            
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
                    data_parts.append(self.data_fetch_utils.format_intent_specific_data(intent_specific))
                if variable_specific:
                    data_parts.append(self.data_fetch_utils.format_variable_specific_data(variable_specific))
                if data_parts:
                    prompt_parts.append(f"Based on our chat, this data might help you in forming a reply, or filling in more fields: {' + '.join(data_parts)}")
            
            # Conversation history - always included since user_chats will never be empty
            conversation_history = prompt_data.get('conversation_history', [])
            prompt_parts.append(f"Finally, this is our current conversation that you must continue: {self.conversation_utils.format_conversation_history(conversation_history)}")
            print(f"DDDDDD DEBUG: Adding conversation history")

            # print(f"🟢🟢🟢🟢 FINAL INPUT: {pprint.pformat(prompt_parts)}")

            return "\n\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Failed to compile prompt string: {e}")
            return prompt_data.get('system_prompt', 'Error compiling prompt')
    
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