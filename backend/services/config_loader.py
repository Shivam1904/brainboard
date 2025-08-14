"""
Configuration Loader for AI Preprocessing Configuration
"""

import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class AIConfigLoader:
    """Loads and manages AI preprocessing configuration from YAML file."""
    
    def __init__(self, config_path: str = None):
        """Initialize the configuration loader."""
        if config_path is None:
            # Default to the config file in the backend directory
            config_path = Path(__file__).parent.parent / "ai_preprocessing_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = None
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Validate configuration structure
            self._validate_config()
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
            return False
    
    def _validate_config(self):
        """Validate that the configuration has required sections."""
        required_sections = [
            'global', 'strategies', 'adding', 'editing', 'analysing',
            'validation_rules', 'preprocessing_context'
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return a minimal default configuration if loading fails."""
        return {
            'global': {
                'default_user_id': 'user_001',
                'fallback_strategies': ['try_harder', 'ask_user', 'ignore_argument']
            },
            'strategies': {
                'try_harder': {'description': 'Fetch additional context and retry'},
                'ask_user': {'description': 'Ask user for missing information'},
                'ignore_argument': {'description': 'Skip optional missing arguments'}
            },
            'adding': {'description': 'Create new widgets and tasks'},
            'editing': {'description': 'Update existing widgets'},
            'analysing': {'description': 'Analyze user data'},
            'validation_rules': {},
            'preprocessing_context': []
        }
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration settings."""
        return self.config.get('global', {})
    
    def get_strategies(self) -> Dict[str, Any]:
        """Get strategy definitions."""
        return self.config.get('strategies', {})
    
    def get_intent_config(self, intent: str) -> Dict[str, Any]:
        """Get configuration for a specific intent."""
        return self.config.get(intent, {})
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""
        return self.config.get('validation_rules', {})
    
    def get_preprocessing_context(self) -> List[Dict[str, Any]]:
        """Get preprocessing context requirements."""
        return self.config.get('preprocessing_context', [])
    
    def get_required_fields(self, intent: str) -> List[str]:
        """Get required fields for an intent."""
        intent_config = self.get_intent_config(intent)
        ai_response_args = intent_config.get('ai_response_arguments', {})
        required = ai_response_args.get('required', [])
        return [field['name'] for field in required]
    
    def get_optional_fields(self, intent: str) -> List[str]:
        """Get optional fields for an intent."""
        intent_config = self.get_intent_config(intent)
        ai_response_args = intent_config.get('ai_response_arguments', {})
        optional = ai_response_args.get('optional', [])
        return [field['name'] for field in optional]
    
    def get_missing_field_strategy(self, intent: str, field: str) -> Optional[Dict[str, Any]]:
        """Get the strategy for handling a missing field."""
        intent_config = self.get_intent_config(intent)
        missing_strategies = intent_config.get('missing_argument_strategies', {})
        return missing_strategies.get(field)
    
    def get_validation_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific validation rule."""
        validation_rules = self.get_validation_rules()
        return validation_rules.get(rule_name)
    
    def get_tool_arguments(self, intent: str) -> Dict[str, Any]:
        """Get tool arguments configuration for an intent."""
        intent_config = self.get_intent_config(intent)
        return intent_config.get('tool_arguments', {})
    
    def get_fallback_strategies(self) -> List[str]:
        """Get global fallback strategies."""
        global_config = self.get_global_config()
        return global_config.get('fallback_strategies', [])
    
    def get_try_harder_flow(self) -> Dict[str, Any]:
        """Get try harder flow definition."""
        return self.config.get('try_harder_flow', {})
    
    def reload_config(self) -> bool:
        """Reload configuration from file."""
        return self.load_config()
    
    def is_config_loaded(self) -> bool:
        """Check if configuration is loaded."""
        return self.config is not None
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded configuration."""
        if not self.config:
            return {"error": "No configuration loaded"}
        
        return {
            "config_path": str(self.config_path),
            "intents": list(self.config.keys()),
            "strategies": list(self.get_strategies().keys()),
            "validation_rules": list(self.get_validation_rules().keys()),
            "preprocessing_context": len(self.get_preprocessing_context())
        } 