"""
Static Content Utilities
Handles static content like system_prompt, examples_prompt, and reference_data.
"""

import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from services.ai_db_service import AIDatabaseService

logger = logging.getLogger(__name__)

class StaticContentUtils:
    """Utility class for handling static content."""
    
    def __init__(self, config_path: str = "variable_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.system_prompt = self._load_system_prompt()
        self.examples_prompt = self._load_examples_prompt()
        self.ai_db_service = AIDatabaseService()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(__file__).parent.parent / self.config_path
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _load_examples_prompt(self) -> str:
        """Load examples prompt from file."""
        try:
            prompt_file = Path(__file__).parent.parent / "examples_prompt.txt"
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
    
    def get_system_prompt(self) -> str:
        """Get system prompt content."""
        return self.system_prompt
    
    def get_examples_prompt(self) -> str:
        """Get examples prompt content."""
        return self.examples_prompt
    
    async def get_reference_data(self, context: Any) -> Dict[str, Any]:
        """Get general reference data from database and static config."""
        try:
            # Get static categories and formats from config
            static_data = {
                "categories": ['health', 'productivity', 'job', 'information', 'entertainment', 'utilities'],
                "date_format": 'DD-MM-YYYY',
                "time_format": 'HH:MM'
            }
            
            # Get user-specific data from database
            db_data = await self.ai_db_service.fetch_user_reference_data('user_001')
            
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
    
    def format_reference_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Format reference data for prompt."""
        if not data:
            return None
        
        formatted = ["CTX:"]
        for key, value in data.items():
            if isinstance(value, list):
                x = map(lambda item: "\"" + item + "\"", value)
                ss = ', '.join(x)
                if value:
                    formatted.append(f"{key}: [{ss}]")
            elif value is not None and value != "":
                formatted.append(f"{key}: \"{value}\"")
        
        return "\n".join(formatted) 