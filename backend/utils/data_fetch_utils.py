"""
Data Fetch Utilities
Handles intent and variable specific data fetching functionality.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataFetchUtils:
    """Utility class for handling intent and variable specific data fetching."""
    
    def __init__(self, ai_db_service):
        self.ai_db_service = ai_db_service
    
    async def get_intent_specific_data(self, context: Any, variable_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get intent-specific data from database based on missing variables."""
        try:
            missing_vars = getattr(context, 'missing_variables', [])
            intent_type = getattr(context, 'current_intent', 'unknown')
            
            data = {}
            for var_name in missing_vars:
                var_config = self._find_variable_config(var_name, variable_config)
                if var_config and var_config.get('forDB_fetch_data_key'):
                    db_data = await self._fetch_intent_specific_data(intent_type, var_name, var_config)
                    if db_data:
                        data[var_name] = db_data
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get intent-specific data: {e}")
            return {}
    
    async def get_variable_specific_data(self, context: Any, variable_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get variable-specific data from database based on present variables."""
        try:
            collected_vars = getattr(context, 'collected_variables', [])
            intent_type = getattr(context, 'current_intent', 'unknown')
            
            data = {}
            for var in collected_vars:
                var_name = var.get('name')
                if var_name:
                    var_config = self._find_variable_config(var_name, variable_config)
                    if var_config:
                        db_data = await self._fetch_variable_specific_data(intent_type, var_name, var_config)
                        if db_data:
                            data[var_name] = db_data
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get variable-specific data: {e}")
            return {}
    
    def _find_variable_config(self, var_name: str, variable_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find variable configuration in variable config file."""
        variables = variable_config.get('variables', {})
        return variables.get(var_name)
    
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
    
    def format_intent_specific_data(self, data: Dict[str, Any]) -> Optional[str]:
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
    
    def format_variable_specific_data(self, data: Dict[str, Any]) -> Optional[str]:
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