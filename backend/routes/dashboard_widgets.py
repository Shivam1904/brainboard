"""
Dashboard Widgets Routes - Consolidated routes for all widget types.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import date

from db.dependency import get_db_session_dependency
from services.service_factory import ServiceFactory
from schemas.dashboard_widget import (
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    DashboardWidgetResponse
)

router = APIRouter(tags=["dashboard-widgets"])



@router.post("/newwidget", response_model=DashboardWidgetResponse)
async def create_widget(
    widget_data: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Create a new widget with the given configuration."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        widget = await service.create_widget(
            widget_type=widget_data.widget_type,
            widget_data=widget_data
        )
        
        # Commit the transaction at the route level
        await db.commit()
        
        return DashboardWidgetResponse.from_orm(widget)
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget: {str(e)}"
        )


@router.get("/allwidgets", response_model=List[DashboardWidgetResponse])
async def get_user_widgets(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all widgets for a specific user."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        widgets = await service.get_user_widgets()
        return [DashboardWidgetResponse.from_orm(widget) for widget in widgets]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user widgets: {str(e)}"
        )


@router.get("/{widget_id}", response_model=DashboardWidgetResponse)
async def get_widget(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get a specific widget by ID."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        widget = await service.get_widget(widget_id)
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        return DashboardWidgetResponse.from_orm(widget)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget: {str(e)}"
        )


@router.put("/{widget_id}/update", response_model=DashboardWidgetResponse)
async def update_widget(
    widget_id: str,
    update_data: DashboardWidgetUpdate,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update a widget with new data."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        widget = await service.update_widget(widget_id, update_data)
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Commit the transaction at the route level
        await db.commit()
        
        return DashboardWidgetResponse.from_orm(widget)
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
        )


@router.delete("/{widget_id}/delete")
async def delete_widget(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Soft delete a widget by setting delete_flag to True."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        success = await service.delete_widget(widget_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        return {"message": "Widget deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete widget: {str(e)}"
        )


@router.get("/alloftype/{widget_type}", response_model=List[DashboardWidgetResponse])
async def get_widgets_by_type(
    widget_type: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all widgets of a specific type for a user."""
    try:
        service_factory = ServiceFactory(db)
        service = service_factory.dashboard_widget_service
        
        widgets = await service.get_widgets_by_type(widget_type)
        return [DashboardWidgetResponse.from_orm(widget) for widget in widgets]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widgets by type: {str(e)}"
        )

