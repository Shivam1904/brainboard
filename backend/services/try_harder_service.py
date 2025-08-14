"""
Try Harder Service - Handles context gathering and AI retry for missing fields
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.models.llm_client import LLMClient
from services.ai_tool_preprocessing import CreationPreprocessing, EditingPreprocessing, AnalysisPreprocessing

logger = logging.getLogger(__name__)

class TryHarderService:
    """Service for handling try_harder strategy with context gathering and AI retry."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the try harder service."""
        self.db_session = db_session
        self.llm_client = LLMClient()
        
        # Initialize preprocessing services
        self.creation_preprocessing = CreationPreprocessing(db_session)
        self.editing_preprocessing = EditingPreprocessing(db_session)
        self.analysis_preprocessing = AnalysisPreprocessing(db_session)
    
    async def execute_try_harder_strategy(
        self, 
        intent: str, 
        ai_response: Dict[str, Any], 
        context: Dict[str, Any], 
        missing_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Execute try_harder strategy: gather context and retry AI once.
        
        Returns:
            Dict with success status and either enhanced AI response or fallback info
        """
        try:
            # Step 1: Gather enhanced context
            enhanced_context = await self._gather_enhanced_context(intent, ai_response, context, missing_fields)
            
            # Step 2: Retry AI with enhanced context (ONLY ONCE)
            retry_result = await self._retry_ai_with_enhanced_context(intent, ai_response, enhanced_context)
            
            if retry_result["success"]:
                return {
                    "success": True,
                    "action": "proceed_with_enhanced",
                    "enhanced_ai_response": retry_result["enhanced_ai_response"],
                    "context_gathered": enhanced_context,
                    "retry_attempts": 1
                }
            else:
                # AI retry failed - fall back to ask_user
                return {
                    "success": False,
                    "action": "fallback_to_ask_user",
                    "reason": "AI retry failed",
                    "context_gathered": enhanced_context,
                    "retry_attempts": 1
                }
                
        except Exception as e:
            logger.error(f"Try harder strategy execution failed: {e}")
            return {
                "success": False,
                "action": "fallback_to_ask_user",
                "reason": f"Error: {str(e)}",
                "retry_attempts": 1
            }
    
    async def _gather_enhanced_context(
        self, 
        intent: str, 
        ai_response: Dict[str, Any], 
        context: Dict[str, Any], 
        missing_fields: List[str]
    ) -> Dict[str, Any]:
        """Gather enhanced context from multiple sources."""
        enhanced_context = {
            "original_context": context.copy(),
            "ai_response": ai_response.copy(),
            "missing_fields": missing_fields,
            "found_fields": self._get_found_fields(ai_response),
            "chat_history": context.get("user_chats", []),
            "user_tasks": context.get("user_tasks", []),
            "todays_date": context.get("todays_date", ""),
            "context_sources": {},
            "gathered_data": {},
            "missing_fields_analysis": self._analyze_missing_fields(intent, missing_fields),
            "previous_try_harder_attempts": context.get("previous_try_harder_attempts", [])
        }
        
        # Use handlers for different types of context gathering
        context_handlers = self._get_context_handlers(intent)
        
        for handler_name, handler_func in context_handlers.items():
            try:
                handler_result = await handler_func(ai_response, context)
                if handler_result["success"]:
                    enhanced_context["gathered_data"][handler_name] = handler_result["data"]
                    enhanced_context["context_sources"][handler_name] = handler_result["sources"]
            except Exception as e:
                logger.warning(f"Context handler {handler_name} failed: {e}")
                enhanced_context["gathered_data"][handler_name] = {"error": str(e)}
        
        # Add previous AI responses from chat history
        enhanced_context["previous_ai_responses"] = self._extract_previous_ai_responses(context.get("user_chat", []))
        
        # Add missing arguments analysis
        enhanced_context["missing_arguments"] = self._analyze_missing_arguments(intent, ai_response, missing_fields)
        
        return enhanced_context
    
    def _get_context_handlers(self, intent: str) -> Dict[str, callable]:
        """Get context handlers based on intent."""
        handlers = {}
        
        if intent == "adding":
            handlers.update({
                "user_context": self._gather_user_context,
                "existing_widgets": self._gather_existing_widgets,
                "user_categories": self._gather_user_categories
            })
        elif intent == "editing":
            handlers.update({
                "task_context": self._gather_task_context,
                "task_history": self._gather_task_history,
                "today_status": self._gather_today_status
            })
        elif intent == "analysing":
            handlers.update({
                "analysis_data": self._gather_analysis_data,
                "statistics": self._gather_statistics
            })
        
        return handlers
    
    async def _gather_user_context(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather user context for creation."""
        try:
            user_context = await self.creation_preprocessing.fetch_user_context("user_001")
            return {
                "success": user_context["success"],
                "data": user_context,
                "sources": ["database", "user_profile"]
            }
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_existing_widgets(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather existing widgets information."""
        try:
            user_context = await self.creation_preprocessing.fetch_user_context("user_001")
            if user_context["success"]:
                return {
                    "success": True,
                    "data": {
                        "total_widgets": len(user_context.get("existing_widgets", [])),
                        "widget_types": list(set([w.get("type") for w in user_context.get("existing_widgets", [])]))
                    },
                    "sources": ["database"]
                }
            return {"success": False, "data": {}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_user_categories(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather user categories information."""
        try:
            user_context = await self.creation_preprocessing.fetch_user_context("user_001")
            if user_context["success"]:
                return {
                    "success": True,
                    "data": {
                        "categories": user_context.get("categories", []),
                        "category_count": len(user_context.get("categories", []))
                    },
                    "sources": ["database"]
                }
            return {"success": False, "data": {}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_task_context(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather task context for editing."""
        try:
            picked_title = ai_response.get("picked_title")
            if picked_title:
                editing_context = await self.editing_preprocessing.fetch_editing_context(picked_title, "user_001")
                return {
                    "success": editing_context["success"],
                    "data": editing_context,
                    "sources": ["database", "task_history"]
                }
            return {"success": False, "data": {"error": "No task title provided"}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_task_history(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather task history information."""
        try:
            picked_title = ai_response.get("picked_title")
            if picked_title:
                editing_context = await self.editing_preprocessing.fetch_editing_context(picked_title, "user_001")
                if editing_context["success"]:
                    return {
                        "success": True,
                        "data": {
                            "monthly_stats": editing_context.get("widget_history", {}).get("monthly_stats", {}),
                            "recent_activity": editing_context.get("widget_history", {}).get("recent_activity", [])
                        },
                        "sources": ["database"]
                    }
            return {"success": False, "data": {}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_today_status(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather today's status for the task."""
        try:
            picked_title = ai_response.get("picked_title")
            if picked_title:
                editing_context = await self.editing_preprocessing.fetch_editing_context(picked_title, "user_001")
                if editing_context["success"]:
                    return {
                        "success": True,
                        "data": {
                            "today_status": editing_context.get("today_status", {}),
                            "exists": editing_context.get("today_status", {}).get("exists", False)
                        },
                        "sources": ["database"]
                    }
            return {"success": False, "data": {}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_analysis_data(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather analysis data."""
        try:
            analysis_data = await self.analysis_preprocessing.fetch_analysis_data("user_001")
            return {
                "success": analysis_data["success"],
                "data": analysis_data,
                "sources": ["database", "statistics"]
            }
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _gather_statistics(self, ai_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather statistical information."""
        try:
            analysis_data = await self.analysis_preprocessing.fetch_analysis_data("user_001")
            if analysis_data["success"]:
                return {
                    "success": True,
                    "data": {
                        "overall_stats": analysis_data.get("overall_stats", {}),
                        "categories": list(analysis_data.get("overall_stats", {}).get("categories", {}).keys()),
                        "analysis_capabilities": analysis_data.get("analysis_capabilities", [])
                    },
                    "sources": ["database"]
                }
            return {"success": False, "data": {}, "sources": []}
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}, "sources": []}
    
    async def _retry_ai_with_enhanced_context(
        self, 
        intent: str, 
        original_ai_response: Dict[str, Any], 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retry AI with enhanced context (ONLY ONCE)."""
        try:
            # Create enhanced prompt with additional context
            enhanced_prompt = self._create_enhanced_prompt(intent, original_ai_response, enhanced_context)
            
            messages = [
                {"role": "system", "content": "You are a conversational task management AI that interprets user conversations and outputs structured JSON in a fixed schema. You help users create, edit, and analyze their tasks and habits. Always respond with valid JSON following the exact field specifications provided."},
                {"role": "user", "content": enhanced_prompt}
            ]
            print("🟢 🟢 🟢 🟢 🟢 🟢 🟢 TRY HARDER SERVICE: Enhanced prompt: ", enhanced_prompt)
            response = await self.llm_client.call_openai(messages)
            print("🟢 🟢 🟢 🟢 🟢 🟢 🟢 TRY HARDER SERVICE: Response: ", response)
            if not response:
                return {"success": False, "message": "No response from OpenAI"}
            
            # Parse JSON response
            try:
                cleaned_response = self._clean_json_response(response)
                enhanced_ai_response = json.loads(cleaned_response)
                return {
                    "success": True,
                    "enhanced_ai_response": enhanced_ai_response,
                    "original_response": original_ai_response
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse enhanced AI response: {e}")
                return {"success": False, "message": f"Failed to parse AI response: {e}"}
                
        except Exception as e:
            logger.error(f"Error retrying AI with enhanced context: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _create_enhanced_prompt(self, intent: str, original_ai_response: Dict[str, Any], enhanced_context: Dict[str, Any]) -> str:
        """Create enhanced prompt with additional context."""
        try:
            # Read the original prompt template
            prompt_file_path = "../src/components/prompt_add_edit.txt"
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Prepare enhanced context data
            user_tasks_str = json.dumps(enhanced_context["user_tasks"])
            todays_date = enhanced_context["todays_date"]
            chat_str = json.dumps(enhanced_context["chat_history"], indent=2)
            
            # Create comprehensive enhanced context summary
            enhanced_context_summary = {
                "missing_fields": enhanced_context["missing_fields"],
                "found_fields": enhanced_context["found_fields"],
                "missing_arguments_analysis": enhanced_context["missing_arguments"],
                "missing_fields_analysis": enhanced_context.get("missing_fields_analysis", {}),
                "previous_ai_responses": enhanced_context["previous_ai_responses"],
                "previous_try_harder_attempts": enhanced_context.get("previous_try_harder_attempts", []),
                "gathered_data": enhanced_context.get("gathered_data", {}),
                "context_sources": enhanced_context.get("context_sources", {})
            }
            
            enhanced_context_str = json.dumps(enhanced_context_summary, indent=2)
            
            # Replace template placeholders with actual data
            # Replace the generic user_chat description with actual conversation data
            prompt_template = prompt_template.replace(
                '"user_chat": full conversation so far (with "sender": "user" or "ai").',
                f'"user_chat": {chat_str}'
            )
            
            # Replace other template placeholders
            prompt_template = prompt_template.replace(
                '"user_tasks": [list of user tasks]',
                f'"user_tasks": {user_tasks_str}'
            )
            
            prompt_template = prompt_template.replace(
                '"todays_date": "YYYY-MM-DD"',
                f'"todays_date": "{todays_date}"'
            )
            
            # Append the enhanced context to the prompt template
            enhanced_prompt = prompt_template + f"""

                ENHANCED CONTEXT:
                {{
                    "user_tasks": {user_tasks_str},
                    "todays_date": "{todays_date}",
                    "user_chat": {chat_str},
                    "enhanced_context": {enhanced_context_str}
                }}

                CONTEXT ANALYSIS:
                The AI has previously attempted to process this request but some fields are missing.
                Please use the enhanced context above to provide a more complete response.
                
                MISSING FIELDS: {', '.join(enhanced_context['missing_fields'])}
                FOUND FIELDS: {', '.join(enhanced_context['found_fields'].keys())}
                
                MISSING FIELDS ANALYSIS:
                {json.dumps(enhanced_context.get('missing_fields_analysis', {}), indent=2)}
                
                PREVIOUS TRY HARDER ATTEMPTS:
                {json.dumps(enhanced_context.get('previous_try_harder_attempts', []), indent=2)}
                
                GATHERED CONTEXT DATA:
                {json.dumps(enhanced_context.get('gathered_data', {}), indent=2)}
                
                INSTRUCTIONS:
                1. Analyze the enhanced context carefully, especially the missing fields analysis
                2. Consider previous try_harder attempts to avoid repeating the same approach
                3. Use the gathered context data to infer missing values where possible
                4. Consider the context sources for each piece of information
                5. Respond with valid JSON following the exact schema
                6. Include a confidence_score field indicating your confidence in the filled values
                7. If you cannot determine a value with high confidence, leave it empty rather than guessing
                
                Please respond with the appropriate JSON following the schema above, using the enhanced context to fill in missing information.
                """
            
            return enhanced_prompt
            
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_file_path}")
            return self._create_fallback_enhanced_prompt(intent, original_ai_response, enhanced_context)
        except Exception as e:
            logger.error(f"Error reading prompt file: {e}")
            return self._create_fallback_enhanced_prompt(intent, original_ai_response, enhanced_context)
    
    def _create_fallback_enhanced_prompt(self, intent: str, original_ai_response: Dict[str, Any], enhanced_context: Dict[str, Any]) -> str:
        """Create fallback enhanced prompt if the main prompt file cannot be read."""
        missing_fields = enhanced_context["missing_fields"]
        found_fields = enhanced_context["found_fields"]
        
        return f"""
        You are a conversational task management AI. Please respond with JSON.

        ENHANCED CONTEXT:
        {{
            "intent": "{intent}",
            "missing_fields": {json.dumps(missing_fields)},
            "found_fields": {json.dumps(found_fields)},
            "gathered_data": {json.dumps(enhanced_context.get('gathered_data', {}))}
        }}

        Please use this enhanced context to provide a complete response with all required fields.
        """
    
    def _get_found_fields(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Get all found fields from AI response."""
        found_fields = {}
        for key, value in ai_response.items():
            if value is not None and value != "" and value != []:
                found_fields[key] = value
        return found_fields
    
    def _extract_previous_ai_responses(self, chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract previous AI responses from chat history."""
        ai_responses = []
        for msg in chat_history:
            if msg.get("role") == "ai" and msg.get("msg"):
                # Try to parse as JSON if it looks like structured data
                try:
                    parsed = json.loads(msg["msg"])
                    if isinstance(parsed, dict) and "intent" in parsed:
                        ai_responses.append(parsed)
                except:
                    # Not JSON, but still an AI response
                    ai_responses.append({"raw_response": msg["msg"]})
        return ai_responses
    
    def _analyze_missing_arguments(self, intent: str, ai_response: Dict[str, Any], missing_fields: List[str]) -> Dict[str, Any]:
        """Analyze missing arguments and their context."""
        missing_analysis = {}
        
        for field in missing_fields:
            missing_analysis[field] = {
                "field_name": field,
                "is_required": True,  # Default to required
                "context_hints": [],
                "possible_sources": []
            }
        
        return missing_analysis
    
    def _analyze_missing_fields(self, intent: str, missing_fields: List[str]) -> Dict[str, Any]:
        """Analyze missing fields with detailed information about requirements and strategies."""
        missing_analysis = {}
        
        for field in missing_fields:
            missing_analysis[field] = {
                "field_name": field,
                "field_type": "unknown",
                "is_required": True,  # Default to required
                "strategy": "try_harder",
                "context_data": [],
                "fallback_strategy": "ask_user",
                "description": f"Missing field: {field}",
                "possible_sources": [],
                "confidence_required": 0.8
            }
        
        return missing_analysis
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response to handle markdown formatting and common JSON issues."""
        if not response:
            return "{}"
        
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
        import re
        # Remove trailing commas before } or ]
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        
        # Remove trailing commas at the end of lines
        response = re.sub(r',(\s*\n\s*[}\]])', r'\1', response)
        
        return response.strip() 