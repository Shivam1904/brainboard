"""
Single Item Tracker Service - Business logic for tracker operations
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from models.database import (
    SingleItemTrackerDetails, SingleItemTrackerItemActivity, DashboardWidgetDetails, DailyWidget
)

logger = logging.getLogger(__name__)

class SingleItemTrackerService:
    """Service for single item tracker operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tracker_details_and_activity(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get tracker details and activity for a specific widget"""
        try:
            # Get tracker details
            tracker_details = self.db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.widget_id == widget_id,
                SingleItemTrackerDetails.delete_flag == False
            ).first()
            
            if not tracker_details:
                return None
            
            # Get today's activity
            today_activity = self.db.query(SingleItemTrackerItemActivity).join(
                DailyWidget
            ).filter(
                DailyWidget.date == date.today(),
                DailyWidget.delete_flag == False,
                SingleItemTrackerItemActivity.widget_id == widget_id
            ).first()
            
            # If no activity exists for today, create one
            if not today_activity:
                # Get today's daily widget
                daily_widget = self.db.query(DailyWidget).filter(
                    DailyWidget.date == date.today(),
                    DailyWidget.delete_flag == False
                ).first()
                
                if daily_widget:
                    today_activity = SingleItemTrackerItemActivity(
                        daily_widget_id=daily_widget.id,
                        widget_id=widget_id,
                        singleitemtrackerdetails_id=tracker_details.id,
                        created_by="system"
                    )
                    self.db.add(today_activity)
                    self.db.commit()
                    self.db.refresh(today_activity)
            
            return {
                "tracker_details": {
                    "id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "created_at": tracker_details.created_at.isoformat(),
                    "updated_at": tracker_details.updated_at.isoformat()
                },
                "activity": {
                    "id": today_activity.id if today_activity else None,
                    "value": today_activity.value if today_activity else None,
                    "time_added": today_activity.time_added.isoformat() if today_activity and today_activity.time_added else None,
                    "created_at": today_activity.created_at.isoformat() if today_activity else None,
                    "updated_at": today_activity.updated_at.isoformat() if today_activity else None
                } if today_activity else None
            }
        except Exception as e:
            logger.error(f"Error getting tracker details and activity for widget {widget_id}: {e}")
            self.db.rollback()
            return None
    
    def update_activity(self, activity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update tracker activity"""
        try:
            logger.info(f"Attempting to update tracker activity with ID: {activity_id}")
            logger.info(f"Update data: {update_data}")
            
            # First, let's check if the activity exists
            activity = self.db.query(SingleItemTrackerItemActivity).filter(
                SingleItemTrackerItemActivity.id == activity_id
            ).first()
            
            if not activity:
                logger.error(f"Tracker activity with ID {activity_id} not found in database")
                # Let's also log all tracker activities to see what's available
                all_activities = self.db.query(SingleItemTrackerItemActivity).all()
                logger.info(f"All tracker activities in database: {[{'id': a.id, 'widget_id': a.widget_id, 'created_at': a.created_at} for a in all_activities]}")
                return None
            
            logger.info(f"Found tracker activity: {activity.id}, widget_id: {activity.widget_id}")
            
            # Update fields
            if "value" in update_data:
                activity.value = update_data["value"]
                logger.info(f"Updated value to: {update_data['value']}")
            if "time_added" in update_data:
                # Convert ISO string to datetime object
                if isinstance(update_data["time_added"], str):
                    activity.time_added = datetime.fromisoformat(update_data["time_added"].replace('Z', '+00:00'))
                else:
                    activity.time_added = update_data["time_added"]
                logger.info(f"Updated time_added to: {update_data['time_added']}")
            
            activity.updated_at = datetime.utcnow()
            activity.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            logger.info(f"Successfully updated tracker activity {activity_id}")
            
            return {
                "activity_id": activity.id,
                "value": activity.value,
                "time_added": activity.time_added.isoformat() if activity.time_added else None,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating tracker activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def create_tracker_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create tracker activity entry for today's dashboard"""
        try:
            # Get tracker details for the widget
            tracker_details = self.db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.widget_id == widget_id
            ).first()
            
            if not tracker_details:
                logger.warning(f"No tracker details found for widget {widget_id}")
                return None
            
            # Create new activity entry
            activity = SingleItemTrackerItemActivity(
                daily_widget_id=daily_widget_id,
                widget_id=widget_id,
                singleitemtrackerdetails_id=tracker_details.id,
                created_by=user_id
            )
            
            self.db.add(activity)
            self.db.flush()  # Get the ID
            
            logger.info(f"Created tracker activity {activity.id} for widget {widget_id}")
            
            return {
                "activity_id": activity.id,
                "value": activity.value,
                "time_added": activity.time_added
            }
            
        except Exception as e:
            logger.error(f"Error creating tracker activity for widget {widget_id}: {e}")
            return None

    def create_tracker_details(self, widget_id: str, title: str, value_type: str = "number", 
                              value_unit: str = "units", target_value: str = "0", user_id: str = None) -> Dict[str, Any]:
        """Create single item tracker details"""
        try:
            tracker_details = SingleItemTrackerDetails(
                widget_id=widget_id,
                title=title,
                value_type=value_type,
                value_unit=value_unit,
                target_value=target_value,
                created_by=user_id
            )
            self.db.add(tracker_details)
            self.db.flush()  # Get the ID
            
            return {
                "tracker_details_id": tracker_details.id,
                "widget_id": tracker_details.widget_id,
                "title": tracker_details.title,
                "value_type": tracker_details.value_type,
                "value_unit": tracker_details.value_unit,
                "target_value": tracker_details.target_value
            }
        except Exception as e:
            logger.error(f"Error creating tracker details: {e}")
            raise
    
    def get_tracker_details(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get tracker details for a specific widget"""
        try:
            tracker = self.db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.widget_id == widget_id,
                SingleItemTrackerDetails.delete_flag == False
            ).first()
            
            if not tracker:
                return None
            
            return {
                "id": tracker.id,
                "widget_id": tracker.widget_id,
                "title": tracker.title,
                "value_type": tracker.value_type,
                "value_unit": tracker.value_unit,
                "target_value": tracker.target_value,
                "created_at": tracker.created_at.isoformat(),
                "updated_at": tracker.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting tracker details for widget {widget_id}: {e}")
            return None
    
    def update_or_create_tracker_details(self, widget_id: str, title: str, value_type: str = "number",
                                        value_unit: str = "units", target_value: str = "0", user_id: str = None) -> Dict[str, Any]:
        """Update existing tracker details or create new ones if they don't exist"""
        try:
            # Check if tracker details exist
            tracker_details = self.db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.widget_id == widget_id
            ).first()
            
            if tracker_details:
                # Update existing tracker details
                tracker_details.title = title
                tracker_details.value_type = value_type
                tracker_details.value_unit = value_unit
                tracker_details.target_value = target_value
                tracker_details.updated_at = datetime.now(timezone.utc)
                
                return {
                    "tracker_details_id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "action": "updated"
                }
            else:
                # Create new tracker details
                return self.create_tracker_details(
                    widget_id=widget_id,
                    title=title,
                    value_type=value_type,
                    value_unit=value_unit,
                    target_value=target_value,
                    user_id=user_id
                )
        except Exception as e:
            logger.error(f"Error updating/creating tracker details for widget {widget_id}: {e}")
            raise
    
    def update_tracker_details(self, tracker_details_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update tracker details"""
        try:
            tracker = self.db.query(SingleItemTrackerDetails).filter(
                SingleItemTrackerDetails.id == tracker_details_id
            ).first()
            
            if not tracker:
                return None
            
            # Update fields
            if "title" in update_data:
                tracker.title = update_data["title"]
            if "value_type" in update_data:
                tracker.value_type = update_data["value_type"]
            if "value_unit" in update_data:
                tracker.value_unit = update_data["value_unit"]
            if "target_value" in update_data:
                tracker.target_value = update_data["target_value"]
            
            tracker.updated_at = datetime.utcnow()
            tracker.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            
            return {
                "id": tracker.id,
                "widget_id": tracker.widget_id,
                "title": tracker.title,
                "value_type": tracker.value_type,
                "value_unit": tracker.value_unit,
                "target_value": tracker.target_value,
                "updated_at": tracker.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating tracker details {tracker_details_id}: {e}")
            self.db.rollback()
            return None 