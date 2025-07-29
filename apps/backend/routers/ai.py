"""
AI Router - Internal AI APIs
Handles AI-generated daily plans and web summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date, datetime
import logging
import os
import json
import requests
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import asyncio

from core.database import get_db
from models.database import (
    User, DashboardWidgetDetails, DailyWidget, DailyWidgetsAIOutput,
    WebSearchSummaryAIOutput, ToDoItemActivity, SingleItemTrackerItemActivity,
    AlarmItemActivity, WebSearchDetails, WebSearchItemActivity, ToDoDetails,
    SingleItemTrackerDetails, AlarmDetails
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])

# Initialize OpenAI client (will be None if API key not available)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        default_user = User(
            email="default@brainboard.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user.id

# ============================================================================
# AI HELPER FUNCTIONS
# ============================================================================

def perform_web_search(query: str) -> Dict[str, Any]:
    """
    Perform web search using Serper API
    """
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
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Serper API request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Web search service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )

def parse_search_results(search_response: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Parse and format Serper API search results
    """
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

def create_summarization_prompt(query: str, search_results: List[Dict[str, str]]) -> str:
    """
    Create a prompt for OpenAI summarization
    """
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

async def generate_summary_with_openai(prompt: str) -> Dict[str, Any]:
    """
    Generate summary using OpenAI
    Returns dict with summary and metadata
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not available - using fallback summary")
            return {
                "summary": "OpenAI API not configured. Using fallback summary.",
                "response_time": None,
                "confidence_score": "0.10",
                "model_used": "fallback"
            }
        
        # Measure response time
        import time
        start_time = time.time()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that provides accurate, concise summaries of web search results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistent factual summaries
            max_tokens=500
        )
        
        response_time = time.time() - start_time
        summary = response.choices[0].message.content.strip()
        
        return {
            "summary": summary,
            "response_time": f"{response_time:.2f}s",
            "confidence_score": "0.85",  # High confidence for successful generation
            "model_used": "gpt-3.5-turbo"
        }
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return {
            "summary": "Unable to generate AI summary. Please check the search results directly.",
            "response_time": None,
            "confidence_score": "0.20",
            "model_used": "fallback"
        }

def create_fallback_summary(search_results: List[Dict[str, str]]) -> str:
    """
    Create a fallback summary from raw search results
    """
    if not search_results:
        return "No relevant information found."
    
    summary_parts = []
    for i, result in enumerate(search_results[:3], 1):
        summary_parts.append(f"{i}. {result['title']}\n   {result['snippet'][:200]}...")
    
    return "\n\n".join(summary_parts)

def create_daily_plan_prompt(widgets: List[Dict[str, Any]], target_date: date) -> str:
    """
    Create a prompt for LLM to generate daily plan
    """
    widgets_text = ""
    for i, widget in enumerate(widgets, 1):
        widgets_text += f"""
{i}. Widget ID: {widget['id']}
   Title: {widget['title']}
   Type: {widget['widget_type']}
   Category: {widget['category']}
   Importance: {widget['importance']} (0.0-1.0 scale)
   Frequency: {widget['frequency']}
"""
    
    prompt = f"""
You are an intelligent personal productivity assistant. Your task is to analyze the user's widgets and create a daily plan for {target_date}.

AVAILABLE WIDGETS:
{widgets_text}

TASK: Analyze each widget and determine:
1. Which widgets should be included in today's plan
2. Priority level for each selected widget (HIGH/MEDIUM/LOW)
3. Reasoning for your selection

CONSIDERATIONS:
- Daily widgets should generally be prioritized
- Higher importance scores (0.8+) should be prioritized
- Consider category balance (Health, Productivity, Fun, etc.)
- Weekly widgets might be due today
- Don't overwhelm the user - select 3-8 widgets for today

RESPONSE FORMAT (JSON array):
[
  {{
    "widget_id": "widget_id_here",
    "selected": true/false,
    "priority": "HIGH/MEDIUM/LOW",
    "reasoning": "Brief explanation of why this widget was selected/rejected for today"
  }}
]

