"""
SingleItemTracker service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

from models.single_item_tracker_details import SingleItemTrackerDetails
from models.single_item_tracker_item_activity import SingleItemTrackerItemActivity
from models.daily_widget import DailyWidget

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default values
DEFAULT_SYSTEM_USER = "system"
DEFAULT_USER = "user_001"

# ============================================================================
# SERVICE CLASS
# ============================================================================
class SingleItemTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tracker_details_and_activity(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get tracker details and activity for a widget."""
        try:
            # Get tracker details
            stmt = select(SingleItemTrackerDetails).where(
                SingleItemTrackerDetails.widget_id == widget_id,
                SingleItemTrackerDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            tracker_details = result.scalars().first()

            if not tracker_details:
                return {"tracker_details": None, "activity": None}

            # Get today's activity
            today = date.today()
            stmt = select(SingleItemTrackerItemActivity).where(
                SingleItemTrackerItemActivity.singleitemtrackerdetails_id == tracker_details.id,
                SingleItemTrackerItemActivity.delete_flag == False
            )
            result = await self.db.execute(stmt)
            activities = result.scalars().all()
            
            # Find today's activity manually
            activity = None
            for act in activities:
                if act.created_at and act.created_at.date() == today:
                    activity = act
                    break

            # If no activity exists for today, create one
            if not activity:
                # Get today's daily widget
                stmt = select(DailyWidget).where(
                    DailyWidget.delete_flag == False
                )
                result = await self.db.execute(stmt)
                daily_widgets = result.scalars().all()
                
                # Find today's daily widget
                daily_widget = None
                for dw in daily_widgets:
                    if dw.date == today:
                        daily_widget = dw
                        break

                if daily_widget:
                    activity = SingleItemTrackerItemActivity(
                        daily_widget_id=daily_widget.id,
                        widget_id=widget_id,
                        singleitemtrackerdetails_id=tracker_details.id,
                        created_by=user_id
                    )
                    self.db.add(activity)
                    await self.db.commit()
                    await self.db.refresh(activity)

            return {
                "tracker_details": {
                    "id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "created_at": tracker_details.created_at,
                    "updated_at": tracker_details.updated_at
                },
                "activity": {
                    "id": activity.id if activity else None,
                    "widget_id": activity.widget_id if activity else None,
                    "singleitemtrackerdetails_id": activity.singleitemtrackerdetails_id if activity else None,
                    "value": activity.value if activity else None,
                    "time_added": activity.time_added if activity else None,
                    "created_at": activity.created_at if activity else None,
                    "updated_at": activity.updated_at if activity else None
                } if activity else None
            }
        except Exception as e:
            logger.error(f"Error getting tracker details and activity: {e}")
            raise

    async def update_activity(self, activity_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update tracker activity."""
        try:
            stmt = select(SingleItemTrackerItemActivity).where(
                SingleItemTrackerItemActivity.id == activity_id
            )
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update fields if provided
            if "value" in update_data:
                activity.value = update_data["value"]
            if "time_added" in update_data:
                activity.time_added = update_data["time_added"]

            activity.updated_by = user_id
            activity.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": "Activity updated successfully",
                "activity": {
                    "id": activity.id,
                    "widget_id": activity.widget_id,
                    "singleitemtrackerdetails_id": activity.singleitemtrackerdetails_id,
                    "value": activity.value,
                    "time_added": activity.time_added,
                    "created_at": activity.created_at,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
            raise

    async def get_tracker_details(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get tracker details for a widget."""
        try:
            stmt = select(SingleItemTrackerDetails).where(
                SingleItemTrackerDetails.widget_id == widget_id,
                SingleItemTrackerDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            tracker_details = result.scalars().first()

            if not tracker_details:
                return {"tracker_details": None}

            return {
                "tracker_details": {
                    "id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "created_at": tracker_details.created_at,
                    "updated_at": tracker_details.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error getting tracker details: {e}")
            raise

    async def create_tracker_details(self, widget_id: str, title: str, value_type: str = "number", 
                                   value_unit: str = None, target_value: str = None, user_id: str = None) -> Dict[str, Any]:
        """Create tracker details."""
        try:
            tracker_details = SingleItemTrackerDetails(
                widget_id=widget_id,
                title=title,
                value_type=value_type,
                value_unit=value_unit,
                target_value=target_value,
                created_by=user_id or DEFAULT_USER
            )
            
            self.db.add(tracker_details)
            await self.db.commit()
            await self.db.refresh(tracker_details)

            return {
                "success": True,
                "message": "Tracker details created successfully",
                "tracker_details": {
                    "id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "created_at": tracker_details.created_at,
                    "updated_at": tracker_details.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error creating tracker details: {e}")
            raise

    async def update_or_create_tracker_details(self, widget_id: str, title: str, value_type: str = "number",
                                             value_unit: str = None, target_value: str = None, user_id: str = None) -> Dict[str, Any]:
        """Update existing tracker details or create new ones if they don't exist."""
        try:
            # Check if tracker details exist
            stmt = select(SingleItemTrackerDetails).where(
                SingleItemTrackerDetails.widget_id == widget_id,
                SingleItemTrackerDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            tracker_details = result.scalars().first()

            if tracker_details:
                # Update existing tracker details
                tracker_details.title = title
                tracker_details.value_type = value_type
                tracker_details.value_unit = value_unit
                tracker_details.target_value = target_value
                tracker_details.updated_at = datetime.now()
                tracker_details.updated_by = user_id or DEFAULT_USER

                await self.db.commit()
                await self.db.refresh(tracker_details)

                return {
                    "success": True,
                    "message": "Tracker details updated successfully",
                    "tracker_details": {
                        "id": tracker_details.id,
                        "widget_id": tracker_details.widget_id,
                        "title": tracker_details.title,
                        "value_type": tracker_details.value_type,
                        "value_unit": tracker_details.value_unit,
                        "target_value": tracker_details.target_value,
                        "created_at": tracker_details.created_at,
                        "updated_at": tracker_details.updated_at
                    },
                    "action": "updated"
                }
            else:
                # Create new tracker details
                return await self.create_tracker_details(
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

    async def update_tracker_details(self, tracker_details_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update tracker details."""
        try:
            stmt = select(SingleItemTrackerDetails).where(
                SingleItemTrackerDetails.id == tracker_details_id
            )
            result = await self.db.execute(stmt)
            tracker_details = result.scalars().first()

            if not tracker_details:
                return {"success": False, "message": "Tracker details not found"}

            # Update fields if provided
            if "title" in update_data:
                tracker_details.title = update_data["title"]
            if "value_type" in update_data:
                tracker_details.value_type = update_data["value_type"]
            if "value_unit" in update_data:
                tracker_details.value_unit = update_data["value_unit"]
            if "target_value" in update_data:
                tracker_details.target_value = update_data["target_value"]

            tracker_details.updated_by = user_id
            tracker_details.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(tracker_details)

            return {
                "success": True,
                "message": "Tracker details updated successfully",
                "tracker_details": {
                    "id": tracker_details.id,
                    "widget_id": tracker_details.widget_id,
                    "title": tracker_details.title,
                    "value_type": tracker_details.value_type,
                    "value_unit": tracker_details.value_unit,
                    "target_value": tracker_details.target_value,
                    "created_at": tracker_details.created_at,
                    "updated_at": tracker_details.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating tracker details: {e}")
            raise

    async def create_tracker_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create tracker activity for today."""
        try:
            # Get tracker details
            stmt = select(SingleItemTrackerDetails).where(
                SingleItemTrackerDetails.widget_id == widget_id
            )
            result = await self.db.execute(stmt)
            tracker_details = result.scalars().first()

            if not tracker_details:
                return None

            # Check if activity already exists for today
            today = date.today()
            stmt = select(SingleItemTrackerItemActivity).where(
                SingleItemTrackerItemActivity.singleitemtrackerdetails_id == tracker_details.id,
                SingleItemTrackerItemActivity.created_at >= today
            )
            result = await self.db.execute(stmt)
            existing_activity = result.scalars().first()

            if existing_activity:
                return {
                    "id": existing_activity.id,
                    "widget_id": existing_activity.widget_id,
                    "singleitemtrackerdetails_id": existing_activity.singleitemtrackerdetails_id,
                    "value": existing_activity.value,
                    "time_added": existing_activity.time_added,
                    "created_at": existing_activity.created_at,
                    "updated_at": existing_activity.updated_at
                }

            # Create new activity
            activity = SingleItemTrackerItemActivity(
                daily_widget_id=daily_widget_id,
                widget_id=widget_id,
                singleitemtrackerdetails_id=tracker_details.id,
                created_by=user_id
            )

            self.db.add(activity)
            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "id": activity.id,
                "widget_id": activity.widget_id,
                "singleitemtrackerdetails_id": activity.singleitemtrackerdetails_id,
                "value": activity.value,
                "time_added": activity.time_added,
                "created_at": activity.created_at,
                "updated_at": activity.updated_at
            }
        except Exception as e:
            logger.error(f"Error creating tracker activity for today: {e}")
            raise

    async def get_user_trackers(self, user_id: str) -> Dict[str, Any]:
        """Get all trackers for a user."""
        try:
            # Get all widgets for the user that are SingleItemTracker type
            stmt = select(SingleItemTrackerDetails).join(
                SingleItemTrackerDetails.dashboard_widget
            ).where(
                SingleItemTrackerDetails.dashboard_widget.has(user_id=user_id)
            )
            result = await self.db.execute(stmt)
            trackers = result.scalars().all()

            return {
                "trackers": [
                    {
                        "id": tracker.id,
                        "widget_id": tracker.widget_id,
                        "title": tracker.title,
                        "value_type": tracker.value_type,
                        "value_unit": tracker.value_unit,
                        "target_value": tracker.target_value,
                        "created_at": tracker.created_at,
                        "updated_at": tracker.updated_at
                    }
                    for tracker in trackers
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user trackers: {e}")
            raise 