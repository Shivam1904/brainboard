"""
WebSearch Service - Business logic for websearch operations
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timezone
import logging

from models.database import (
    WebSearchDetails, WebSearchItemActivity, DashboardWidgetDetails, DailyWidget,
    WebSearchSummaryAIOutput
)

logger = logging.getLogger(__name__)

class WebSearchService:
    """Service for websearch operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary_and_activity(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get websearch summary and activity for a specific widget"""
        try:
            # Get websearch details
            websearch_details = self.db.query(WebSearchDetails).filter(
                WebSearchDetails.widget_id == widget_id,
                WebSearchDetails.delete_flag == False
            ).first()
            
            if not websearch_details:
                return None
            
            # Get today's activity
            today_activity = self.db.query(WebSearchItemActivity).join(
                DailyWidget
            ).filter(
                DailyWidget.date == date.today(),
                DailyWidget.delete_flag == False,
                WebSearchItemActivity.widget_id == widget_id
            ).first()
            
            # If no activity exists for today, create one
            if not today_activity:
                # Get today's daily widget
                daily_widget = self.db.query(DailyWidget).filter(
                    DailyWidget.date == date.today(),
                    DailyWidget.delete_flag == False
                ).first()
                
                if daily_widget:
                    today_activity = WebSearchItemActivity(
                        daily_widget_id=daily_widget.id,
                        widget_id=widget_id,
                        websearchdetails_id=websearch_details.id,
                        created_by="system"
                    )
                    self.db.add(today_activity)
                    self.db.commit()
                    self.db.refresh(today_activity)
            
            return {
                "websearch_details": {
                    "id": websearch_details.id,
                    "widget_id": websearch_details.widget_id,
                    "title": websearch_details.title,
                    "created_at": websearch_details.created_at.isoformat(),
                    "updated_at": websearch_details.updated_at.isoformat()
                },
                "activity": {
                    "id": today_activity.id if today_activity else None,
                    "status": today_activity.status if today_activity else None,
                    "reaction": today_activity.reaction if today_activity else None,
                    "summary": today_activity.summary if today_activity else None,
                    "source_json": today_activity.source_json if today_activity else None,
                    "created_at": today_activity.created_at.isoformat() if today_activity else None,
                    "updated_at": today_activity.updated_at.isoformat() if today_activity else None
                } if today_activity else None
            }
        except Exception as e:
            logger.error(f"Error getting websearch summary and activity for widget {widget_id}: {e}")
            self.db.rollback()
            return None
    
    def update_activity(self, activity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update websearch activity"""
        try:
            logger.info(f"Attempting to update websearch activity with ID: {activity_id}")
            logger.info(f"Update data: {update_data}")
            
            # First, let's check if the activity exists
            activity = self.db.query(WebSearchItemActivity).filter(
                WebSearchItemActivity.id == activity_id
            ).first()
            
            if not activity:
                logger.error(f"Websearch activity with ID {activity_id} not found in database")
                # Let's also log all websearch activities to see what's available
                all_activities = self.db.query(WebSearchItemActivity).all()
                logger.info(f"All websearch activities in database: {[{'id': a.id, 'widget_id': a.widget_id, 'created_at': a.created_at} for a in all_activities]}")
                return None
            
            logger.info(f"Found websearch activity: {activity.id}, widget_id: {activity.widget_id}")
            
            # Update fields
            if "status" in update_data:
                activity.status = update_data["status"]
                logger.info(f"Updated status to: {update_data['status']}")
            if "reaction" in update_data:
                activity.reaction = update_data["reaction"]
                logger.info(f"Updated reaction to: {update_data['reaction']}")
            if "summary" in update_data:
                activity.summary = update_data["summary"]
                logger.info(f"Updated summary to: {update_data['summary']}")
            if "source_json" in update_data:
                activity.source_json = update_data["source_json"]
                logger.info(f"Updated source_json")
            
            activity.updated_at = datetime.utcnow()
            activity.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            logger.info(f"Successfully updated websearch activity {activity_id}")
            
            return {
                "activity_id": activity.id,
                "status": activity.status,
                "reaction": activity.reaction,
                "summary": activity.summary,
                "source_json": activity.source_json,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating websearch activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def create_websearch_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create websearch activity entry for today's dashboard"""
        try:
            # Get websearch details for the widget
            websearch_details = self.db.query(WebSearchDetails).filter(
                WebSearchDetails.widget_id == widget_id
            ).first()
            
            if not websearch_details:
                logger.warning(f"No websearch details found for widget {widget_id}")
                return None
            
            # Create new activity entry
            activity = WebSearchItemActivity(
                daily_widget_id=daily_widget_id,
                widget_id=widget_id,
                websearchdetails_id=websearch_details.id,
                status="pending",
                created_by=user_id
            )
            
            self.db.add(activity)
            self.db.flush()  # Get the ID
            
            logger.info(f"Created websearch activity {activity.id} for widget {widget_id}")
            
            return {
                "activity_id": activity.id,
                "status": activity.status,
                "reaction": activity.reaction,
                "summary": activity.summary
            }
            
        except Exception as e:
            logger.error(f"Error creating websearch activity for widget {widget_id}: {e}")
            return None

    def create_websearch_details(self, widget_id: str, title: str, user_id: str = None) -> Dict[str, Any]:
        """Create websearch details"""
        try:
            websearch_details = WebSearchDetails(
                widget_id=widget_id,
                title=title,
                created_by=user_id
            )
            self.db.add(websearch_details)
            self.db.flush()  # Get the ID
            
            return {
                "websearch_details_id": websearch_details.id,
                "widget_id": websearch_details.widget_id,
                "title": websearch_details.title
            }
        except Exception as e:
            logger.error(f"Error creating websearch details: {e}")
            raise
    
    def get_websearch_details(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get websearch details for a specific widget"""
        try:
            websearch = self.db.query(WebSearchDetails).filter(
                WebSearchDetails.widget_id == widget_id,
                WebSearchDetails.delete_flag == False
            ).first()
            
            if not websearch:
                return None
            
            return {
                "id": websearch.id,
                "widget_id": websearch.widget_id,
                "title": websearch.title,
                "created_at": websearch.created_at.isoformat(),
                "updated_at": websearch.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting websearch details for widget {widget_id}: {e}")
            return None
    
    def update_or_create_websearch_details(self, widget_id: str, title: str, user_id: str = None) -> Dict[str, Any]:
        """Update existing websearch details or create new ones if they don't exist"""
        try:
            # Check if websearch details exist
            websearch_details = self.db.query(WebSearchDetails).filter(
                WebSearchDetails.widget_id == widget_id
            ).first()
            
            if websearch_details:
                # Update existing websearch details
                websearch_details.title = title
                websearch_details.updated_at = datetime.now(timezone.utc)
                
                return {
                    "websearch_details_id": websearch_details.id,
                    "widget_id": websearch_details.widget_id,
                    "title": websearch_details.title,
                    "action": "updated"
                }
            else:
                # Create new websearch details
                return self.create_websearch_details(
                    widget_id=widget_id,
                    title=title,
                    user_id=user_id
                )
        except Exception as e:
            logger.error(f"Error updating/creating websearch details for widget {widget_id}: {e}")
            raise
    
    def update_websearch_details(self, websearch_details_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update websearch details"""
        try:
            websearch = self.db.query(WebSearchDetails).filter(
                WebSearchDetails.id == websearch_details_id
            ).first()
            
            if not websearch:
                return None
            
            # Update fields
            if "title" in update_data:
                websearch.title = update_data["title"]
            
            websearch.updated_at = datetime.utcnow()
            websearch.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            
            return {
                "id": websearch.id,
                "widget_id": websearch.widget_id,
                "title": websearch.title,
                "updated_at": websearch.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating websearch details {websearch_details_id}: {e}")
            self.db.rollback()
            return None
    
    def get_ai_summary(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get AI-generated summary for a specific widget"""
        try:
            # Get the most recent AI summary for this widget
            ai_summary = self.db.query(WebSearchSummaryAIOutput).filter(
                WebSearchSummaryAIOutput.widget_id == widget_id
            ).order_by(WebSearchSummaryAIOutput.created_at.desc()).first()
            
            if not ai_summary:
                return None
            
            return {
                "ai_summary_id": ai_summary.id,
                "widget_id": ai_summary.widget_id,
                "query": ai_summary.query,
                "summary": ai_summary.result_json.get("summary", ""),
                "sources": ai_summary.result_json.get("sources", []),
                "search_successful": ai_summary.result_json.get("search_successful", False),
                "results_count": ai_summary.result_json.get("results_count", 0),
                "ai_model_used": ai_summary.ai_model_used,
                "generation_type": ai_summary.generation_type,
                "created_at": ai_summary.created_at.isoformat(),
                "updated_at": ai_summary.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI summary for widget {widget_id}: {e}")
            return None 