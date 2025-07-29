"""
Single Item Tracker Widget Router
6 Core API endpoints for tracking single metrics (weight, pages, steps, etc.)

Endpoints:
- POST / - Create Tracker Widget
- GET /{tracker_id} - Get Tracker
- POST /{tracker_id}/entry - Add Entry
- POST /{tracker_id}/entry/{entry_id} - Update Entry  
- DELETE /{tracker_id}/entry/{entry_id} - Delete Entry
- GET /{tracker_id}/history - Get Tracker History

Examples:
- Weight Tracker: 75.5 kg
- Book Pages: 234 pages
- Daily Steps: 8,500 steps
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date
import logging

from core.database import get_db
from models.database_models import SingleItemTracker, SingleItemTrackerLog, DashboardWidget
from models.schemas.tracker_schemas import (
    CreateSingleItemTrackerRequest,
    SingleItemTrackerResponse,
    UpdateValueRequest,
    SingleItemTrackerLogResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["single-item-tracker"])

# ============================================================================
# SINGLE ITEM TRACKER API - 6 Core Endpoints Only
# ============================================================================

@router.post("/", response_model=SingleItemTrackerResponse)
async def create_tracker_widget(
    request: CreateSingleItemTrackerRequest,
    db: Session = Depends(get_db)
):
    """Create a new single item tracker widget"""
    try:
        # Verify widget exists
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == request.dashboard_widget_id
        ).first()
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard widget not found"
            )
        
        # Check if tracker already exists for this widget
        existing_tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.dashboard_widget_id == request.dashboard_widget_id
        ).first()
        if existing_tracker:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tracker already exists for this widget"
            )
        
        # Create new tracker
        tracker = SingleItemTracker(
            dashboard_widget_id=request.dashboard_widget_id,
            item_name=request.item_name,
            item_unit=request.item_unit,
            current_value=request.current_value,
            target_value=request.target_value,
            value_type=request.value_type.value
        )
        
        db.add(tracker)
        db.commit()
        db.refresh(tracker)
        
        logger.info(f"Created tracker: {tracker.item_name} (ID: {tracker.id})")
        return _format_tracker_response(tracker)
        
    except Exception as e:
        logger.error(f"Error creating tracker: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tracker"
        )

@router.get("/{tracker_id}", response_model=SingleItemTrackerResponse)
async def get_tracker(
    tracker_id: str,
    db: Session = Depends(get_db)
):
    """Get tracker details"""
    tracker = db.query(SingleItemTracker).filter(
        SingleItemTracker.id == tracker_id
    ).first()
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracker not found"
        )
    
    return _format_tracker_response(tracker)

@router.post("/{tracker_id}/entry", response_model=SingleItemTrackerLogResponse)
async def add_tracker_entry(
    tracker_id: str,
    request: UpdateValueRequest,
    db: Session = Depends(get_db)
):
    """Add new entry to tracker"""
    # Verify tracker exists
    tracker = db.query(SingleItemTracker).filter(
        SingleItemTracker.id == tracker_id
    ).first()
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracker not found"
        )
    
    try:
        # Create log entry
        entry = SingleItemTrackerLog(
            tracker_id=tracker_id,
            value=request.value,
            date=date.today(),
            notes=request.notes
        )
        
        # Update tracker's current value
        tracker.current_value = request.value
        tracker.updated_at = datetime.utcnow()
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        logger.info(f"Added entry to tracker {tracker_id}: {request.value}")
        return _format_log_response(entry)
        
    except Exception as e:
        logger.error(f"Error adding entry: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add entry"
        )

@router.post("/{tracker_id}/entry/{entry_id}", response_model=SingleItemTrackerLogResponse)
async def update_tracker_entry(
    tracker_id: str,
    entry_id: str,
    request: UpdateValueRequest,
    db: Session = Depends(get_db)
):
    """Update existing entry"""
    # Verify tracker exists
    tracker = db.query(SingleItemTracker).filter(
        SingleItemTracker.id == tracker_id
    ).first()
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracker not found"
        )
    
    # Get entry
    entry = db.query(SingleItemTrackerLog).filter(
        SingleItemTrackerLog.id == entry_id,
        SingleItemTrackerLog.tracker_id == tracker_id
    ).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    try:
        # Update entry
        entry.value = request.value
        entry.notes = request.notes
        
        # If this is the most recent entry, update tracker's current value
        latest_entry = db.query(SingleItemTrackerLog).filter(
            SingleItemTrackerLog.tracker_id == tracker_id
        ).order_by(desc(SingleItemTrackerLog.date)).first()
        
        if latest_entry and latest_entry.id == entry_id:
            tracker.current_value = request.value
            tracker.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entry)
        
        logger.info(f"Updated entry {entry_id} in tracker {tracker_id}")
        return _format_log_response(entry)
        
    except Exception as e:
        logger.error(f"Error updating entry: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update entry"
        )

@router.delete("/{tracker_id}/entry/{entry_id}")
async def delete_entry(
    tracker_id: str,
    entry_id: str,
    db: Session = Depends(get_db)
):
    """Delete entry from tracker"""
    # Verify tracker exists
    tracker = db.query(SingleItemTracker).filter(
        SingleItemTracker.id == tracker_id
    ).first()
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracker not found"
        )
    
    # Get entry
    entry = db.query(SingleItemTrackerLog).filter(
        SingleItemTrackerLog.id == entry_id,
        SingleItemTrackerLog.tracker_id == tracker_id
    ).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    try:
        # Check if this is the current value entry
        was_current = (tracker.current_value == entry.value)
        
        db.delete(entry)
        
        # If we deleted the current value, update to the most recent remaining entry
        if was_current:
            latest_entry = db.query(SingleItemTrackerLog).filter(
                SingleItemTrackerLog.tracker_id == tracker_id
            ).order_by(desc(SingleItemTrackerLog.date)).first()
            
            if latest_entry:
                tracker.current_value = latest_entry.value
            else:
                tracker.current_value = None
            tracker.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Deleted entry {entry_id} from tracker {tracker_id}")
        return {"message": "Entry deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting entry: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete entry"
        )

@router.get("/{tracker_id}/history", response_model=List[SingleItemTrackerLogResponse])
async def get_tracker_history(
    tracker_id: str,
    limit: int = Query(30, ge=1, le=100, description="Number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: Session = Depends(get_db)
):
    """Get tracker history with pagination"""
    # Verify tracker exists
    tracker = db.query(SingleItemTracker).filter(
        SingleItemTracker.id == tracker_id
    ).first()
    if not tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracker not found"
        )
    
    # Get history entries
    entries = db.query(SingleItemTrackerLog).filter(
        SingleItemTrackerLog.tracker_id == tracker_id
    ).order_by(desc(SingleItemTrackerLog.date)).offset(offset).limit(limit).all()
    
    return [_format_log_response(entry) for entry in entries]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_tracker_response(tracker: SingleItemTracker) -> SingleItemTrackerResponse:
    """Format tracker for API response"""
    return SingleItemTrackerResponse(
        id=tracker.id,
        dashboard_widget_id=tracker.dashboard_widget_id,
        item_name=tracker.item_name,
        item_unit=tracker.item_unit,
        current_value=tracker.current_value,
        target_value=tracker.target_value,
        value_type=tracker.value_type,
        created_at=tracker.created_at,
        updated_at=tracker.updated_at
    )

def _format_log_response(log: SingleItemTrackerLog) -> SingleItemTrackerLogResponse:
    """Format log entry for API response"""
    return SingleItemTrackerLogResponse(
        id=log.id,
        value=log.value,
        date=log.date,
        notes=log.notes,
        created_at=log.created_at
    )
