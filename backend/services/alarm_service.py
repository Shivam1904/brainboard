"""
Alarm service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from models.alarm_details import AlarmDetails
from models.alarm_item_activity import AlarmItemActivity

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default values
DEFAULT_SNOOZE_MINUTES = 5
DEFAULT_SYSTEM_USER = "system"
DEFAULT_USER = "user_001"
TIME_FORMAT = "%H:%M"

# ============================================================================
# SERVICE CLASS
# ============================================================================
class AlarmService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_alarm_details_and_activity(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get alarm details and activity for a widget."""
        try:
            # Get alarm details
            stmt = select(AlarmDetails).where(
                AlarmDetails.widget_id == widget_id
            )
            result = await self.db.execute(stmt)
            alarm_details = result.scalars().first()

            if not alarm_details:
                return {"alarm_details": None, "activities": []}

            # Get today's activities
            today = datetime.now().date()
            stmt = select(AlarmItemActivity).where(
                AlarmItemActivity.alarmdetails_id == alarm_details.id,
                AlarmItemActivity.created_at >= today
            )
            result = await self.db.execute(stmt)
            activities = result.scalars().all()

            return {
                "alarm_details": {
                    "id": alarm_details.id,
                    "widget_id": alarm_details.widget_id,
                    "alarm_times": alarm_details.alarm_times,
                    "is_snoozable": alarm_details.is_snoozable,
                    "target_value": alarm_details.target_value,
                    "created_at": alarm_details.created_at,
                    "updated_at": alarm_details.updated_at
                },
                "activities": [
                    {
                        "id": activity.id,
                        "widget_id": activity.widget_id,
                        "alarmdetails_id": activity.alarmdetails_id,
                        "started_at": activity.started_at,
                        "snoozed_at": activity.snoozed_at,
                        "snooze_until": activity.snooze_until,
                        "snooze_count": activity.snooze_count,
                        "created_at": activity.created_at,
                        "updated_at": activity.updated_at
                    }
                    for activity in activities
                ]
            }
        except Exception as e:
            logger.error(f"Error getting alarm details and activity: {e}")
            raise

    async def snooze_alarm(self, activity_id: str, user_id: str, snooze_minutes: int) -> Dict[str, Any]:
        """Snooze an alarm activity."""
        try:
            stmt = select(AlarmItemActivity).where(AlarmItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update activity
            activity.snooze_count += 1
            activity.snoozed_at = datetime.now()
            activity.snooze_until = datetime.now() + timedelta(minutes=snooze_minutes)
            activity.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": f"Alarm snoozed for {snooze_minutes} minutes",
                "activity": {
                    "id": activity.id,
                    "snooze_count": activity.snooze_count,
                    "snoozed_at": activity.snoozed_at,
                    "snooze_until": activity.snooze_until,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error snoozing alarm: {e}")
            raise

    async def stop_alarm(self, activity_id: str, user_id: str) -> Dict[str, Any]:
        """Stop an alarm activity."""
        try:
            stmt = select(AlarmItemActivity).where(AlarmItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update activity
            activity.started_at = datetime.now()
            activity.snooze_until = None  # Clear snooze
            activity.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": "Alarm stopped",
                "activity": {
                    "id": activity.id,
                    "started_at": activity.started_at,
                    "snooze_until": activity.snooze_until,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error stopping alarm: {e}")
            raise

    async def update_activity(self, activity_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an alarm activity."""
        try:
            stmt = select(AlarmItemActivity).where(AlarmItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update fields
            for key, value in update_data.items():
                if hasattr(activity, key):
                    setattr(activity, key, value)

            activity.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": "Activity updated",
                "activity": {
                    "id": activity.id,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
            raise

    async def get_alarm_details(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get alarm details for a widget."""
        try:
            stmt = select(AlarmDetails).where(
                AlarmDetails.widget_id == widget_id
            )
            result = await self.db.execute(stmt)
            alarm_details = result.scalars().first()

            if not alarm_details:
                return None

            return {
                "id": alarm_details.id,
                "widget_id": alarm_details.widget_id,
                "alarm_times": alarm_details.alarm_times,
                "is_snoozable": alarm_details.is_snoozable,
                "target_value": alarm_details.target_value,
                "created_at": alarm_details.created_at,
                "updated_at": alarm_details.updated_at
            }
        except Exception as e:
            logger.error(f"Error getting alarm details: {e}")
            raise

    async def update_alarm_details(self, alarm_details_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update alarm details."""
        try:
            stmt = select(AlarmDetails).where(AlarmDetails.id == alarm_details_id)
            result = await self.db.execute(stmt)
            alarm_details = result.scalars().first()

            if not alarm_details:
                return {"success": False, "message": "Alarm details not found"}

            # Update fields
            for key, value in update_data.items():
                if hasattr(alarm_details, key):
                    setattr(alarm_details, key, value)

            alarm_details.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(alarm_details)

            return {
                "success": True,
                "message": "Alarm details updated",
                "alarm_details": {
                    "id": alarm_details.id,
                    "alarm_times": alarm_details.alarm_times,
                    "is_snoozable": alarm_details.is_snoozable,
                    "target_value": alarm_details.target_value,
                    "updated_at": alarm_details.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating alarm details: {e}")
            raise 