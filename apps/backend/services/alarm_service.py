"""
Alarm Service - Business logic for alarm operations
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timezone, timedelta
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
            
            # If no activity exists for today, create one
            if not today_activity:
                # Get today's daily widget
                daily_widget = self.db.query(DailyWidget).filter(
                    DailyWidget.date == date.today(),
                    DailyWidget.delete_flag == False
                ).first()
                
                if daily_widget:
                    today_activity = AlarmItemActivity(
                        daily_widget_id=daily_widget.id,
                        widget_id=widget_id,
                        alarmdetails_id=alarm_details.id,
                        created_by="system"
                    )
                    self.db.add(today_activity)
                    self.db.commit()
                    self.db.refresh(today_activity)
            
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
                    "snooze_until": today_activity.snooze_until.isoformat() if today_activity and today_activity.snooze_until else None,
                    "snooze_count": today_activity.snooze_count if today_activity else 0,
                    "created_at": today_activity.created_at.isoformat() if today_activity else None,
                    "updated_at": today_activity.updated_at.isoformat() if today_activity else None
                } if today_activity else None
            }
        except Exception as e:
            logger.error(f"Error getting alarm details and activity for widget {widget_id}: {e}")
            self.db.rollback()
            return None
    
    def should_alarm_trigger(self, alarm_details: Dict[str, Any], activity: Dict[str, Any]) -> bool:
        """Check if alarm should trigger based on current time and snooze status"""
        if not alarm_details or not activity:
            return False
        
        now = datetime.now()
        
        # If alarm was already started today, don't trigger again
        if activity.get("started_at"):
            return False
        
        # Check if currently snoozed
        if activity.get("snooze_until"):
            snooze_until = datetime.fromisoformat(activity["snooze_until"].replace('Z', '+00:00'))
            if now < snooze_until:
                return False
        
        # Check if any alarm time matches current time (within 1 minute)
        current_time_str = now.strftime("%H:%M")
        for alarm_time in alarm_details.get("alarm_times", []):
            if alarm_time == current_time_str:
                return True
        
        return False
    
    def snooze_alarm(self, activity_id: str, snooze_minutes: int = 2) -> Optional[Dict[str, Any]]:
        """Snooze alarm for specified minutes"""
        try:
            activity = self.db.query(AlarmItemActivity).filter(
                AlarmItemActivity.id == activity_id
            ).first()
            
            if not activity:
                return None
            
            now = datetime.now()
            snooze_until = now + timedelta(minutes=snooze_minutes)
            
            activity.snoozed_at = now
            activity.snooze_until = snooze_until
            activity.snooze_count += 1
            activity.updated_at = now
            activity.updated_by = "user"
            
            self.db.commit()
            
            return {
                "activity_id": activity.id,
                "snoozed_at": activity.snoozed_at.isoformat(),
                "snooze_until": activity.snooze_until.isoformat(),
                "snooze_count": activity.snooze_count,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error snoozing alarm activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def stop_alarm(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Stop alarm (mark as started)"""
        try:
            activity = self.db.query(AlarmItemActivity).filter(
                AlarmItemActivity.id == activity_id
            ).first()
            
            if not activity:
                return None
            
            now = datetime.now()
            activity.started_at = now
            activity.snooze_until = None  # Clear snooze
            activity.updated_at = now
            activity.updated_by = "user"
            
            self.db.commit()
            
            return {
                "activity_id": activity.id,
                "started_at": activity.started_at.isoformat(),
                "snooze_until": None,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error stopping alarm activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def update_activity(self, activity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update alarm activity"""
        try:
            logger.info(f"Attempting to update alarm activity with ID: {activity_id}")
            logger.info(f"Update data: {update_data}")
            
            # First, let's check if the activity exists
            activity = self.db.query(AlarmItemActivity).filter(
                AlarmItemActivity.id == activity_id
            ).first()
            
            if not activity:
                logger.error(f"Alarm activity with ID {activity_id} not found in database")
                # Let's also log all alarm activities to see what's available
                all_activities = self.db.query(AlarmItemActivity).all()
                logger.info(f"All alarm activities in database: {[{'id': a.id, 'widget_id': a.widget_id, 'created_at': a.created_at} for a in all_activities]}")
                return None
            
            logger.info(f"Found alarm activity: {activity.id}, widget_id: {activity.widget_id}")
            
            # Update fields
            if "started_at" in update_data:
                # Convert ISO string to datetime object
                if isinstance(update_data["started_at"], str):
                    activity.started_at = datetime.fromisoformat(update_data["started_at"].replace('Z', '+00:00'))
                else:
                    activity.started_at = update_data["started_at"]
                logger.info(f"Updated started_at to: {update_data['started_at']}")
            if "snoozed_at" in update_data:
                # Convert ISO string to datetime object
                if isinstance(update_data["snoozed_at"], str):
                    activity.snoozed_at = datetime.fromisoformat(update_data["snoozed_at"].replace('Z', '+00:00'))
                else:
                    activity.snoozed_at = update_data["snoozed_at"]
                logger.info(f"Updated snoozed_at to: {update_data['snoozed_at']}")
            
            activity.updated_at = datetime.utcnow()
            activity.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            logger.info(f"Successfully updated alarm activity {activity_id}")
            
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
    
    def create_alarm_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create alarm activity entry for today's dashboard"""
        try:
            # Get alarm details for the widget
            alarm_details = self.db.query(AlarmDetails).filter(
                AlarmDetails.widget_id == widget_id
            ).first()
            
            if not alarm_details:
                logger.warning(f"No alarm details found for widget {widget_id}")
                return None
            
            # Create new activity entry
            activity = AlarmItemActivity(
                daily_widget_id=daily_widget_id,
                widget_id=widget_id,
                alarmdetails_id=alarm_details.id,
                created_by=user_id
            )
            
            self.db.add(activity)
            self.db.flush()  # Get the ID
            
            logger.info(f"Created alarm activity {activity.id} for widget {widget_id}")
            
            return {
                "activity_id": activity.id,
                "started_at": activity.started_at,
                "snoozed_at": activity.snoozed_at
            }
            
        except Exception as e:
            logger.error(f"Error creating alarm activity for widget {widget_id}: {e}")
            return None

    def create_alarm_details(self, widget_id: str, title: str, alarm_times: list = None, user_id: str = None) -> Dict[str, Any]:
        """Create alarm details"""
        try:
            # Use provided alarm times or default to 09:00
            if alarm_times is None:
                alarm_times = ["09:00"]
            
            alarm_details = AlarmDetails(
                widget_id=widget_id,
                title=title,
                alarm_times=alarm_times,
                created_by=user_id
            )
            self.db.add(alarm_details)
            self.db.flush()  # Get the ID
            
            return {
                "alarm_details_id": alarm_details.id,
                "widget_id": alarm_details.widget_id,
                "title": alarm_details.title,
                "alarm_times": alarm_details.alarm_times
            }
        except Exception as e:
            logger.error(f"Error creating alarm details: {e}")
            raise
    
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
    
    def update_or_create_alarm_details(self, widget_id: str, title: str, alarm_times: list = None, user_id: str = None) -> Dict[str, Any]:
        """Update existing alarm details or create new ones if they don't exist"""
        try:
            # Use provided alarm times or default to 09:00
            if alarm_times is None:
                alarm_times = ["09:00"]
            
            # Check if alarm details exist
            alarm_details = self.db.query(AlarmDetails).filter(
                AlarmDetails.widget_id == widget_id
            ).first()
            
            if alarm_details:
                # Update existing alarm details
                alarm_details.title = title
                alarm_details.alarm_times = alarm_times
                alarm_details.updated_at = datetime.now(timezone.utc)
                
                return {
                    "alarm_details_id": alarm_details.id,
                    "widget_id": alarm_details.widget_id,
                    "title": alarm_details.title,
                    "alarm_times": alarm_details.alarm_times,
                    "action": "updated"
                }
            else:
                # Create new alarm details
                return self.create_alarm_details(
                    widget_id=widget_id,
                    title=title,
                    alarm_times=alarm_times,
                    user_id=user_id
                )
        except Exception as e:
            logger.error(f"Error updating/creating alarm details for widget {widget_id}: {e}")
            raise
    
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