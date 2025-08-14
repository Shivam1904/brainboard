"""
Validation Engine for AI Service
Applies validation rules from the configuration file
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .config_loader import AIConfigLoader

class ValidationEngine:
    """Validates data according to configuration rules."""
    
    def __init__(self, config_loader: AIConfigLoader):
        """Initialize validation engine with configuration."""
        self.config = config_loader
    
    def validate_field(self, field_name: str, value: Any, rule_name: str) -> Tuple[bool, Optional[str]]:
        """Validate a single field against a validation rule."""
        rule = self.config.get_validation_rule(rule_name)
        if not rule:
            return False, f"Unknown validation rule: {rule_name}"
        
        rule_type = rule.get('type')
        
        try:
            if rule_type == 'string':
                return self._validate_string(value, rule)
            elif rule_type == 'enum':
                return self._validate_enum(value, rule)
            elif rule_type == 'integer':
                return self._validate_integer(value, rule)
            elif rule_type == 'float':
                return self._validate_float(value, rule)
            elif rule_type == 'boolean':
                return self._validate_boolean(value, rule)
            elif rule_type == 'array':
                return self._validate_array(value, rule)
            elif rule_type == 'validation_function':
                return self._validate_custom_function(value, rule)
            else:
                return False, f"Unknown rule type: {rule_type}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
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
    
    def validate_intent_data(self, intent: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all fields for an intent according to configuration."""
        validation_results = {
            'valid': True,
            'errors': [],
            'missing_required': [],
            'invalid_fields': []
        }
        
        # Get required and optional fields from config
        required_fields = self.config.get_required_fields(intent)
        optional_fields = self.config.get_optional_fields(intent)
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                validation_results['missing_required'].append(field)
                validation_results['valid'] = False
        
        # Validate present fields using tool arguments configuration
        tool_args = self.config.get_tool_arguments(intent)
        
        # Validate required fields
        required_tool_args = tool_args.get('required', [])
        for field_config in required_tool_args:
            field_name = field_config.get('name')
            if field_name and field_name in data and data[field_name] is not None:
                validation_rule = field_config.get('validation')
                if validation_rule:
                    is_valid, error_msg = self.validate_field(field_name, data[field_name], validation_rule)
                    if not is_valid:
                        validation_results['invalid_fields'].append({
                            'field': field_name,
                            'value': data[field_name],
                            'error': error_msg
                        })
                        validation_results['valid'] = False
        
        # Validate optional fields
        optional_tool_args = tool_args.get('optional', [])
        for field_config in optional_tool_args:
            field_name = field_config.get('name')
            if field_name and field_name in data and data[field_name] is not None:
                validation_rule = field_config.get('validation')
                if validation_rule:
                    is_valid, error_msg = self.validate_field(field_name, data[field_name], validation_rule)
                    if not is_valid:
                        validation_results['invalid_fields'].append({
                            'field': field_name,
                            'value': data[field_name],
                            'error': error_msg
                        })
                        validation_results['valid'] = False
        
        # Compile error messages
        if validation_results['missing_required']:
            validation_results['errors'].append(
                f"Missing required fields: {', '.join(validation_results['missing_required'])}"
            )
        
        for invalid_field in validation_results['invalid_fields']:
            validation_results['errors'].append(
                f"Field '{invalid_field['field']}' invalid: {invalid_field['error']}"
            )
        
        return validation_results
    
    def get_missing_field_strategy(self, intent: str, field: str) -> Optional[Dict[str, Any]]:
        """Get the strategy for handling a missing field."""
        return self.config.get_missing_field_strategy(intent, field)
    
    def should_apply_default(self, intent: str, field: str) -> bool:
        """Check if a field should use default values."""
        strategy = self.get_missing_field_strategy(intent, field)
        return strategy and strategy.get('strategy') == 'use_defaults'
    
    def get_default_value(self, intent: str, field: str) -> Any:
        """Get the default value for a field."""
        strategy = self.get_missing_field_strategy(intent, field)
        if strategy and strategy.get('strategy') == 'use_defaults':
            return strategy.get('default')
        return None
    
    def should_ignore_field(self, intent: str, field: str) -> bool:
        """Check if a field should be ignored when missing."""
        strategy = self.get_missing_field_strategy(intent, field)
        return strategy and strategy.get('strategy') == 'ignore_argument'
    
    def should_try_harder(self, intent: str, field: str) -> bool:
        """Check if a field should trigger try harder logic."""
        strategy = self.get_missing_field_strategy(intent, field)
        return strategy and strategy.get('strategy') == 'try_harder'
    
    def should_ask_user(self, intent: str, field: str) -> bool:
        """Check if a field should trigger asking the user."""
        strategy = self.get_missing_field_strategy(intent, field)
        return strategy and strategy.get('strategy') == 'ask_user' 