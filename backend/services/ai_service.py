"""
AI service for handling all AI operations including daily plan generation and web summary generation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import requests

from models.daily_widgets_ai_output import DailyWidgetsAIOutput
from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widget import DailyWidget
from models.todo_details import TodoDetails
from models.todo_item_activity import TodoItemActivity
from models.single_item_tracker_details import SingleItemTrackerDetails
from models.single_item_tracker_item_activity import SingleItemTrackerItemActivity
from models.alarm_details import AlarmDetails
from models.alarm_item_activity import AlarmItemActivity
from models.websearch_details import WebSearchDetails
from models.websearch_item_activity import WebSearchItemActivity
from ai_engine.models.llm_client import LLMClient
from ai_engine.prompts.intent_recognition import IntentRecognitionPrompts
from ai_engine.prompts.parameter_extraction import ParameterExtractionPrompts
from ai_engine.prompts.followup_questions import FollowupQuestionPrompts
from ai_engine.prompts.confirmation_messages import ConfirmationMessagePrompts
from ai_engine.models.intent_models import IntentResponse, ParameterExtractionResponse

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default values
DEFAULT_USER = "user_001"
DEFAULT_SYSTEM_USER = "system"

# ============================================================================
# AI SERVICE CLASS
# ============================================================================
class AIService:
    """Service for handling all AI operations including daily plans and web summaries."""
    
    def __init__(self, db_session: AsyncSession = None):
        """Initialize the AI service."""
        self.llm_client = LLMClient()
        self.db_session = db_session
    
    # ============================================================================
    # DAILY PLAN GENERATION
    # ============================================================================
    
    async def generate_daily_plan(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Generate daily plan for a user on a specific date
        - Permanent widgets go directly to DailyWidgets
        - Non-permanent widgets are processed by AI service
        """
        try:
            # Get all user widgets
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widgets = result.scalars().all()
            
            if not widgets:
                logger.warning(f"No widgets found for user {user_id}")
                return {
                    "message": "No widgets found for today's plan",
                    "date": target_date.isoformat(),
                    "widgets_processed": 0,
                    "permanent_widgets_added": 0,
                    "ai_widgets_processed": 0
                }
            
            # Separate permanent widgets from regular widgets
            permanent_widgets = [w for w in widgets if w.is_permanent]
            regular_widgets = [w for w in widgets if not w.is_permanent]
            
            permanent_widgets_added = 0
            ai_widgets_processed = 0
            
            # Process permanent widgets directly
            if permanent_widgets:
                permanent_widgets_added = await self._process_permanent_widgets(
                    permanent_widgets, target_date, user_id
                )
            
            # Process regular widgets through AI service
            if regular_widgets:
                ai_widgets_processed = await self._process_ai_widgets(
                    regular_widgets, target_date, user_id
                )
            
            return {
                "message": "Today's plan generated successfully",
                "date": target_date.isoformat(),
                "widgets_processed": len(widgets),
                "permanent_widgets_added": permanent_widgets_added,
                "ai_widgets_processed": ai_widgets_processed
            }
            
        except Exception as e:
            logger.error(f"Failed to generate daily plan for user {user_id}: {e}")
            raise
    
    async def _process_permanent_widgets(
        self, 
        permanent_widgets: List[DashboardWidgetDetails], 
        target_date: date, 
        user_id: str
    ) -> int:
        """Process permanent widgets directly to daily widgets."""
        try:
            widgets_added = 0
            
            for widget in permanent_widgets:
                # Check if daily widget already exists for this date
                stmt = select(DailyWidget).where(
                    and_(
                        DailyWidget.widget_ids.contains([widget.id]),
                        DailyWidget.date == target_date
                    )
                )
                result = await self.db_session.execute(stmt)
                existing = result.scalars().first()
                
                if not existing:
                    # Create daily widget
                    daily_widget = DailyWidget(
                        widget_ids=[widget.id],
                        widget_type=widget.widget_type,
                        priority="HIGH",
                        reasoning="Permanent widget - automatically included",
                        date=target_date,
                        created_by=user_id
                    )
                    self.db_session.add(daily_widget)
                    widgets_added += 1
            
            await self.db_session.commit()
            return widgets_added
            
        except Exception as e:
            logger.error(f"Failed to process permanent widgets: {e}")
            await self.db_session.rollback()
            raise
    
    async def _process_ai_widgets(
        self, 
        regular_widgets: List[DashboardWidgetDetails], 
        target_date: date, 
        user_id: str
    ) -> int:
        """Process regular widgets through AI service."""
        try:
            # Create widget context for AI
            widget_context = []
            for widget in regular_widgets:
                widget_context.append({
                    "id": widget.id,
                    "title": widget.title,
                    "widget_type": widget.widget_type,
                    "importance": widget.importance,
                    "frequency": widget.frequency,
                    "category": widget.category
                })
            
            # Generate AI plan
            try:
                ai_result = await self._generate_daily_plan_with_llm(widget_context, target_date)
                ai_plan = ai_result["plan"]
            except Exception as e:
                logger.error(f"AI plan generation failed, using fallback: {e}")
                ai_plan = self._generate_fallback_daily_plan(widget_context)
            
            # Process AI plan and create outputs
            ai_outputs = []
            for plan_item in ai_plan:
                widget_id = plan_item.get("widget_id")
                if widget_id:
                    ai_output = DailyWidgetsAIOutput(
                        widget_id=widget_id,
                        priority=plan_item.get("priority", "MEDIUM"),
                        reasoning=plan_item.get("reasoning", ""),
                        result_json=plan_item,
                        date=target_date,
                        ai_model_used=ai_result.get("model_used"),
                        ai_prompt_used=ai_result.get("prompt_used"),
                        ai_response_time=ai_result.get("response_time"),
                        confidence_score=ai_result.get("confidence_score"),
                        generation_type=ai_result.get("model_used", "fallback"),
                        created_by=user_id
                    )
                    self.db_session.add(ai_output)
                    ai_outputs.append(ai_output)
            
            await self.db_session.commit()
            return len(ai_outputs)
            
        except Exception as e:
            logger.error(f"Failed to process AI widgets: {e}")
            await self.db_session.rollback()
            raise
    
    async def _generate_daily_plan_with_llm(self, widgets: List[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Generate daily plan using LLM."""
        try:
            prompt = self._create_daily_plan_prompt(widgets, target_date)
            
            # Measure response time
            start_time = time.time()
            
            response = await self.llm_client.call_openai([
                {"role": "system", "content": "You are an intelligent personal productivity assistant that creates daily plans based on user widgets. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ])
            
            response_time = time.time() - start_time
            
            if not response:
                logger.warning("OpenAI client not available - using fallback logic")
                fallback_plan = self._generate_fallback_daily_plan(widgets)
                return {
                    "plan": fallback_plan,
                    "prompt_used": None,
                    "response_time": None,
                    "confidence_score": None,
                    "model_used": "fallback"
                }
            
            # Parse JSON response
            try:
                plan = json.loads(response)
                
                # Validate plan structure
                if not isinstance(plan, list):
                    raise ValueError("Response is not a list")
                
                # Ensure all required fields are present
                for item in plan:
                    if not all(key in item for key in ["widget_id", "selected", "priority", "reasoning"]):
                        raise ValueError("Missing required fields in plan item")
                
                return {
                    "plan": plan,
                    "prompt_used": prompt,
                    "response_time": f"{response_time:.2f}s",
                    "confidence_score": "0.85",
                    "model_used": "gpt-3.5-turbo"
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                fallback_plan = self._generate_fallback_daily_plan(widgets)
                return {
                    "plan": fallback_plan,
                    "prompt_used": prompt,
                    "response_time": f"{response_time:.2f}s",
                    "confidence_score": "0.30",
                    "model_used": "gpt-3.5-turbo"
                }
                
        except Exception as e:
            logger.error(f"LLM daily plan generation failed: {e}")
            fallback_plan = self._generate_fallback_daily_plan(widgets)
            return {
                "plan": fallback_plan,
                "prompt_used": None,
                "response_time": None,
                "confidence_score": "0.10",
                "model_used": "fallback"
            }
    
    def _generate_fallback_daily_plan(self, widgets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate fallback daily plan using simple logic."""
        plan = []
        
        for widget in widgets:
            # Simple logic: prioritize daily widgets and high importance
            priority_score = widget['importance']
            if widget['frequency'] == "daily":
                priority_score += 0.2
            elif widget['frequency'] == "weekly":
                priority_score += 0.1
            
            priority = "HIGH" if priority_score > 0.7 else "MEDIUM" if priority_score > 0.4 else "LOW"
            selected = priority_score > 0.3  # Select widgets with reasonable importance
            
            plan.append({
                "widget_id": widget['id'],
                "selected": selected,
                "priority": priority,
                "reasoning": f"Fallback: Selected based on importance ({widget['importance']}) and frequency ({widget['frequency']})"
            })
        
        return plan
    
    def _create_daily_plan_prompt(self, widgets: List[Dict[str, Any]], target_date: date) -> str:
        """Create a prompt for LLM to generate daily plan."""
        widgets_text = ""
        for i, widget in enumerate(widgets, 1):
            widgets_text += f"""
{i}. Widget ID: {widget['id']}
   Title: {widget['title']}
   Type: {widget['widget_type']}
   Importance: {widget['importance']}
   Frequency: {widget['frequency']}
   Category: {widget['category']}
"""
        
        prompt = f"""
You are an intelligent personal productivity assistant. Based on the user's widgets below, create a daily plan for {target_date.strftime('%Y-%m-%d')}.

Available Widgets:
{widgets_text}

Please analyze each widget and decide which ones should be included in today's plan. Consider:
- Widget importance and frequency
- User's productivity patterns
- Balance between different types of activities
- Realistic daily capacity

For each widget, provide:
- widget_id: The widget's ID
- selected: true/false whether to include in today's plan
- priority: "HIGH", "MEDIUM", or "LOW"
- reasoning: Brief explanation for your decision

Respond with a JSON array like this:
[
  {{
    "widget_id": "widget_123",
    "selected": true,
    "priority": "HIGH",
    "reasoning": "High importance daily task that should be prioritized"
  }},
  {{
    "widget_id": "widget_456",
    "selected": false,
    "priority": "LOW",
    "reasoning": "Weekly task that can be postponed"
  }}
]

Please provide only the JSON array, no additional text.
"""
        return prompt
    
    # ============================================================================
    # WEB SUMMARY GENERATION
    # ============================================================================
    
    async def generate_web_summaries(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """Generate web summaries for user's websearch widgets."""
        try:
            # Get user's websearch widgets
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.widget_type == "websearch",
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            websearch_widgets = result.scalars().all()
            
            if not websearch_widgets:
                return {
                    "message": "No websearch widgets found",
                    "date": target_date.isoformat(),
                    "summaries_generated": 0
                }
            
            summaries_generated = 0
            
            for widget in websearch_widgets:
                # Get websearch details
                stmt = select(WebSearchDetails).where(WebSearchDetails.widget_id == widget.id)
                result = await self.db_session.execute(stmt)
                websearch_details = result.scalars().first()
                
                if websearch_details and websearch_details.search_query:
                    try:
                        summary_result = await self._generate_web_summary(
                            websearch_details.search_query, 
                            websearch_details.id,
                            target_date,
                            user_id
                        )
                        if summary_result:
                            summaries_generated += 1
                    except Exception as e:
                        logger.error(f"Failed to generate summary for widget {widget.id}: {e}")
            
            return {
                "message": "Web summaries generated successfully",
                "date": target_date.isoformat(),
                "summaries_generated": summaries_generated
            }
            
        except Exception as e:
            logger.error(f"Failed to generate web summaries for user {user_id}: {e}")
            raise
    
    async def _generate_web_summary(
        self, 
        query: str, 
        websearch_details_id: str, 
        target_date: date, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Generate web summary for a specific query."""
        try:
            # Perform web search
            search_results = await self._perform_web_search(query)
            
            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                return None
            
            # Generate AI summary
            summary_result = await self._generate_summary_with_openai(query, search_results)
            
            # Store summary in database (using existing WebSearchSummaryAIOutput model)
            from models.websearch_summary_ai_output import WebSearchSummaryAIOutput
            
            summary_output = WebSearchSummaryAIOutput(
                websearchdetails_id=websearch_details_id,
                summary_text=summary_result["summary"],
                result_json=summary_result,
                date=target_date,
                ai_model_used=summary_result.get("model_used"),
                ai_prompt_used=summary_result.get("prompt_used"),
                ai_response_time=summary_result.get("response_time"),
                confidence_score=summary_result.get("confidence_score"),
                generation_type=summary_result.get("model_used", "fallback"),
                created_by=user_id
            )
            
            self.db_session.add(summary_output)
            await self.db_session.commit()
            
            return summary_result
            
        except Exception as e:
            logger.error(f"Failed to generate web summary for query '{query}': {e}")
            await self.db_session.rollback()
            return None
    
    async def _perform_web_search(self, query: str) -> List[Dict[str, str]]:
        """Perform web search using Serper API."""
        try:
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                raise ValueError("SERPER_API_KEY not found in environment variables")
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": 5  # Get top 5 results
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            search_response = response.json()
            return self._parse_search_results(search_response)
            
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return []
    
    def _parse_search_results(self, search_response: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse and format Serper API search results."""
        try:
            results = []
            organic_results = search_response.get("organic", [])
            
            for result in organic_results[:5]:  # Top 5 results
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "combined_text": f"Title: {result.get('title', '')}\nURL: {result.get('link', '')}\nSnippet: {result.get('snippet', '')}"
                }
                results.append(formatted_result)
            
            return results
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
            return []
    
    async def _generate_summary_with_openai(self, query: str, search_results: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate summary using OpenAI."""
        try:
            prompt = self._create_summarization_prompt(query, search_results)
            
            # Measure response time
            start_time = time.time()
            
            response = await self.llm_client.call_openai([
                {"role": "system", "content": "You are a helpful AI assistant that provides accurate, concise summaries of web search results."},
                {"role": "user", "content": prompt}
            ])
            
            response_time = time.time() - start_time
            
            if not response:
                logger.warning("OpenAI client not available - using fallback summary")
                return {
                    "summary": "OpenAI API not configured. Using fallback summary.",
                    "response_time": None,
                    "confidence_score": "0.10",
                    "model_used": "fallback",
                    "prompt_used": prompt
                }
            
            summary = response.strip()
            
            return {
                "summary": summary,
                "response_time": f"{response_time:.2f}s",
                "confidence_score": "0.85",
                "model_used": "gpt-3.5-turbo",
                "prompt_used": prompt
            }
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {
                "summary": "Unable to generate AI summary. Please check the search results directly.",
                "response_time": None,
                "confidence_score": "0.20",
                "model_used": "fallback",
                "prompt_used": None
            }
    
    def _create_summarization_prompt(self, query: str, search_results: List[Dict[str, str]]) -> str:
        """Create a prompt for OpenAI summarization."""
        combined_content = "\n\n---\n\n".join([result["combined_text"] for result in search_results])
        
        prompt = f"""
You are a helpful AI assistant that provides concise, factual summaries of web search results.

ORIGINAL QUERY: {query}

SEARCH RESULTS:
{combined_content}

Please provide a comprehensive summary that:
1. Directly addresses the original query
2. Highlights the most relevant and recent information
3. Includes key facts and insights
4. Is concise but thorough (2-3 paragraphs maximum)
5. Maintains factual accuracy
6. Cites sources when appropriate

SUMMARY:
"""
        return prompt
    
    # ============================================================================
    # ACTIVITY GENERATION FROM AI OUTPUTS
    # ============================================================================
    
    async def generate_activity_from_plan(self, target_date: date, user_id: str) -> Dict[str, Any]:
        """Generate activities from AI outputs."""
        try:
            # Get AI outputs for the date
            stmt = select(DailyWidgetsAIOutput).where(
                and_(
                    DailyWidgetsAIOutput.date == target_date,
                    DailyWidgetsAIOutput.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            ai_outputs = result.scalars().all()
            
            if not ai_outputs:
                return {
                    "message": "No AI outputs found for the specified date",
                    "date": target_date.isoformat(),
                    "activities_created": 0
                }
            
            # Group widgets by type
            widgets_by_type = {}
            for ai_output in ai_outputs:
                stmt = select(DashboardWidgetDetails).where(DashboardWidgetDetails.id == ai_output.widget_id)
                result = await self.db_session.execute(stmt)
                widget = result.scalars().first()
                
                if widget:
                    if widget.widget_type not in widgets_by_type:
                        widgets_by_type[widget.widget_type] = []
                    widgets_by_type[widget.widget_type].append(widget.id)
            
            activities_created = 0
            
            # Create daily widgets and activities
            for widget_type, widget_ids in widgets_by_type.items():
                daily_widget = DailyWidget(
                    widget_ids=widget_ids,
                    widget_type=widget_type,
                    priority="HIGH",  # TODO: Get from AI output
                    reasoning=f"AI selected {len(widget_ids)} {widget_type} widgets",
                    date=target_date,
                    created_by=user_id
                )
                self.db_session.add(daily_widget)
                await self.db_session.flush()  # Get the ID
                
                # Create activity entries
                activities_created += await self._create_activity_entries(
                    daily_widget.id, widget_ids, widget_type, user_id
                )
            
            await self.db_session.commit()
            
            return {
                "message": "Activities generated successfully from AI plan",
                "date": target_date.isoformat(),
                "activities_created": activities_created
            }
            
        except Exception as e:
            logger.error(f"Failed to generate activities from AI plan: {e}")
            await self.db_session.rollback()
            raise
    
    async def _create_activity_entries(
        self, 
        daily_widget_id: str, 
        widget_ids: List[str], 
        widget_type: str, 
        user_id: str
    ) -> int:
        """Create activity entries for widgets."""
        activities_created = 0
        
        for widget_id in widget_ids:
            if widget_type in ["todo-habit", "todo-task", "todo-event"]:
                stmt = select(TodoDetails).where(TodoDetails.widget_id == widget_id)
                result = await self.db_session.execute(stmt)
                todo_details = result.scalars().first()
                
                if todo_details:
                    activity = TodoItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        tododetails_id=todo_details.id,
                        status="pending",
                        progress=0,
                        created_by=user_id
                    )
                    self.db_session.add(activity)
                    activities_created += 1
            
            elif widget_type == "singleitemtracker":
                stmt = select(SingleItemTrackerDetails).where(SingleItemTrackerDetails.widget_id == widget_id)
                result = await self.db_session.execute(stmt)
                tracker_details = result.scalars().first()
                
                if tracker_details:
                    activity = SingleItemTrackerItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        singleitemtrackerdetails_id=tracker_details.id,
                        created_by=user_id
                    )
                    self.db_session.add(activity)
                    activities_created += 1
            
            elif widget_type == "alarm":
                stmt = select(AlarmDetails).where(AlarmDetails.widget_id == widget_id)
                result = await self.db_session.execute(stmt)
                alarm_details = result.scalars().first()
                
                if alarm_details:
                    activity = AlarmItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        alarmdetails_id=alarm_details.id,
                        created_by=user_id
                    )
                    self.db_session.add(activity)
                    activities_created += 1
            
            elif widget_type == "websearch":
                stmt = select(WebSearchDetails).where(WebSearchDetails.widget_id == widget_id)
                result = await self.db_session.execute(stmt)
                websearch_details = result.scalars().first()
                
                if websearch_details:
                    activity = WebSearchItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        websearchdetails_id=websearch_details.id,
                        status="pending",
                        created_by=user_id
                    )
                    self.db_session.add(activity)
                    activities_created += 1
        
        return activities_created
    
    # ============================================================================
    # CHAT-RELATED METHODS (for backward compatibility)
    # ============================================================================
    
    async def recognize_intent(self, user_message: str, fallback_attempt: int = 0) -> Optional[IntentResponse]:
        """Recognize user intent from message."""
        try:
            messages = IntentRecognitionPrompts.create_messages(user_message, fallback_attempt)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for intent recognition")
                return None
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return IntentResponse(
                    intent=data.get("intent", "unknown"),
                    confidence=data.get("confidence", 0.0),
                    parameters=data.get("parameters", {}),
                    reasoning=data.get("reasoning", ""),
                    is_fallback=fallback_attempt > 0,
                    fallback_attempt=fallback_attempt
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return None
    
    async def extract_parameters(
        self, 
        user_message: str, 
        current_intent: str, 
        existing_parameters: Dict[str, Any],
        missing_parameters: List[str]
    ) -> Optional[ParameterExtractionResponse]:
        """Extract parameters from follow-up message."""
        try:
            messages = ParameterExtractionPrompts.create_messages(
                user_message, current_intent, existing_parameters, missing_parameters
            )
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for parameter extraction")
                return None
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return ParameterExtractionResponse(
                    updated_parameters=data.get("updated_parameters", {}),
                    missing_parameters=data.get("missing_parameters", []),
                    confidence=data.get("confidence", 0.0),
                    reasoning=data.get("reasoning", "")
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            return None
    
    async def generate_followup_question(
        self, 
        intent: str, 
        missing_parameters: List[str], 
        current_context: str = ""
    ) -> Optional[str]:
        """Generate follow-up question for missing information."""
        try:
            messages = FollowupQuestionPrompts.create_messages(intent, missing_parameters, current_context)
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for follow-up question")
                return None
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None
    
    async def generate_confirmation(self, intent: str, result: Dict[str, Any]) -> Optional[str]:
        """Generate confirmation message for successful operation."""
        try:
            if result.get("success"):
                messages = ConfirmationMessagePrompts.create_success_messages(intent, result)
            else:
                messages = ConfirmationMessagePrompts.create_error_messages(intent, result.get("message", ""))
            
            response = await self.llm_client.call_openai(messages)
            
            if not response:
                logger.error("No response from OpenAI for confirmation message")
                return None
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating confirmation message: {e}")
            return None
    
    def get_fallback_message(self, attempt: int) -> str:
        """Get predefined fallback message."""
        return IntentRecognitionPrompts.get_fallback_prompt(attempt) 