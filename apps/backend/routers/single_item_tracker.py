from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date, timedelta
import logging

from core.database import get_db
from models.database_models import SingleItemTracker, SingleItemTrackerLog, DashboardWidget
from models.schemas import (
    CreateSingleItemTrackerRequest,
    UpdateSingleItemTrackerRequest,
    UpdateValueRequest,
    SingleItemTrackerResponse,
    SingleItemTrackerWithLogsResponse,
    SingleItemTrackerLogResponse,
    SingleItemTrackerStatsResponse,
    SingleItemTrackerWidgetDataResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/widgets/single-item-tracker", tags=["single-item-tracker"])

def _calculate_progress_percentage(current: str, target: str, value_type: str) -> Optional[float]:
    """Calculate progress percentage if both values are numeric"""
    try:
        if value_type in ["number", "decimal"] and current and target:
            current_num = float(current)
            target_num = float(target)
            if target_num > 0:
                return min((current_num / target_num) * 100, 100.0)
    except (ValueError, ZeroDivisionError):
        pass
    return None

def _calculate_streak(tracker_id: str, db: Session) -> int:
    """Calculate consecutive days with entries"""
    logs = db.query(SingleItemTrackerLog).filter(
        SingleItemTrackerLog.tracker_id == tracker_id
    ).order_by(desc(SingleItemTrackerLog.date)).limit(30).all()
    
    if not logs:
        return 0
    
    streak = 0
    current_date = date.today()
    
    for log in logs:
        if log.date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

@router.post("/create", response_model=SingleItemTrackerResponse)
async def create_tracker(
    tracker_data: CreateSingleItemTrackerRequest,
    db: Session = Depends(get_db)
):
    """Create a new single item tracker"""
    try:
        # Verify widget exists
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == tracker_data.dashboard_widget_id
        ).first()
        
        if not widget:
            raise HTTPException(status_code=404, detail="Dashboard widget not found")
        
        # Check if tracker already exists for this widget
        existing_tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.dashboard_widget_id == tracker_data.dashboard_widget_id
        ).first()
        
        if existing_tracker:
            raise HTTPException(status_code=409, detail="Tracker already exists for this widget")
        
        # Create new tracker
        tracker = SingleItemTracker(
            dashboard_widget_id=tracker_data.dashboard_widget_id,
            item_name=tracker_data.item_name,
            item_unit=tracker_data.item_unit,
            current_value=tracker_data.current_value,
            target_value=tracker_data.target_value,
            value_type=tracker_data.value_type
        )
        
        db.add(tracker)
        db.commit()
        db.refresh(tracker)
        
        logger.info(f"Created single item tracker: {tracker.id} for item: {tracker.item_name}")
        return SingleItemTrackerResponse.from_orm(tracker)
        
    except Exception as e:
        logger.error(f"Error creating single item tracker: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tracker_id}/update-value", response_model=SingleItemTrackerResponse)
