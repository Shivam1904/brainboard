"""
AI Prompt Preprocessing Service
Collects data from multiple sources and compiles it into comprehensive AI prompts.
"""

import logging
import pprint
import yaml
from typing import Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from utils.variable_utils import VariableUtils
from utils.data_fetch_utils import DataFetchUtils
from utils.static_content_utils import StaticContentUtils
from utils.intent_config_utils import IntentConfigUtils
from utils.context_utils import ContextUtils
from utils.conversation_utils import ConversationUtils

logger = logging.getLogger(__name__)

class AIPromptPreprocessing:
    """Service for collecting and compiling AI prompt data from multiple sources."""
    
    def __init__(self):
        self.variable_config_path = "variable_config.yaml"
        self.variable_config = self._load_variable_config()
        
        # Initialize utility classes with defensive programming
        try:
            self.variable_utils = VariableUtils(self.variable_config)
            self.data_fetch_utils = DataFetchUtils()
            self.static_content_utils = StaticContentUtils(self.variable_config_path)
            self.intent_config_utils = IntentConfigUtils(self.variable_config)
            self.context_utils = ContextUtils(self.variable_config)
            self.conversation_utils = ConversationUtils()
        except Exception as e:
            logger.error(f"Failed to initialize utility classes: {e}")
            # Create fallback instances with empty configs
            self.variable_utils = VariableUtils({})
            self.data_fetch_utils = DataFetchUtils()
            self.static_content_utils = StaticContentUtils("variable_config.yaml")
            self.intent_config_utils = IntentConfigUtils({})
            self.context_utils = ContextUtils({})
            self.conversation_utils = ConversationUtils()
    
    def _load_variable_config(self) -> Dict[str, Any]:
        """Load variable configuration from YAML file."""
        try:
            # Ensure variable_config_path is a string
            if not isinstance(self.variable_config_path, str):
                logger.error(f"Invalid variable_config_path type: {type(self.variable_config_path)}, expected string")
                return {}
            
            # Construct path more robustly
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent
            config_file = backend_dir / self.variable_config_path
            
            logger.info(f"Loading config from: {config_file}")
            
            if not config_file.exists():
                logger.error(f"Config file not found: {config_file}")
                return {}
                
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Successfully loaded config with {len(config) if config else 0} top-level keys")
                return config or {}
        except Exception as e:
            logger.error(f"Failed to load variable config: {e}")
            logger.error(f"variable_config_path: {self.variable_config_path}, type: {type(self.variable_config_path)}")
            return {}
    
    async def compile_prompt_string(self, context: Any, db_session: AsyncSession) -> str:
        """
        Compile the collected data into a single input prompt string.
        
        Args:
            context: Context object containing session data
            db_session: Database session object
            
        Returns:
            Formatted prompt string ready for AI
        """
        try:
            # Debug: Check context state
            logger.info(f"Compiling prompt string for context: {getattr(context, 'connection_id', 'unknown')}")
            logger.info(f"Context has user_chats: {hasattr(context, 'user_chats')}")
            if hasattr(context, 'user_chats'):
                logger.info(f"user_chats type: {type(context.user_chats)}")
                logger.info(f"user_chats length: {len(context.user_chats) if context.user_chats else 0}")
                logger.info(f"user_chats content: {context.user_chats}")
            
            prompt_data = await self.compile_ai_prompt(context=context, db_session=db_session)

            # New prompt structure as requested - only include sections with data
            prompt_parts = []
            
            # System prompt is always included
            if prompt_data.get('system_prompt'):
                prompt_parts.append(prompt_data.get('system_prompt'))
            
            # Intent configuration - only add if no intent is detected in context
            intent_config = prompt_data.get('intent_config', {})
            current_intent = getattr(context, 'current_intent', 'unknown')
            # if intent_config and (not current_intent or current_intent == 'unknown'):
            prompt_parts.append(f"{self.intent_config_utils.format_intent_config(intent_config)}")
            
            # System prompt is always included
            if prompt_data.get('examples_prompt'):
                prompt_parts.append(prompt_data.get('examples_prompt'))
            
            # Reference data
            reference_data = prompt_data.get('reference_data', {})
            if reference_data:
                prompt_parts.append(f"{self.static_content_utils.format_reference_data(reference_data)}")
            
            # Collected variables
            collected_vars = prompt_data.get('collected_variables', {})
            if collected_vars:
                formatted_collected = self.variable_utils.format_collected_variables(collected_vars)
                if formatted_collected:
                    prompt_parts.append(f"{formatted_collected}")
                    
            # Missing variables
            missing_vars = prompt_data.get('missing_variables', {})
            if missing_vars:
                prompt_parts.append(f"{self.variable_utils.format_missing_variables(missing_vars)}")
            
            # Intent text
            intent_text = current_intent if current_intent and current_intent != 'unknown' else None
            if intent_text:
                prompt_parts.append(f"INTENT HAS BEEN DETECTED: \'{intent_text}\'")
                if(intent_text == 'adding'):
                    prompt_parts.append(f"Do not change until next intent is found.")
                elif(intent_text == 'editing_config'):
                    prompt_parts.append(f"")
                elif(intent_text == 'editing_day_activity'):
                    prompt_parts.append(f"")
                elif(intent_text == 'analyzing'):
                    prompt_parts.append(f"Do not change until user diverts from topic of analyzing.")
                elif(intent_text == 'discussing'):
                    prompt_parts.append(f"Change to 'adding' only when user confirms creating the task.")
                else:
                    prompt_parts.append(f"Intent has not been detected yet. Try to infer from conversation.")
            else:
                prompt_parts.append(f"Intent has not been detected yet. Try to infer from conversation.")
            
            # Conversation history - always included since user_chats will never be empty
            conversation_history = prompt_data.get('conversation_history', [])
            if conversation_history:
                formatted_history = self.conversation_utils.format_conversation_history(conversation_history)
                prompt_parts.append(f"{formatted_history}")
                
                # Add instruction to check conversation history for repetitive responses
                # prompt_parts.append("Make sure to never repeat in ai_response what the ai has already said.")

            res = "\n\n".join(prompt_parts)

            logger.debug(f"🟢🟢🟢🟢 FINAL INPUT: {res}")

            return res
            
        except Exception as e:
            logger.error(f"Failed to compile prompt string: {e}")
            logger.error(f"Context state: {getattr(context, 'connection_id', 'unknown')}")
            logger.error(f"Context has user_chats: {hasattr(context, 'user_chats')}")
            if hasattr(context, 'user_chats'):
                logger.error(f"user_chats type: {type(context.user_chats)}")
                logger.error(f"user_chats content: {context.user_chats}")
            return prompt_data.get('system_prompt', 'Error compiling prompt')
    
    async def compile_ai_prompt(self, context: Any, db_session: AsyncSession) -> Dict[str, Any]:
        """
        Main function to compile AI prompt from multiple data sources.
        
        Args:
            context: Context object containing session data
            db_session: Database session object
            
        Returns:
            Dictionary with all prompt data blocks
        """
        try:
            # Debug: Check conversation history extraction
            conversation_history = self.conversation_utils.get_conversation_history(context)
            logger.info(f"Extracted conversation history: {len(conversation_history) if conversation_history else 0} messages")
            logger.info(f"Conversation history type: {type(conversation_history)}")
            if conversation_history:
                logger.info(f"First message: {conversation_history[0] if len(conversation_history) > 0 else 'None'}")
            
            prompt_data = {
                "system_prompt": self.static_content_utils.get_system_prompt(),
                "intent_config": self.intent_config_utils.get_intent_configuration(),
                "examples_prompt": self.static_content_utils.get_examples_prompt(),
                "conversation_history": conversation_history,
                "reference_data": await self.static_content_utils.get_reference_data(context),
                "collected_variables": self.variable_utils.get_collected_variables(context),
                "missing_variables": self.variable_utils.get_missing_variables(context),
                "intent_specific_data": await self.data_fetch_utils.get_intent_specific_data(context, self.variable_config),
                "variable_specific_data": await self.data_fetch_utils.get_variable_specific_data(context, self.variable_config)
            }
            logger.info("Successfully compiled AI prompt data")
            return prompt_data
            
        except Exception as e:
            logger.error(f"Failed to compile AI prompt: {e}")
            logger.error(f"Context state: {getattr(context, 'connection_id', 'unknown')}")
            logger.error(f"Context has user_chats: {hasattr(context, 'user_chats')}")
            if hasattr(context, 'user_chats'):
                logger.error(f"user_chats type: {type(context.user_chats)}")
                logger.error(f"user_chats content: {context.user_chats}")
            return {
                "error": f"Failed to compile prompt: {str(e)}",
                "system_prompt": self.static_content_utils.get_system_prompt()
            } 