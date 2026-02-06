"""
Strategy Handler for AI Service
Implements configuration-based error handling strategies
"""

from typing import Dict, Any, List, Optional
from .config_loader import AIConfigLoader
from .validation_engine import ValidationEngine

class StrategyHandler:
    """Handles missing field strategies based on configuration."""
    
    def __init__(self, config_loader: AIConfigLoader, validation_engine: ValidationEngine):
        """Initialize strategy handler."""
        self.config = config_loader
        self.validator = validation_engine
    
    def handle_missing_fields(self, intent: str, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missing fields according to configuration strategies."""
        required_fields = self.config.get_required_fields(intent)
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if not missing_fields:
            return {
                'action': 'proceed',
                'message': 'All required fields present',
                'enhanced_data': data
            }
        
        # Apply strategies for each missing field
        strategies_to_apply = []
        enhanced_data = data.copy()
        
        for field in missing_fields:
            strategy_list = self.validator.get_missing_field_strategy(intent, field)
            if strategy_list and len(strategy_list) > 0:
                # Get the first strategy (assuming one strategy per field for now)
                strategy = strategy_list[0]
                strategies_to_apply.append({
                    'field': field,
                    'strategy': strategy.get('strategy'),
                    'strategy_config': strategy
                })
        
        # Determine overall action based on strategies
        if self._should_ask_user(strategies_to_apply):
            print("🟢 STRATEGY HANDLER: Asking user for missing information")
            return self._handle_ask_user_strategy(intent, missing_fields, data, context)
        elif self._should_try_harder(strategies_to_apply):
            print("🟢 STRATEGY HANDLER: Trying harder")
            return self._handle_try_harder_strategy(intent, missing_fields, data, context)
        elif self._should_use_defaults(strategies_to_apply):
            print("🟢 STRATEGY HANDLER: Using defaults")
            return self._handle_use_defaults_strategy(intent, missing_fields, data, context)
        else:
            # Default to ignore_argument for remaining fields
            return self._handle_ignore_argument_strategy(intent, missing_fields, data, context)
    
    def _should_ask_user(self, strategies: List[Dict[str, Any]]) -> bool:
        """Check if any strategy requires asking the user."""
        return any(s['strategy'] == 'ask_user' for s in strategies)
    
    def _should_try_harder(self, strategies: List[Dict[str, Any]]) -> bool:
        """Check if any strategy requires trying harder."""
        return any(s['strategy'] == 'try_harder' for s in strategies)
    
    def _should_use_defaults(self, strategies: List[Dict[str, Any]]) -> bool:
        """Check if any strategy requires using defaults."""
        return any(s['strategy'] == 'use_defaults' for s in strategies)
    
    def _handle_ask_user_strategy(self, intent: str, missing_fields: List[str], data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ask_user strategy - end flow and ask user for missing information."""
        missing_fields_str = ', '.join(missing_fields)
        
        # Use  from AI if available, otherwise fall back to default message
        message = data.get('ai_response')
        if not message:
            message = f"Please provide the following information: {missing_fields_str}"
        
        return {
            'action': 'ask_user',
            'message': message,
            'missing_fields': missing_fields,
            'intent': intent,
            'should_continue_chat': True,
            'response_type': 'ask_user'
        }
    
    def _handle_try_harder_strategy(self, intent: str, missing_fields: List[str], data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle try_harder strategy - fetch additional context."""
        try_harder_fields = [
            field for field in missing_fields 
            if self.validator.should_try_harder(intent, field)
        ]
        
        # Get required fields for this intent
        required_fields = self.config.get_required_fields(intent)
        optional_fields = self.config.get_optional_fields(intent)
        
        # Check if there was a previous try_harder attempt
        previous_try_harder = context.get("previous_try_harder_attempts", [])
        
        # Update context with missing fields information
        if "missing_fields_analysis" not in context:
            context["missing_fields_analysis"] = {}
        
        for field in missing_fields:
            if field not in context["missing_fields_analysis"]:
                context["missing_fields_analysis"][field] = {
                    "field_name": field,
                    "is_required": field in required_fields,
                    "is_optional": field in optional_fields,
                    "strategy": "try_harder" if field in try_harder_fields else "unknown"
                }
        
        return {
            'action': 'try_harder',
            'message': f"Let me get more context to help with: {', '.join(try_harder_fields)}",
            'missing_fields': try_harder_fields,
            'intent': intent,
            'should_continue_chat': True,
            'response_type': 'try_harder',
            'required_fields': required_fields,
            'optional_fields': optional_fields,
            'previous_try_harder_attempts': previous_try_harder
        }
    
    def _handle_use_defaults_strategy(self, intent: str, missing_fields: List[str], data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle use_defaults strategy - apply default values."""
        enhanced_data = data.copy()
        applied_defaults = []
        
        for field in missing_fields:
            if self.validator.should_apply_default(intent, field):
                default_value = self.validator.get_default_value(intent, field)
                if default_value is not None:
                    enhanced_data[field] = default_value
                    applied_defaults.append(field)
        
        if applied_defaults:
            return {
                'action': 'proceed_with_defaults',
                'message': f"Applied defaults for: {', '.join(applied_defaults)}",
                'enhanced_data': enhanced_data,
                'applied_defaults': applied_defaults,
                'intent': intent,
                'should_continue_chat': False,
                'response_type': 'defaults_applied'
            }
        else:
            # No defaults could be applied, fall back to try_harder
            return self._handle_try_harder_strategy(intent, missing_fields, data, context)
    
    def _handle_ignore_argument_strategy(self, intent: str, missing_fields: List[str], data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ignore_argument strategy - skip missing optional fields."""
        ignored_fields = [
            field for field in missing_fields 
            if self.validator.should_ignore_field(intent, field)
        ]
        
        if ignored_fields:
            return {
                'action': 'proceed_ignoring',
                'message': f"Proceeding without optional fields: {', '.join(ignored_fields)}",
                'enhanced_data': data,
                'ignored_fields': ignored_fields,
                'intent': intent,
                'should_continue_chat': False,
                'response_type': 'ignored_optional'
            }
        else:
            # No fields can be ignored, fall back to ask_user
            return self._handle_ask_user_strategy(intent, missing_fields, data, context)
    
    def _get_context_requirements(self, intent: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Get context requirements for missing fields."""
        context_requirements = []
        
        for field in fields:
            strategy = self.validator.get_missing_field_strategy(intent, field)
            if strategy and strategy.get('strategy') == 'try_harder':
                context_data = strategy.get('context_data', [])
                context_requirements.append({
                    'field': field,
                    'context_data': context_data,
                    'action': strategy.get('action', 'fetch_user_context'),
                    'description': strategy.get('description', '')
                })
        
        return context_requirements
    
    def get_try_harder_summary(self, intent: str, missing_fields: List[str]) -> Dict[str, Any]:
        """Get a comprehensive summary of what context can be gathered for try_harder strategy."""
        summary = {
            'intent': intent,
            'missing_fields': missing_fields,
            'context_gathering_plan': {},
            'estimated_success_rate': 0.0,
            'context_sources': {},
            'fallback_strategy': 'ask_user'
        }
        
        # Analyze each missing field
        total_fields = len(missing_fields)
        gatherable_fields = 0
        
        for field in missing_fields:
            strategy = self.validator.get_missing_field_strategy(intent, field)
            if strategy and strategy.get('strategy') == 'try_harder':
                context_data = strategy.get('context_data', [])
                gatherable_fields += 1
                
                summary['context_gathering_plan'][field] = {
                    'strategy': 'try_harder',
                    'context_data': context_data,
                    'context_sources': self._categorize_context_sources(context_data),
                    'estimated_confidence': self._estimate_confidence(context_data),
                    'fallback_strategy': strategy.get('fallback_strategy', 'ask_user')
                }
            else:
                summary['context_gathering_plan'][field] = {
                    'strategy': 'unknown',
                    'context_data': [],
                    'context_sources': {},
                    'estimated_confidence': 0.0,
                    'fallback_strategy': 'ask_user'
                }
        
        # Calculate estimated success rate
        if total_fields > 0:
            summary['estimated_success_rate'] = (gatherable_fields / total_fields) * 100
        
        # Get overall context sources
        summary['context_sources'] = self._get_context_sources(intent, missing_fields)
        
        # Determine fallback strategy
        if summary['estimated_success_rate'] < 50:
            summary['fallback_strategy'] = 'ask_user'
        elif summary['estimated_success_rate'] < 80:
            summary['fallback_strategy'] = 'use_defaults'
        else:
            summary['fallback_strategy'] = 'proceed_ignoring'
        
        return summary
    
    def _categorize_context_sources(self, context_data: List[str]) -> Dict[str, List[str]]:
        """Categorize context data by source type."""
        categories = {
            'database': [],
            'chat_history': [],
            'ai_responses': [],
            'user_profile': [],
            'existing_data': [],
            'inference': []
        }
        
        for data_type in context_data:
            if data_type.startswith('db_'):
                categories['database'].append(data_type)
            elif data_type.startswith('chat_'):
                categories['chat_history'].append(data_type)
            elif data_type.startswith('ai_'):
                categories['ai_responses'].append(data_type)
            elif data_type.startswith('profile_'):
                categories['user_profile'].append(data_type)
            elif data_type.startswith('existing_'):
                categories['existing_data'].append(data_type)
            elif data_type.startswith('infer_'):
                categories['inference'].append(data_type)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _estimate_confidence(self, context_data: List[str]) -> float:
        """Estimate confidence level for context gathering based on available data types."""
        if not context_data:
            return 0.0
        
        # Assign confidence scores to different data types
        confidence_scores = {
            'db_user_widgets': 0.9,
            'db_categories': 0.8,
            'db_user_preferences': 0.7,
            'chat_recent_messages': 0.6,
            'chat_user_patterns': 0.5,
            'ai_previous_responses': 0.4,
            'profile_user_habits': 0.7,
            'existing_similar_tasks': 0.8,
            'infer_from_context': 0.3
        }
        
        total_score = 0.0
        for data_type in context_data:
            total_score += confidence_scores.get(data_type, 0.5)
        
        return min(total_score / len(context_data), 1.0)
    
    def _get_context_sources(self, intent: str, fields: List[str]) -> Dict[str, List[str]]:
        """Get available context sources for missing fields."""
        sources = {
            'database': [],
            'chat_history': [],
            'ai_responses': [],
            'user_profile': [],
            'existing_data': []
        }
        
        for field in fields:
            strategy = self.validator.get_missing_field_strategy(intent, field)
            if strategy and strategy.get('strategy') == 'try_harder':
                context_data = strategy.get('context_data', [])
                
                for data_type in context_data:
                    if data_type.startswith('db_'):
                        sources['database'].append(field)
                    elif data_type.startswith('chat_'):
                        sources['chat_history'].append(field)
                    elif data_type.startswith('ai_'):
                        sources['ai_responses'].append(field)
                    elif data_type.startswith('profile_'):
                        sources['user_profile'].append(field)
                    elif data_type.startswith('existing_'):
                        sources['existing_data'].append(field)
        
        # Remove duplicates
        for key in sources:
            sources[key] = list(set(sources[key]))
        
        return sources
    
    def get_strategy_summary(self, intent: str) -> Dict[str, Any]:
        """Get a summary of strategies for an intent."""
        required_fields = self.config.get_required_fields(intent)
        optional_fields = self.config.get_optional_fields(intent)
        
        strategy_summary = {
            'intent': intent,
            'required_fields': {},
            'optional_fields': {},
            'strategies': {}
        }
        
        # Analyze required fields
        for field in required_fields:
            strategy_list = self.validator.get_missing_field_strategy(intent, field)
            if strategy_list and len(strategy_list) > 0:
                strategy = strategy_list[0]
                strategy_summary['required_fields'][field] = {
                    'strategy': strategy.get('strategy', 'unknown'),
                    'description': strategy.get('description', '')
                }
            else:
                strategy_summary['required_fields'][field] = {
                    'strategy': 'unknown',
                    'description': ''
                }
        
        # Analyze optional fields
        for field in optional_fields:
            strategy_list = self.validator.get_missing_field_strategy(intent, field)
            if strategy_list and len(strategy_list) > 0:
                strategy = strategy_list[0]
                strategy_summary['optional_fields'][field] = {
                    'strategy': strategy.get('strategy', 'unknown'),
                    'description': strategy.get('description', '')
                }
            else:
                strategy_summary['optional_fields'][field] = {
                    'strategy': 'unknown',
                    'description': ''
                }
        
        # Get strategy counts
        strategies = self.config.get_strategies()
        strategy_summary['strategies'] = {
            'available': list(strategies.keys()),
            'descriptions': {k: v.get('description', '') for k, v in strategies.items()}
        }
        
        return strategy_summary 