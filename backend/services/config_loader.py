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
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
            return False
    
    def is_config_loaded(self) -> bool:
        """Check if configuration is loaded."""
        return self.config is not None
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded configuration."""
        if not self.config:
            return {"error": "No configuration loaded"}
        
        return {
            "config_path": str(self.config_path)
        } 