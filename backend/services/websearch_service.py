"""
WebSearch service for business logic.
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

from models.websearch_details import WebSearchDetails
from models.websearch_item_activity import WebSearchItemActivity
from models.websearch_summary_ai_output import WebSearchSummaryAIOutput
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
class WebSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary_and_activity(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get websearch summary and activity for a specific widget."""
        try:
            # Get websearch details
            stmt = select(WebSearchDetails).where(
                WebSearchDetails.widget_id == widget_id,
                WebSearchDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            websearch_details = result.scalars().first()

            if not websearch_details:
                return {"websearch_details": None, "activity": None}

            # Get today's activity
            today = date.today()
            stmt = select(WebSearchItemActivity).join(
                DailyWidget
            ).where(
                DailyWidget.date == today,
                DailyWidget.delete_flag == False,
                WebSearchItemActivity.widget_id == widget_id,
                WebSearchItemActivity.delete_flag == False
            )
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            # If no activity exists for today, create one
            if not activity:
                # Get today's daily widget
                stmt = select(DailyWidget).where(
                    DailyWidget.date == today,
                    DailyWidget.delete_flag == False
                )
                result = await self.db.execute(stmt)
                daily_widget = result.scalars().first()

                if daily_widget:
                    activity = WebSearchItemActivity(
                        daily_widget_id=daily_widget.id,
                        widget_id=widget_id,
                        websearchdetails_id=websearch_details.id,
                        status="pending",
                        created_by=user_id
                    )
                    self.db.add(activity)
                    await self.db.commit()
                    await self.db.refresh(activity)

            return {
                "websearch_details": {
                    "id": websearch_details.id,
                    "widget_id": websearch_details.widget_id,
                    "title": websearch_details.title,
                    "created_at": websearch_details.created_at,
                    "updated_at": websearch_details.updated_at
                },
                "activity": {
                    "id": activity.id if activity else None,
                    "daily_widget_id": activity.daily_widget_id if activity else None,
                    "widget_id": activity.widget_id if activity else None,
                    "websearchdetails_id": activity.websearchdetails_id if activity else None,
                    "status": activity.status if activity else None,
                    "reaction": activity.reaction if activity else None,
                    "summary": activity.summary if activity else None,
                    "source_json": activity.source_json if activity else None,
                    "created_at": activity.created_at if activity else None,
                    "updated_at": activity.updated_at if activity else None
                } if activity else None
            }
        except Exception as e:
            logger.error(f"Error getting websearch summary and activity for widget {widget_id}: {e}")
            raise

    async def update_activity(self, activity_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update websearch activity."""
        try:
            stmt = select(WebSearchItemActivity).where(
                WebSearchItemActivity.id == activity_id,
                WebSearchItemActivity.delete_flag == False
            )
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update fields
            if "status" in update_data:
                activity.status = update_data["status"]
            if "reaction" in update_data:
                activity.reaction = update_data["reaction"]
            if "summary" in update_data:
                activity.summary = update_data["summary"]
            if "source_json" in update_data:
                activity.source_json = update_data["source_json"]

            activity.updated_at = datetime.now()
            activity.updated_by = user_id

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "activity_id": activity.id,
                "status": activity.status,
                "reaction": activity.reaction,
                "summary": activity.summary,
                "source_json": activity.source_json,
                "updated_at": activity.updated_at
            }
        except Exception as e:
            logger.error(f"Error updating websearch activity {activity_id}: {e}")
            raise

    async def get_websearch_details(self, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get websearch details for a specific widget."""
        try:
            stmt = select(WebSearchDetails).where(
                WebSearchDetails.widget_id == widget_id,
                WebSearchDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            websearch = result.scalars().first()

            if not websearch:
                return None

            return {
                "id": websearch.id,
                "widget_id": websearch.widget_id,
                "title": websearch.title,
                "created_at": websearch.created_at,
                "updated_at": websearch.updated_at
            }
        except Exception as e:
            logger.error(f"Error getting websearch details for widget {widget_id}: {e}")
            raise

    async def update_websearch_details(self, websearch_details_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update websearch details."""
        try:
            stmt = select(WebSearchDetails).where(
                WebSearchDetails.id == websearch_details_id,
                WebSearchDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            websearch = result.scalars().first()

            if not websearch:
                return None

            # Update fields
            if "title" in update_data:
                websearch.title = update_data["title"]

            websearch.updated_at = datetime.now()
            websearch.updated_by = user_id

            await self.db.commit()
            await self.db.refresh(websearch)

            return {
                "id": websearch.id,
                "widget_id": websearch.widget_id,
                "title": websearch.title,
                "updated_at": websearch.updated_at
            }
        except Exception as e:
            logger.error(f"Error updating websearch details {websearch_details_id}: {e}")
            raise

    async def get_ai_summary(self, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get AI-generated summary for a specific widget."""
        try:
            # Get the most recent AI summary for this widget
            stmt = select(WebSearchSummaryAIOutput).where(
                WebSearchSummaryAIOutput.widget_id == widget_id,
                WebSearchSummaryAIOutput.delete_flag == False
            ).order_by(WebSearchSummaryAIOutput.created_at.desc())
            result = await self.db.execute(stmt)
            ai_summary = result.scalars().first()

            if not ai_summary:
                return None

            return {
                "ai_summary_id": ai_summary.id,
                "widget_id": ai_summary.widget_id,
                "query": ai_summary.query,
                "summary": ai_summary.result_json.get("summary", "") if ai_summary.result_json else "",
                "sources": ai_summary.result_json.get("sources", []) if ai_summary.result_json else [],
                "search_successful": ai_summary.result_json.get("search_successful", False) if ai_summary.result_json else False,
                "results_count": ai_summary.result_json.get("results_count", 0) if ai_summary.result_json else 0,
                "ai_model_used": ai_summary.ai_model_used,
                "generation_type": ai_summary.generation_type,
                "created_at": ai_summary.created_at,
                "updated_at": ai_summary.updated_at
            }
        except Exception as e:
            logger.error(f"Error getting AI summary for widget {widget_id}: {e}")
            raise

    async def create_websearch_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create websearch activity entry for today's dashboard."""
        try:
            # Get websearch details for the widget
            stmt = select(WebSearchDetails).where(
                WebSearchDetails.widget_id == widget_id,
                WebSearchDetails.delete_flag == False
            )
            result = await self.db.execute(stmt)
            websearch_details = result.scalars().first()

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
            await self.db.flush()  # Get the ID

            logger.info(f"Created websearch activity {activity.id} for widget {widget_id}")

            return {
                "activity_id": activity.id,
                "status": activity.status,
                "reaction": activity.reaction,
                "summary": activity.summary
            }

        except Exception as e:
            logger.error(f"Error creating websearch activity for widget {widget_id}: {e}")
            raise

    async def create_websearch_details(self, widget_id: str, title: str, user_id: str) -> Dict[str, Any]:
        """Create websearch details."""
        try:
            websearch_details = WebSearchDetails(
                widget_id=widget_id,
                title=title,
                created_by=user_id
            )
            self.db.add(websearch_details)
            await self.db.flush()  # Get the ID

            return {
                "websearch_details_id": websearch_details.id,
                "widget_id": websearch_details.widget_id,
                "title": websearch_details.title
            }
        except Exception as e:
            logger.error(f"Error creating websearch details: {e}")
            raise 