Please provide only the JSON array, no additional text.
"""
    return prompt

async def generate_daily_plan_with_llm(widgets: List[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
    """
    Generate daily plan using LLM
    Returns dict with plan data and metadata
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not available - using fallback logic")
            fallback_plan = generate_fallback_daily_plan(widgets)
            return {
                "plan": fallback_plan,
                "prompt_used": None,
                "response_time": None,
                "confidence_score": None,
                "model_used": "fallback"
            }
        
        prompt = create_daily_plan_prompt(widgets, target_date)
        
        # Measure response time
        import time
        start_time = time.time()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intelligent personal productivity assistant that creates daily plans based on user widgets. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistent planning
            max_tokens=1000
        )
        
        response_time = time.time() - start_time
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            import json
            plan = json.loads(response_text)
            
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
                "confidence_score": "0.85",  # Estimated confidence for successful parsing
                "model_used": "gpt-3.5-turbo"
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Response text: {response_text}")
            fallback_plan = generate_fallback_daily_plan(widgets)
            return {
                "plan": fallback_plan,
                "prompt_used": prompt,
                "response_time": f"{response_time:.2f}s",
                "confidence_score": "0.30",  # Low confidence due to parsing failure
                "model_used": "gpt-3.5-turbo"
            }
            
    except Exception as e:
        logger.error(f"LLM daily plan generation failed: {e}")
        fallback_plan = generate_fallback_daily_plan(widgets)
        return {
            "plan": fallback_plan,
            "prompt_used": None,
            "response_time": None,
            "confidence_score": "0.10",  # Very low confidence due to error
            "model_used": "fallback"
        }

