"""
Pydantic schemas for API validation.
"""

from .ai import (
    DailyPlanRequest, WebSummaryRequest, ActivityGenerationRequest,
    DailyPlanResponse, WebSummaryResponse, ActivityGenerationResponse,
    WidgetInfo, AIPlanItem, AIOutputMetadata, DailyPlanData, WebSummaryData, ActivityGenerationData,
    ToolResponse, AIErrorResponse
)
from .weather import (
    WeatherResponse
)

from .dashboard_widget import (
    DashboardWidgetBase, DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    AlarmWidgetCreate, TodoWidgetCreate, TrackerWidgetCreate, WebSearchWidgetCreate,
    ActivityData, AlarmActivityData, TodoActivityData, TrackerActivityData, WebSearchActivityData
)

__all__ = [
    "DailyPlanRequest", "WebSummaryRequest", "ActivityGenerationRequest",
    "DailyPlanResponse", "WebSummaryResponse", "ActivityGenerationResponse", 
    "WidgetInfo", "AIPlanItem", "AIOutputMetadata", "DailyPlanData", "WebSummaryData", "ActivityGenerationData",
    "ToolResponse", "AIErrorResponse",
    "WeatherResponse",
    "DashboardWidgetBase", "DashboardWidgetCreate", "DashboardWidgetUpdate", "DashboardWidgetResponse",
    "AlarmWidgetCreate", "TodoWidgetCreate", "TrackerWidgetCreate", "WebSearchWidgetCreate",
    "ActivityData", "AlarmActivityData", "TodoActivityData", "TrackerActivityData", "WebSearchActivityData"
]
