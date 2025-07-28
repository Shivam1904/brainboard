from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from core.database import get_db
from models.schemas import (
    CreateWidgetRequest,
    CreateWidgetResponse,
    GenerateSummaryRequest,
    SummaryResponse,
    WidgetInfo,
    ErrorResponse
)
from services.widget_service import WidgetService
from factories.service_factory import ServiceFactory

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get widget service
def get_widget_service(db: Session = Depends(get_db)) -> WidgetService:
    """Create widget service with database session"""
    return ServiceFactory.create_widget_service(db)

@router.post(
    "/create",
    response_model=CreateWidgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Web Summary Widget",
    description="Create a new web summary widget and generate the first summary"
)
async def create_widget(
    request: CreateWidgetRequest,
    widget_service: WidgetService = Depends(get_widget_service)
) -> CreateWidgetResponse:
    """
    Create a new web summary widget with an initial query.
    This endpoint:
    1. Creates a new widget in the database
    2. Immediately generates the first summary
    3. Returns both widget info and the first summary
    """
    try:
        logger.info(f"Creating widget with query: {request.query}")
        
        response = await widget_service.create_web_summary_widget(
            query=request.query
        )
        
        logger.info(f"Successfully created widget {response.widget_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid request for widget creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Widget creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create widget. Please try again."
        )

@router.post(
    "/{widget_id}/generate",
    response_model=SummaryResponse,
    summary="Generate New Summary",
    description="Generate a new summary for an existing widget"
)
async def generate_summary(
    widget_id: str,
    request: GenerateSummaryRequest,
    widget_service: WidgetService = Depends(get_widget_service)
) -> SummaryResponse:
    """
    Generate a new summary for an existing widget.
    This is the "slow" endpoint that:
    1. Performs web search
    2. Uses AI to generate summary
    3. Saves the new summary to database
    4. Returns the fresh summary
    """
    try:
        logger.info(f"Generating summary for widget {widget_id} with query: {request.query}")
        
        response = await widget_service.generate_new_summary(
            widget_id=widget_id,
            query=request.query
        )
        
        logger.info(f"Successfully generated summary for widget {widget_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid request for summary generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Summary generation failed for widget {widget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary. Please try again."
        )

@router.get(
    "/{widget_id}/latest",
    response_model=SummaryResponse,
    summary="Get Latest Summary",
    description="Get the latest summary for a widget (fast database lookup)"
)
async def get_latest_summary(
    widget_id: str,
    widget_service: WidgetService = Depends(get_widget_service)
) -> SummaryResponse:
    """
    Get the latest summary for a widget from the database.
    This is the "fast" endpoint that:
    1. Queries the database for the most recent summary
    2. Returns cached summary immediately
    3. No AI processing involved
    """
    try:
        logger.info(f"Fetching latest summary for widget {widget_id}")
        
        summary = await widget_service.get_latest_summary(widget_id)
        
        if not summary:
            logger.warning(f"No summary found for widget {widget_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No summary found for widget {widget_id}"
            )
        
        logger.info(f"Successfully retrieved latest summary for widget {widget_id}")
        return summary
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        logger.warning(f"Invalid widget ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get latest summary for widget {widget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summary. Please try again."
        )

@router.get(
    "/{widget_id}",
    response_model=WidgetInfo,
    summary="Get Widget Info",
    description="Get complete widget information including latest summary"
)
async def get_widget_info(
    widget_id: str,
    widget_service: WidgetService = Depends(get_widget_service)
) -> WidgetInfo:
    """
    Get complete information about a widget including its latest summary.
    """
    try:
        logger.info(f"Fetching widget info for {widget_id}")
        
        widget_info = await widget_service.get_widget_info(widget_id)
        
        if not widget_info:
            logger.warning(f"Widget {widget_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        logger.info(f"Successfully retrieved widget info for {widget_id}")
        return widget_info
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to get widget info for {widget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve widget information. Please try again."
        )

@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Widget",
    description="Delete a widget and all its summaries"
)
async def delete_widget(
    widget_id: str,
    widget_service: WidgetService = Depends(get_widget_service)
) -> None:
    """
    Delete a widget and all its associated summaries.
    """
    try:
        logger.info(f"Deleting widget {widget_id}")
        
        deleted = await widget_service.delete_widget(widget_id)
        
        if not deleted:
            logger.warning(f"Widget {widget_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        logger.info(f"Successfully deleted widget {widget_id}")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to delete widget {widget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete widget. Please try again."
        )