def generate_fallback_daily_plan(widgets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate fallback daily plan using simple logic
    """
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

# ============================================================================
# AI INTERNAL APIs
# ============================================================================

@router.post("/generate_today_plan")
async def generate_today_plan(
    target_date: Optional[date] = Query(None, description="Date for plan generation (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Internal AI API: Generate today's plan
    Responsible for generating DailyWidgetsAIOutput
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        # Get all user widgets
        widgets = db.query(DashboardWidgetDetails).filter(
            DashboardWidgetDetails.user_id == user_id,
            DashboardWidgetDetails.delete_flag == False
        ).all()
        
        # AI Logic: Use LLM to generate intelligent daily plan
        ai_outputs = []
        
        if not widgets:
            logger.warning(f"No widgets found for user {user_id}")
            return {
                "message": "No widgets found for today's plan",
                "date": target_date.isoformat(),
                "widgets_processed": 0,
                "ai_outputs_created": 0
            }
        
        # Create widget context for LLM
        widget_context = []
        for widget in widgets:
            widget_context.append({
                "id": widget.id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "category": widget.category
            })
        
        # Generate AI plan using LLM
        try:
            ai_result = await generate_daily_plan_with_llm(widget_context, target_date)
            ai_plan = ai_result["plan"]
            
            # Process AI plan and create outputs
            for plan_item in ai_plan:
                widget_id = plan_item.get("widget_id")
                priority = plan_item.get("priority", "MEDIUM")
                reasoning = plan_item.get("reasoning", "AI selected this widget for today")
                selected = plan_item.get("selected", False)
                
                # Find the corresponding widget
                widget = next((w for w in widgets if w.id == widget_id), None)
                if not widget:
                    continue
                
                ai_output = DailyWidgetsAIOutput(
                    widget_id=widget_id,
                    priority=priority,
                    reasoning=reasoning,
                    result_json={
                        "priority": priority,
                        "selected_for_today": selected,
                        "importance": widget.importance,
                        "frequency": widget.frequency,
                        "category": widget.category,
                        "widget_type": widget.widget_type,
                        "ai_reasoning": reasoning
                    },
                    date=target_date,
                    ai_model_used=ai_result["model_used"],
                    ai_prompt_used=ai_result["prompt_used"],
                    ai_response_time=ai_result["response_time"],
                    confidence_score=ai_result["confidence_score"],
                    generation_type="ai_generated",
                    created_by=user_id
                )
                db.add(ai_output)
                ai_outputs.append(ai_output)
                
        except Exception as e:
            logger.error(f"LLM plan generation failed, using fallback logic: {e}")
            # Fallback to simple logic if LLM fails
            for widget in widgets:
                priority_score = widget.importance
                if widget.frequency == "daily":
                    priority_score += 0.2
                elif widget.frequency == "weekly":
                    priority_score += 0.1
                
                priority = "HIGH" if priority_score > 0.7 else "MEDIUM" if priority_score > 0.4 else "LOW"
                
                reasoning = f"Fallback: AI selected {widget.title} with {priority} priority based on importance ({widget.importance}) and frequency ({widget.frequency})"
                
                ai_output = DailyWidgetsAIOutput(
                    widget_id=widget.id,
                    priority=priority,
                    reasoning=reasoning,
                    result_json={
                        "priority": priority,
                        "priority_score": priority_score,
                        "importance": widget.importance,
                        "frequency": widget.frequency,
                        "category": widget.category,
                        "fallback_used": True
                    },
                    date=target_date,
                    ai_model_used="fallback",
                    ai_prompt_used=None,
                    ai_response_time=None,
                    confidence_score="0.50",  # Medium confidence for fallback logic
                    generation_type="fallback",
                    created_by=user_id
                )
                db.add(ai_output)
                ai_outputs.append(ai_output)
        
        db.commit()
        
        # Generate activity from plan
        await generate_activity_from_plan(target_date, user_id, db)
        
        return {
            "message": "Today's plan generated successfully",
            "date": target_date.isoformat(),
            "widgets_processed": len(widgets),
            "ai_outputs_created": len(ai_outputs)
        }
    except Exception as e:
        logger.error(f"Failed to generate today's plan for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate today's plan: {str(e)}"
        )

@router.post("/generate_web_summary_list")
async def generate_web_summary_list(
    target_date: Optional[date] = Query(None, description="Date for summary generation (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Internal AI API: Generate web summary list
    Responsible for generating WebSearchSummaryAIOutput
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        # Get websearch widgets
        websearch_widgets = db.query(DashboardWidgetDetails).filter(
            DashboardWidgetDetails.user_id == user_id,
            DashboardWidgetDetails.widget_type == "websearch",
            DashboardWidgetDetails.delete_flag == False
        ).all()
        
        # AI Logic: Perform web search and summarization for each widget
        ai_outputs = []
        for widget in websearch_widgets:
            try:
                # 1. Input Validation
                query = widget.title
                if not query or not query.strip():
                    logger.warning(f"Empty query for widget {widget.id}")
                    continue
                
                # 2. Perform Web Search
                search_response = perform_web_search(query)
                
                # 3. Parse and Format Results
                search_results = parse_search_results(search_response)
                
                if not search_results:# Fallback: Create basic output with no results
                    ai_output = WebSearchSummaryAIOutput(
                        widget_id=widget.id,
                        query=query,
                        result_json={
                            "summary": "No relevant information found for this query.",
                            "sources": [],
                            "search_successful": False,
                            "confidence_score": "0.10"
                        },
                        ai_model_used="fallback",
                        ai_prompt_used=None,
                        ai_response_time=None,
                        search_results_count="0",
                        summary_length="0",
                        sources_used=[],
                        generation_type="fallback",
                        created_by=user_id
                    )
                    db.add(ai_output)
                    ai_outputs.append(ai_output)
                    continue
                
                # 4. Summarization Preparation
                prompt = create_summarization_prompt(query, search_results)
                
                # 5. Call OpenAI for Summarization
                summary_result = await generate_summary_with_openai(prompt)
                summary = summary_result["summary"]
                
                # 6. Prepare sources for result
                sources = [{"title": result["title"], "url": result["url"]} for result in search_results]
                
                # 7. Create AI output
                ai_output = WebSearchSummaryAIOutput(
                    widget_id=widget.id,
                    query=query,
                    result_json={
                        "summary": summary,
                        "sources": sources,
                        "search_successful": True,
                        "results_count": len(search_results),
                        "query": query,
                        "confidence_score": summary_result["confidence_score"]
                    },
                    ai_model_used=summary_result["model_used"],
                    ai_prompt_used=prompt,
                    ai_response_time=summary_result["response_time"],
                    search_results_count=str(len(search_results)),
                    summary_length=str(len(summary)),
                    sources_used=sources,
                    generation_type="ai_generated",
                    created_by=user_id
                )
                db.add(ai_output)
                ai_outputs.append(ai_output)
                
            except Exception as e:
                logger.error(f"Failed to process widget {widget.id}: {e}")
                # Create fallback output
                fallback_summary = create_fallback_summary([])
                ai_output = WebSearchSummaryAIOutput(
                    widget_id=widget.id,
                    query=widget.title,
                    result_json={
                        "summary": fallback_summary,
                        "sources": [],
                        "search_successful": False,
                        "error": str(e),
                        "confidence_score": "0.15"
                    },
                    ai_model_used="fallback",
                    ai_prompt_used=None,
                    ai_response_time=None,
                    search_results_count="0",
                    summary_length=str(len(fallback_summary)),
                    sources_used=[],
                    generation_type="fallback",
                    created_by=user_id
                )
                db.add(ai_output)
                ai_outputs.append(ai_output)
        
        db.commit()
        
        return {
            "message": "Web summary list generated successfully",
            "date": target_date.isoformat(),
            "websearch_widgets_processed": len(websearch_widgets),
            "ai_outputs_created": len(ai_outputs)
        }
    except Exception as e:
        logger.error(f"Failed to generate web summary list for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate web summary list: {str(e)}"
        )

async def generate_activity_from_plan(target_date: date, user_id: str, db: Session):
    """
    Internal function: Generate activity from plan
    Reads the plan from DailyWidgetsAIOutput and creates activity tables
    """
    try:
        # Get AI outputs for the date
        ai_outputs = db.query(DailyWidgetsAIOutput).filter(
            DailyWidgetsAIOutput.date == target_date
        ).all()
        
        # Group widgets by type
        widgets_by_type = {}
        for ai_output in ai_outputs:
            widget = db.query(DashboardWidgetDetails).filter(
                DashboardWidgetDetails.id == ai_output.widget_id
            ).first()
            if widget:
                if widget.widget_type not in widgets_by_type:
                    widgets_by_type[widget.widget_type] = []
                widgets_by_type[widget.widget_type].append(widget.id)
        
        # Create daily widgets
        for widget_type, widget_ids in widgets_by_type.items():
            daily_widget = DailyWidget(
                widget_ids=widget_ids,
                widget_type=widget_type,
                priority="HIGH",  # TODO: Get from AI output
                reasoning=f"AI selected {len(widget_ids)} {widget_type} widgets",
                date=target_date,
                created_by=user_id
            )
            db.add(daily_widget)
            db.flush()  # Get the ID
            
            # Create activity entries based on widget type
            if widget_type == "todo":
                for widget_id in widget_ids:
                    todo_details = db.query(ToDoDetails).filter(
                        ToDoDetails.widget_id == widget_id
                    ).first()
                    if todo_details:
                        activity = ToDoItemActivity(
                            daily_widget_id=daily_widget.id,
                            widget_id=widget_id,
                            tododetails_id=todo_details.id,
                            status="pending",
                            progress=0,
                            created_by=user_id
                        )
                        db.add(activity)
            
            elif widget_type == "singleitemtracker":
                for widget_id in widget_ids:
                    tracker_details = db.query(SingleItemTrackerDetails).filter(
                        SingleItemTrackerDetails.widget_id == widget_id
                    ).first()
                    if tracker_details:
                        activity = SingleItemTrackerItemActivity(
                            daily_widget_id=daily_widget.id,
                            widget_id=widget_id,
                            singleitemtrackerdetails_id=tracker_details.id,
                            created_by=user_id
                        )
                        db.add(activity)
            
            elif widget_type == "alarm":
                for widget_id in widget_ids:
                    alarm_details = db.query(AlarmDetails).filter(
                        AlarmDetails.widget_id == widget_id
                    ).first()
                    if alarm_details:
                        activity = AlarmItemActivity(
                            daily_widget_id=daily_widget.id,
                            widget_id=widget_id,
                            alarmdetails_id=alarm_details.id,
                            created_by=user_id
                        )
                        db.add(activity)
            
            elif widget_type == "websearch":
                for widget_id in widget_ids:
                    websearch_details = db.query(WebSearchDetails).filter(
                        WebSearchDetails.widget_id == widget_id
                    ).first()
                    if websearch_details:
                        activity = WebSearchItemActivity(
                            daily_widget_id=daily_widget.id,
                            widget_id=widget_id,
                            websearchdetails_id=websearch_details.id,
                            status="pending",
                            created_by=user_id
                        )
                        db.add(activity)
        
        db.commit()
        logger.info(f"Generated activities for {target_date}")
        
    except Exception as e:
        logger.error(f"Failed to generate activities from plan: {e}")
        db.rollback()
        raise 