"""
Daily Plan Service
Handles generation of daily plans, including permanent widgets and AI-selected widgets
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date
import logging

from models.database import (
    DashboardWidgetDetails, DailyWidget, DailyWidgetsAIOutput,
    ToDoItemActivity, SingleItemTrackerItemActivity, AlarmItemActivity,
    WebSearchItemActivity, ToDoDetails, SingleItemTrackerDetails,
    AlarmDetails, WebSearchDetails
)

logger = logging.getLogger(__name__)

class DailyPlanService:
    """Service for generating daily plans"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_daily_plan(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Generate daily plan for a user on a specific date
        - Permanent widgets go directly to DailyWidgets
        - Non-permanent widgets are processed by AI service
        """
        try:
            # Get all user widgets
            widgets = self.db.query(DashboardWidgetDetails).filter(
                DashboardWidgetDetails.user_id == user_id,
                DashboardWidgetDetails.delete_flag == False
            ).all()
            
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
            self.db.rollback()
            raise
    
    async def _process_permanent_widgets(
        self, 
        permanent_widgets: List[DashboardWidgetDetails], 
        target_date: date, 
        user_id: str
    ) -> int:
        """
        Process permanent widgets - add them directly to DailyWidgets table
        """
        widgets_added = 0
        
        # Group permanent widgets by type
        widgets_by_type = {}
        for widget in permanent_widgets:
            if widget.widget_type not in widgets_by_type:
                widgets_by_type[widget.widget_type] = []
            widgets_by_type[widget.widget_type].append(widget.id)
        
        # Create daily widgets for permanent widgets
        for widget_type, widget_ids in widgets_by_type.items():
            daily_widget = DailyWidget(
                widget_ids=widget_ids,
                widget_type=widget_type,
                priority="HIGH",  # Permanent widgets are always high priority
                reasoning=f"Permanent widget automatically included: {len(widget_ids)} {widget_type} widgets",
                date=target_date,
                created_by=user_id
            )
            self.db.add(daily_widget)
            self.db.flush()  # Get the ID
            
            # Create activity entries for permanent widgets
            await self._create_activity_entries(daily_widget.id, widget_ids, widget_type, user_id)
            widgets_added += len(widget_ids)
        
        self.db.commit()
        logger.info(f"Added {widgets_added} permanent widgets to daily plan")
        return widgets_added
    
    async def _process_ai_widgets(
        self, 
        regular_widgets: List[DashboardWidgetDetails], 
        target_date: date, 
        user_id: str
    ) -> int:
        """
        Process regular widgets through AI service
        This calls the existing AI service to generate AI outputs and then creates activities
        """
        try:
            # Import here to avoid circular imports
            from routers.ai import generate_daily_plan_with_llm, generate_fallback_daily_plan
            
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
                ai_result = await generate_daily_plan_with_llm(widget_context, target_date)
                ai_plan = ai_result["plan"]
            except Exception as e:
                logger.error(f"AI plan generation failed, using fallback: {e}")
                ai_plan = generate_fallback_daily_plan(widget_context)
            
            # Process AI plan and create outputs
            ai_outputs = []
            for plan_item in ai_plan:
                widget_id = plan_item.get("widget_id")
                priority = plan_item.get("priority", "MEDIUM")
                reasoning = plan_item.get("reasoning", "AI selected this widget for today")
                selected = plan_item.get("selected", False)
                
                # Find the corresponding widget
                widget = next((w for w in regular_widgets if w.id == widget_id), None)
                if not widget or not selected:
                    continue
                
                # Create AI output
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
                    ai_model_used=ai_result.get("model_used", "fallback"),
                    ai_prompt_used=ai_result.get("prompt_used"),
                    ai_response_time=ai_result.get("response_time"),
                    confidence_score=ai_result.get("confidence_score", "0.50"),
                    generation_type="ai_generated",
                    created_by=user_id
                )
                self.db.add(ai_output)
                ai_outputs.append(ai_output)
            
            self.db.commit()
            
            # Generate activities from AI outputs
            await self._generate_activity_from_ai_outputs(target_date, user_id)
            
            return len(ai_outputs)
            
        except Exception as e:
            logger.error(f"Failed to process AI widgets: {e}")
            self.db.rollback()
            raise
    
    async def _create_activity_entries(
        self, 
        daily_widget_id: str, 
        widget_ids: List[str], 
        widget_type: str, 
        user_id: str
    ):
        """
        Create activity entries for widgets
        """
        for widget_id in widget_ids:
            if widget_type in ["todo-habit", "todo-task", "todo-event"]:
                todo_details = self.db.query(ToDoDetails).filter(
                    ToDoDetails.widget_id == widget_id
                ).first()
                if todo_details:
                    activity = ToDoItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        tododetails_id=todo_details.id,
                        status="pending",
                        progress=0,
                        created_by=user_id
                    )
                    self.db.add(activity)
            
            elif widget_type == "singleitemtracker":
                tracker_details = self.db.query(SingleItemTrackerDetails).filter(
                    SingleItemTrackerDetails.widget_id == widget_id
                ).first()
                if tracker_details:
                    activity = SingleItemTrackerItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        singleitemtrackerdetails_id=tracker_details.id,
                        created_by=user_id
                    )
                    self.db.add(activity)
            
            elif widget_type == "alarm":
                alarm_details = self.db.query(AlarmDetails).filter(
                    AlarmDetails.widget_id == widget_id
                ).first()
                if alarm_details:
                    activity = AlarmItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        alarmdetails_id=alarm_details.id,
                        created_by=user_id
                    )
                    self.db.add(activity)
            
            elif widget_type == "websearch":
                websearch_details = self.db.query(WebSearchDetails).filter(
                    WebSearchDetails.widget_id == widget_id
                ).first()
                if websearch_details:
                    activity = WebSearchItemActivity(
                        daily_widget_id=daily_widget_id,
                        widget_id=widget_id,
                        websearchdetails_id=websearch_details.id,
                        status="pending",
                        created_by=user_id
                    )
                    self.db.add(activity)
    
    async def _generate_activity_from_ai_outputs(self, target_date: date, user_id: str):
        """
        Generate activities from AI outputs (existing logic from ai.py)
        """
        try:
            # Get AI outputs for the date
            ai_outputs = self.db.query(DailyWidgetsAIOutput).filter(
                DailyWidgetsAIOutput.date == target_date
            ).all()
            
            # Group widgets by type
            widgets_by_type = {}
            for ai_output in ai_outputs:
                widget = self.db.query(DashboardWidgetDetails).filter(
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
                self.db.add(daily_widget)
                self.db.flush()  # Get the ID
                
                # Create activity entries
                await self._create_activity_entries(daily_widget.id, widget_ids, widget_type, user_id)
            
            self.db.commit()
            logger.info(f"Generated activities from AI outputs for {target_date}")
            
        except Exception as e:
            logger.error(f"Failed to generate activities from AI outputs: {e}")
            self.db.rollback()
            raise 