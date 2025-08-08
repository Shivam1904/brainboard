"""
Tracker routes for calendar-linked activity queries.
"""

# =============================================================================
# IMPORTS
# =============================================================================
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import date

from db.dependency import get_db_session_dependency
from services.daily_widget_service import DailyWidgetService
from utils.errors import raise_database_error

# =============================================================================
# ROUTER
# =============================================================================
router = APIRouter()


@router.get("/getWidgetActivityForCalendar")
async def get_widget_activity_for_calendar(
    calendar_id: str = Query(..., description="Calendar widget_id to filter on (matches widget_config.selected_calendar)"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD) inclusive"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD) inclusive"),
    db: AsyncSession = Depends(get_db_session_dependency)
) -> List[Dict[str, Any]]:
    """Get daily widgets joined with dashboard widgets for a given calendar over a period.

    Filters where DashboardWidgetDetails.widget_config.selected_calendar == calendar_id.
    """
    try:
        service = DailyWidgetService(db)
        return await service.get_widgets_for_calendar_period(calendar_id, start_date, end_date)
    except Exception as e:
        raise raise_database_error(
            f"Failed to get widget activity for calendar {calendar_id}: {str(e)}"
        )

