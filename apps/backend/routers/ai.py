"""
AI Router - Internal AI APIs
Handles AI-generated daily plans and web summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date, datetime
import logging

from core.database import get_db
from models.database import (
    User, DashboardWidgetDetails, DailyWidget, DailyWidgetsAIOutput,
    WebSearchSummaryAIOutput, ToDoItemActivity, SingleItemTrackerItemActivity,
    AlarmItemActivity, WebSearchItemActivity
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])

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
        
        # TODO: Implement AI logic here
        # For now, create basic AI output entries
        ai_outputs = []
        for widget in widgets:
            ai_output = DailyWidgetsAIOutput(
                widget_id=widget.id,
                priority="HIGH" if widget.importance > 0.7 else "LOW",
                reasoning=f"AI selected {widget.title} based on importance {widget.importance}",
                result_json={"priority": "HIGH" if widget.importance > 0.7 else "LOW"},
                date=target_date,
                ai_model_used="gpt-3.5-turbo",
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
        
        # TODO: Implement AI logic here
        # For now, create basic AI output entries
        ai_outputs = []
        for widget in websearch_widgets:
            ai_output = WebSearchSummaryAIOutput(
                widget_id=widget.id,
                query=widget.title,
                result_json={"summary": f"AI summary for {widget.title}"},
                ai_model_used="gpt-3.5-turbo",
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