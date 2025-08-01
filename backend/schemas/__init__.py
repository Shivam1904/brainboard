"""
Pydantic schemas for API validation.
"""

from .ai import (
    DailyPlanRequest, WebSummaryRequest, ActivityGenerationRequest,
    DailyPlanResponse, WebSummaryResponse, ActivityGenerationResponse,
    WidgetInfo, AIPlanItem, AIOutputMetadata, DailyPlanData, WebSummaryData, ActivityGenerationData,
    ToolResponse, AIErrorResponse
)

__all__ = [
    "DailyPlanRequest", "WebSummaryRequest", "ActivityGenerationRequest",
    "DailyPlanResponse", "WebSummaryResponse", "ActivityGenerationResponse", 
    "WidgetInfo", "AIPlanItem", "AIOutputMetadata", "DailyPlanData", "WebSummaryData", "ActivityGenerationData",
    "ToolResponse", "AIErrorResponse"
]