async def update_tracker_value(
    tracker_id: str,
    value_data: UpdateValueRequest,
    db: Session = Depends(get_db)
):
    """Update tracker value and create log entry"""
    try:
        # Get tracker
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.id == tracker_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Update current value
        tracker.current_value = value_data.value
        tracker.updated_at = datetime.utcnow()
        
        # Create log entry
        log_entry = SingleItemTrackerLog(
            tracker_id=tracker_id,
            value=value_data.value,
            date=date.today(),
            notes=value_data.notes
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(tracker)
        
        logger.info(f"Updated tracker {tracker_id} value to: {value_data.value}")
        return SingleItemTrackerResponse.from_orm(tracker)
        
    except Exception as e:
        logger.error(f"Error updating tracker value: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tracker_id}", response_model=SingleItemTrackerWithLogsResponse)
async def get_tracker(
    tracker_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of recent logs to include"),
    db: Session = Depends(get_db)
):
    """Get tracker with recent logs"""
    try:
        # Get tracker
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.id == tracker_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Get recent logs
        recent_logs = db.query(SingleItemTrackerLog).filter(
            SingleItemTrackerLog.tracker_id == tracker_id
        ).order_by(desc(SingleItemTrackerLog.date)).limit(limit).all()
        
        # Convert to response format
        response = SingleItemTrackerWithLogsResponse.from_orm(tracker)
        response.recent_logs = [SingleItemTrackerLogResponse.from_orm(log) for log in recent_logs]
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting tracker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget/{widget_id}/data", response_model=SingleItemTrackerWidgetDataResponse)
async def get_widget_data(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Get complete widget data for dashboard display"""
    try:
        # Get tracker for widget
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.dashboard_widget_id == widget_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="No tracker found for this widget")
        
        # Get recent logs (last 7 days)
        recent_logs = db.query(SingleItemTrackerLog).filter(
            SingleItemTrackerLog.tracker_id == tracker.id
        ).order_by(desc(SingleItemTrackerLog.date)).limit(7).all()
        
        # Calculate stats
        total_entries = db.query(SingleItemTrackerLog).filter(
            SingleItemTrackerLog.tracker_id == tracker.id
        ).count()
        
        progress_percentage = _calculate_progress_percentage(
            tracker.current_value, tracker.target_value, tracker.value_type
        )
        
        last_updated = recent_logs[0].date if recent_logs else None
        streak_days = _calculate_streak(tracker.id, db)
        
        stats = SingleItemTrackerStatsResponse(
            total_entries=total_entries,
            current_value=tracker.current_value,
            target_value=tracker.target_value,
            progress_percentage=progress_percentage,
            last_updated=last_updated,
            streak_days=streak_days
        )
        
        return SingleItemTrackerWidgetDataResponse(
            widget_id=widget_id,
            tracker=SingleItemTrackerResponse.from_orm(tracker),
            stats=stats,
            recent_logs=[SingleItemTrackerLogResponse.from_orm(log) for log in recent_logs]
        )
        
    except Exception as e:
        logger.error(f"Error getting widget data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tracker_id}", response_model=SingleItemTrackerResponse)
async def update_tracker(
    tracker_id: str,
    update_data: UpdateSingleItemTrackerRequest,
    db: Session = Depends(get_db)
):
    """Update tracker settings (not the value)"""
    try:
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.id == tracker_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Update fields
        if update_data.item_name is not None:
            tracker.item_name = update_data.item_name
        if update_data.item_unit is not None:
            tracker.item_unit = update_data.item_unit
        if update_data.target_value is not None:
            tracker.target_value = update_data.target_value
        if update_data.value_type is not None:
            tracker.value_type = update_data.value_type
        
        tracker.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tracker)
        
        logger.info(f"Updated tracker settings: {tracker_id}")
        return SingleItemTrackerResponse.from_orm(tracker)
        
    except Exception as e:
        logger.error(f"Error updating tracker: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tracker_id}/logs", response_model=List[SingleItemTrackerLogResponse])
async def get_tracker_logs(
    tracker_id: str,
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get tracker logs with pagination"""
    try:
        # Verify tracker exists
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.id == tracker_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Get logs
        logs = db.query(SingleItemTrackerLog).filter(
            SingleItemTrackerLog.tracker_id == tracker_id
        ).order_by(desc(SingleItemTrackerLog.date)).offset(offset).limit(limit).all()
        
        return [SingleItemTrackerLogResponse.from_orm(log) for log in logs]
        
    except Exception as e:
        logger.error(f"Error getting tracker logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tracker_id}", status_code=204)
async def delete_tracker(
    tracker_id: str,
    db: Session = Depends(get_db)
):
    """Delete tracker and all its logs"""
    try:
        tracker = db.query(SingleItemTracker).filter(
            SingleItemTracker.id == tracker_id
        ).first()
        
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        db.delete(tracker)
        db.commit()
        
        logger.info(f"Deleted tracker: {tracker_id}")
        
    except Exception as e:
        logger.error(f"Error deleting tracker: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
