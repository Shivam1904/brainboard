"""
Validation Engine for AI Service
Applies validation rules from the configuration file
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .config_loader import AIConfigLoader

class ValidationEngine:
    """Validates data according to configuration rules."""
    
    def __init__(self):
        """Initialize validation engine with configuration."""
        self.config = AIConfigLoader("variable_config.yaml")
    
    def _validate_string(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate string values."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        min_length = rule.get('min_length', 0)
        max_length = rule.get('max_length', float('inf'))
        
        if len(value) < min_length:
            return False, f"String too short (min: {min_length})"
        
        if len(value) > max_length:
            return False, f"String too long (max: {max_length})"
        
        return True, None
    
    def _validate_enum(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate enum values."""
        allowed_values = rule.get('values', [])
        
        if value not in allowed_values:
            return False, f"Value '{value}' not in allowed values: {allowed_values}"
        
        return True, None
    
    def _validate_integer(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate integer values."""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"Expected integer, got {type(value).__name__}"
        
        min_val = rule.get('min')
        max_val = rule.get('max')
        
        if min_val is not None and int_value < min_val:
            return False, f"Value too small (min: {min_val})"
        
        if max_val is not None and int_value > max_val:
            return False, f"Value too large (max: {max_val})"
        
        return True, None
    
    def _validate_float(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate float values."""
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, f"Expected float, got {type(value).__name__}"
        
        min_val = rule.get('min')
        max_val = rule.get('max')
        
        if min_val is not None and float_value < min_val:
            return False, f"Value too small (min: {min_val})"
        
        if max_val is not None and float_value > max_val:
            return False, f"Value too large (max: {max_val})"
        
        return True, None
    
    def _validate_boolean(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate boolean values."""
        if isinstance(value, bool):
            return True, None
        
        # Allow string representations
        if isinstance(value, str):
            if value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
                return True, None
        
        return False, f"Expected boolean, got {type(value).__name__}"
    
    def _validate_array(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate array values."""
        if not isinstance(value, list):
            return False, f"Expected array, got {type(value).__name__}"
        
        items_rule = rule.get('items')
        if items_rule:
            for i, item in enumerate(value):
                if items_rule.get('type') == 'string':
                    if not isinstance(item, str):
                        return False, f"Array item {i} should be string, got {type(item).__name__}"
                
                # Check enum constraints for array items
                if 'enum' in items_rule:
                    if item not in items_rule['enum']:
                        return False, f"Array item {i} '{item}' not in allowed values: {items_rule['enum']}"
        
        return True, None
    
    def _validate_custom_function(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate using custom validation functions."""
        function_name = rule.get('function')
        error_message = rule.get('error_message', 'Custom validation failed')
        
        # For now, we'll implement basic custom validations
        if function_name == 'check_exists_in_user_tasks':
            # This would typically check against a database
            # For now, we'll assume it's valid if it's a non-empty string
            if isinstance(value, str) and value.strip():
                return True, None
            else:
                return False, error_message
        
        return False, f"Unknown custom validation function: {function_name}"
    
    async def validate_ai_response(self, ai_response: Any) -> Dict[str, Any]:
        """Validate AI response using the validation engine."""
        # If already a dict, validate it directly
        if isinstance(ai_response, dict):
            return self._validate_dict_response(ai_response)
        
        # If string, clean and parse
        if isinstance(ai_response, str):
            return self._validate_string_response(ai_response)
        return {}
    
    def _validate_dict_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dictionary response."""
        if not isinstance(response, dict):
            return {}
        
        # Basic validation - ensure required fields exist
        validated = {}
        
        # Copy all fields
        for key, value in response.items():
            if value is not None and value != "" and value != []:
                validated[key] = value
        
        return validated
    
    def _validate_string_response(self, response: str) -> Dict[str, Any]:
        """Validate and clean string response."""
        if not response or not response.strip():
            return {}
        
        # Clean the response string
        cleaned_response = self._clean_response_string(response)
        
        # Try to parse as JSON
        try:
            import json
            parsed = json.loads(cleaned_response)
            if isinstance(parsed, dict):
                return self._validate_dict_response(parsed)
            else:
                return {}
        except json.JSONDecodeError as e:
            return {}
    
    def _clean_response_string(self, response: str) -> str:
        """Clean response string to handle common formatting issues."""
        import re
        
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        # Find JSON object boundaries
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx + 1]
        
        # Clean common JSON issues
        response = response.strip()
        
        # Remove trailing commas before closing braces/brackets
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        
        # Remove trailing commas at the end of lines
        response = re.sub(r',(\s*\n\s*[}\]])', r'\1', response)
        
        # Remove trailing commas at the end
        response = re.sub(r',\s*$', '', response)
        
        return response 