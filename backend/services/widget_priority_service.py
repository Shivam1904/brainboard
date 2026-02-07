"""
Widget Priority Service - Returns priority and reason for a dashboard widget on a given date.

Uses same logic as Kotlin PlanningList: RED (critical) / YELLOW (medium) / GREEN (low)
based on completion in 2d, 7d, 15d, 30d, 60d windows. Completion = daily_widget.activity_data.status == 'completed'.
"""
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession


# Valid priority levels
PRIORITY_CRITICAL = "critical"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Reason messages per condition (same idea as Kotlin wittyComments)
REASON_MESSAGES = {
    "DAILY_MISSED": [
        "It's been more than 2 days since you've done this <strong>daily</strong> habit!",
    ],
    "BIWEEKLY_QUOTA_MISSED": [
        "You haven't met your <strong>weekly</strong> goals in the past two weeks!",
    ],
    "WEEKLY_QUOTA_MISSED": [
        "This <strong>weekly</strong> goal is pending.",
    ],
    "BIMONTHLY_QUOTA_MISSED": [
        "Your <strong>monthly</strong> quota hasn't been met in two months!!",
    ],
    "MONTHLY_QUOTA_MISSED": [
        "Your <strong>monthly</strong> quota hasn't been met this month.",
    ],
    "ON_TRACK": [
        "You're on top of your missions.",
    ],
    "NOT_ENOUGH_HISTORY": [
        "Not enough history yet.",
    ],
}


def _is_completed(activity_data: Optional[Dict[str, Any]]) -> bool:
    """True if this daily widget row is considered completed (status == 'completed')."""
    if not activity_data or not isinstance(activity_data, dict):
        return False
    if activity_data.get("status") == "completed":
        return True
    for key in ("todo_activity", "tracker_activity", "alarm_activity", "websearch_activity"):
        sub = activity_data.get(key)
        if isinstance(sub, dict) and sub.get("status") == "completed":
            return True
    return False


def _count_completed_in_window(
    daily_rows: List[Dict[str, Any]],
    window_start: date,
    window_end: date,
) -> int:
    """Count how many days in [window_start, window_end] have a completed row."""
    count = 0
    for row in daily_rows:
        d = row.get("date")
        if d is None:
            continue
        if isinstance(d, str):
            d = date.fromisoformat(d[:10])
        if window_start <= d <= window_end and _is_completed(row.get("activity_data")):
            count += 1
    return count


def _get_required_and_period(frequency_details: Optional[Dict[str, Any]]) -> tuple:
    """
    Return (required_count, period) from widget frequency_details.
    period in ("DAILY", "WEEKLY", "MONTHLY").
    required_count: e.g. 1 for daily, 2 for 2x/week, 4 for 4x/month.
    """
    if not frequency_details or not isinstance(frequency_details, dict):
        return 1, "DAILY"
    period = (frequency_details.get("frequencyPeriod") or "DAILY").upper()
    if period not in ("DAILY", "WEEKLY", "MONTHLY"):
        period = "DAILY"
    req = frequency_details.get("frequency")
    if req is None or (isinstance(req, (int, float)) and req < 1):
        req = 1
    req = max(1, int(req))
    is_daily_habit = frequency_details.get("isDailyHabit") is True
    if is_daily_habit or period == "DAILY":
        return req, "DAILY"
    return req, period


class WidgetPriorityService:
    """Service that returns priority and reason for a widget on a given date."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_priority_for_date(self, widget_id: str, target_date: date) -> Dict[str, Any]:
        """
        Return priority (critical | medium | low) and reason for the given dashboard widget
        on the given date. Uses Kotlin-style windows: 2d, 7d, 15d, 30d, 60d.
        """
        from services.service_factory import ServiceFactory
        factory = ServiceFactory(self.db)
        widget_service = factory.dashboard_widget_service
        daily_service = factory.daily_widget_service

        widget = await widget_service.get_widget(widget_id)
        if not widget:
            return {
                "priority": PRIORITY_MEDIUM,
                "reason": "Widget not found.",
            }

        frequency_details = getattr(widget, "frequency_details", None) or {}
        required, period = _get_required_and_period(frequency_details)

        # Load all daily rows from (target_date - 60) to target_date (inclusive)
        start = target_date - timedelta(days=60)
        daily_rows = await daily_service.get_daily_widgets_in_date_range(
            widget_id, start, target_date
        )

        # Normalize date in rows to date object for comparison
        for row in daily_rows:
            d = row.get("date")
            if hasattr(d, "isoformat"):
                pass
            elif isinstance(d, str):
                row["date"] = date.fromisoformat(d[:10])

        # Windows (end = target_date; start = target_date - N days)
        def completed_in_last(n_days: int) -> int:
            w_start = target_date - timedelta(days=n_days)
            return _count_completed_in_window(daily_rows, w_start, target_date)

        two_days = completed_in_last(2)
        seven_days = completed_in_last(7)
        fifteen_days = completed_in_last(15)
        thirty_days = completed_in_last(30)
        sixty_days = completed_in_last(60)

        # Required counts per window (Kotlin logic)
        # RED: 2d (daily), 15d (weekly), 60d (monthly). YELLOW: 7d (weekly), 30d (monthly).
        if period == "DAILY":
            required_2d = required
            required_7d = required * 7
            required_15d = required * 15
            required_30d = required * 30
            required_60d = required * 60
        elif period == "WEEKLY":
            required_2d = 0
            required_7d = required
            required_15d = required * 2
            required_30d = required * 4
            required_60d = required * 8
        else:
            # MONTHLY
            required_2d = 0
            required_7d = 0
            required_15d = 0
            required_30d = required
            required_60d = required * 2

        def pick_reason(key: str) -> str:
            msgs = REASON_MESSAGES.get(key, [""])
            return msgs[0] if msgs else key

        # RED (critical): long windows missed
        if period == "DAILY" and two_days < required_2d:
            return {"priority": PRIORITY_CRITICAL, "reason": pick_reason("DAILY_MISSED")}
        if period == "WEEKLY" and fifteen_days < required_15d:
            return {"priority": PRIORITY_CRITICAL, "reason": pick_reason("BIWEEKLY_QUOTA_MISSED")}
        if period == "MONTHLY" and sixty_days < required_60d:
            return {"priority": PRIORITY_CRITICAL, "reason": pick_reason("BIMONTHLY_QUOTA_MISSED")}

        # YELLOW (medium): shorter windows missed
        if period == "DAILY" and two_days < required_2d:
            return {"priority": PRIORITY_MEDIUM, "reason": pick_reason("DAILY_MISSED")}
        if period == "WEEKLY" and seven_days < required_7d:
            return {"priority": PRIORITY_MEDIUM, "reason": pick_reason("WEEKLY_QUOTA_MISSED")}
        if period == "MONTHLY" and thirty_days < required_30d:
            return {"priority": PRIORITY_MEDIUM, "reason": pick_reason("MONTHLY_QUOTA_MISSED")}

        # GREEN (low): on track
        return {"priority": PRIORITY_LOW, "reason": pick_reason("ON_TRACK")}
