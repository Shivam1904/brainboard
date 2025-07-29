"""
Alarm Service - Business logic for alarm operations
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from models.database import (
    AlarmDetails, AlarmItemActivity, DashboardWidgetDetails, DailyWidget
)

logger = logging.getLogger(__name__)

class AlarmService:
    """Service for alarm operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_alarm_details_and_activity(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get alarm details and activity for a specific widget"""
        try:
            # Get alarm details
            alarm_details = self.db.query(AlarmDetails).filter(
                AlarmDetails.widget_id == widget_id,
                AlarmDetails.delete_flag == False
            ).first()
            
            if not alarm_details:
                return None
            
            # Get today's activity
            today_activity = self.db.query(AlarmItemActivity).join(
                DailyWidget
            ).filter(
                DailyWidget.date == date.today(),
                DailyWidget.delete_flag == False,
                AlarmItemActivity.widget_id == widget_id
            ).first()
            
            return {
                "alarm_details": {
                    "id": alarm_details.id,
                    "widget_id": alarm_details.widget_id,
                    "title": alarm_details.title,
                    "description": alarm_details.description,
                    "alarm_times": alarm_details.alarm_times,
                    "target_value": alarm_details.target_value,
                    "is_snoozable": alarm_details.is_snoozable,
                    "created_at": alarm_details.created_at.isoformat(),
                    "updated_at": alarm_details.updated_at.isoformat()
                },
                "activity": {
                    "id": today_activity.id if today_activity else None,
                    "started_at": today_activity.started_at.isoformat() if today_activity and today_activity.started_at else None,
                    "snoozed_at": today_activity.snoozed_at.isoformat() if today_activity and today_activity.snoozed_at else None,
                    "created_at": today_activity.created_at.isoformat() if today_activity else None,
                    "updated_at": today_activity.updated_at.isoformat() if today_activity else None
                } if today_activity else None
            }
        except Exception as e:
            logger.error(f"Error getting alarm details and activity for widget {widget_id}: {e}")
            return None
    
    def update_activity(self, activity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update alarm activity"""
        try:
            activity = self.db.query(AlarmItemActivity).filter(
                AlarmItemActivity.id == activity_id
            ).first()
            
            if not activity:
                return None
            
            # Update fields
            if "started_at" in update_data:
                activity.started_at = update_data["started_at"]
            if "snoozed_at" in update_data:
                activity.snoozed_at = update_data["snoozed_at"]
            
            activity.updated_at = datetime.utcnow()
            activity.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            
            return {
                "activity_id": activity.id,
                "started_at": activity.started_at.isoformat() if activity.started_at else None,
                "snoozed_at": activity.snoozed_at.isoformat() if activity.snoozed_at else None,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating alarm activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def get_alarm_details(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get alarm details for a specific widget"""
        try:
            alarm = self.db.query(AlarmDetails).filter(
                AlarmDetails.widget_id == widget_id,
                AlarmDetails.delete_flag == False
            ).first()
            
            if not alarm:
                return None
            
            return {
                "id": alarm.id,
                "widget_id": alarm.widget_id,
                "title": alarm.title,
                "description": alarm.description,
                "alarm_times": alarm.alarm_times,
                "target_value": alarm.target_value,
                "is_snoozable": alarm.is_snoozable,
                "created_at": alarm.created_at.isoformat(),
                "updated_at": alarm.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting alarm details for widget {widget_id}: {e}")
            return None
    
    def update_alarm_details(self, alarm_details_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update alarm details"""
        try:
            alarm = self.db.query(AlarmDetails).filter(
                AlarmDetails.id == alarm_details_id
            ).first()
            
            if not alarm:
                return None
            
            # Update fields
            if "title" in update_data:
                alarm.title = update_data["title"]
            if "description" in update_data:
                alarm.description = update_data["description"]
            if "alarm_times" in update_data:
                alarm.alarm_times = update_data["alarm_times"]
            if "target_value" in update_data:
                alarm.target_value = update_data["target_value"]
            if "is_snoozable" in update_data:
                alarm.is_snoozable = update_data["is_snoozable"]
            
            alarm.updated_at = datetime.utcnow()
            alarm.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            
            return {
                "id": alarm.id,
                "widget_id": alarm.widget_id,
                "title": alarm.title,
                "description": alarm.description,
                "alarm_times": alarm.alarm_times,
                "target_value": alarm.target_value,
                "is_snoozable": alarm.is_snoozable,
                "updated_at": alarm.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating alarm details {alarm_details_id}: {e}")
            self.db.rollback()
            return None 