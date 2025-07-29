"""
Alarm Widget Router
5 Core API endpoints for alarm management within widgets

Endpoints:
- POST /create - Create alarm for widget
- GET /{widget_id} - Get all alarms for widget
- POST /{widget_id} - Add new alarm to widget
- POST /{widget_id}/{alarm_id} - Update specific alarm
- DELETE /{widget_id}/{alarm_id} - Delete specific alarm

Examples:
- Daily Standup | daily | [09:00] 
- Yogi Birthday | once | [10:00] | Jun 20
- Meditation Reminder | daily | [07:00, 19:00]
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time, timedelta
import logging

from core.database import get_db
from models.database import Alarm, DashboardWidget
from models.schemas.alarm_schemas import (
    CreateAlarmRequest,
    UpdateAlarmRequest,
    AlarmResponse,
    AlarmType
)
from utils.router_utils import RouterUtils

logger = logging.getLogger(__name__)
router = APIRouter(tags=["alarm"])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_time_string(time_str: str) -> time:
    """Parse time string in HH:MM format"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM format.")

def _calculate_next_trigger(alarm: Alarm) -> Optional[datetime]:
    """Calculate next trigger time for an alarm"""
    if not alarm.is_active or not alarm.alarm_times:
        return None
    
    now = datetime.now()
    today = now.date()
    
    # Parse alarm times
    try:
        times = [_parse_time_string(t) for t in alarm.alarm_times]
    except ValueError:
        logger.error(f"Invalid time format in alarm {alarm.id}")
        return None
    
    if alarm.alarm_type == AlarmType.ONCE:
        if not alarm.specific_date:
            return None
        target_date = alarm.specific_date
        if target_date < today:
            return None
    else:
        target_date = today
    
    # Find next trigger time for today
    next_triggers = []
    for alarm_time in times:
        trigger_datetime = datetime.combine(target_date, alarm_time)
        if trigger_datetime > now:
            next_triggers.append(trigger_datetime)
    
    if next_triggers:
        return min(next_triggers)
    
    # No triggers today, calculate for next occurrence
    if alarm.alarm_type == AlarmType.DAILY:
        next_date = today + timedelta(days=1)
        return datetime.combine(next_date, times[0])
    elif alarm.alarm_type == AlarmType.WEEKLY:
        next_date = today + timedelta(days=7)
        return datetime.combine(next_date, times[0])
    
    return None

# ============================================================================
# HELPER FUNCTIONS FOR RESPONSE FORMATTING
# ============================================================================

def _format_alarm_response(alarm: Alarm) -> AlarmResponse:
    """Format Alarm for API response"""
    return AlarmResponse(
        id=alarm.id,
        dashboard_widget_id=alarm.dashboard_widget_id,
        title=alarm.title,
        alarm_type=alarm.alarm_type,
        alarm_times=alarm.alarm_times,
        frequency_value=alarm.frequency_value,
        specific_date=alarm.specific_date,
        is_active=alarm.is_active,
        is_snoozed=alarm.is_snoozed,
        snooze_until=alarm.snooze_until,
        last_triggered=alarm.last_triggered,
        next_trigger_time=alarm.next_trigger_time,
        created_at=alarm.created_at,
        updated_at=alarm.updated_at
    )

# ============================================================================
# ALARM WIDGET API - 5 Core Endpoints Only
# ============================================================================

@router.post("/create", response_model=AlarmResponse)
async def create_alarm_for_widget(
    request: CreateAlarmRequest,
    db: Session = Depends(get_db)
):
    """Create a new alarm for a widget"""
    try:
        # Verify widget exists
        widget = RouterUtils.verify_widget_exists(db, request.dashboard_widget_id, "alarm")
        
        # Validate time formats
        for time_str in request.alarm_times:
            try:
                _parse_time_string(time_str)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # Validate specific date for one-time alarms
        if request.alarm_type == AlarmType.ONCE and not request.specific_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specific date required for one-time alarms"
            )
        
        # Create alarm
        alarm = Alarm(
            dashboard_widget_id=request.dashboard_widget_id,
            title=request.title,
            alarm_type=request.alarm_type,
            alarm_times=request.alarm_times,
            frequency_value=request.frequency_value,
            specific_date=request.specific_date
        )
        
        # Calculate next trigger time
        alarm.next_trigger_time = _calculate_next_trigger(alarm)
        
        db.add(alarm)
        db.commit()
        db.refresh(alarm)
        
        logger.info(f"Created alarm: {alarm.id} - {alarm.title}")
        return _format_alarm_response(alarm)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alarm: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alarm: {str(e)}"
        )

@router.get("/{widget_id}", response_model=List[AlarmResponse])
async def get_widget_alarms(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Get all alarms for a specific widget"""
    try:
        # Verify widget exists
        widget = RouterUtils.verify_widget_exists(db, widget_id, "alarm")
        
        # Get all alarms for this widget
        alarms = db.query(Alarm).filter(
            Alarm.dashboard_widget_id == widget_id
        ).order_by(Alarm.next_trigger_time.asc()).all()
        
        # Update next trigger times
        for alarm in alarms:
            alarm.next_trigger_time = _calculate_next_trigger(alarm)
        
        db.commit()
        
        logger.info(f"Retrieved {len(alarms)} alarms for widget {widget_id}")
        return [_format_alarm_response(alarm) for alarm in alarms]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alarms for widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alarms: {str(e)}"
        )

@router.post("/{widget_id}", response_model=AlarmResponse)
async def add_alarm_to_widget(
    widget_id: str,
    alarm_data: CreateAlarmRequest,
    db: Session = Depends(get_db)
):
    """Add a new alarm to a widget"""
    try:
        # Verify widget exists
        widget = RouterUtils.verify_widget_exists(db, widget_id, "alarm")
        
        # Override widget_id from URL
        alarm_data.dashboard_widget_id = widget_id
        
        # Use the create endpoint logic
        return await create_alarm_for_widget(alarm_data, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding alarm to widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add alarm: {str(e)}"
        )

@router.post("/{widget_id}/{alarm_id}", response_model=AlarmResponse)
async def update_alarm(
    widget_id: str,
    alarm_id: str,
    update_data: UpdateAlarmRequest,
    db: Session = Depends(get_db)
):
    """Update a specific alarm"""
    try:
        # Verify widget exists
        widget = RouterUtils.verify_widget_exists(db, widget_id, "alarm")
        
        # Get alarm
        alarm = db.query(Alarm).filter(
            Alarm.id == alarm_id,
            Alarm.dashboard_widget_id == widget_id
        ).first()
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm not found"
            )
        
        # Update fields
        if update_data.title is not None:
            alarm.title = update_data.title
        
        if update_data.alarm_type is not None:
            alarm.alarm_type = update_data.alarm_type
        
        if update_data.alarm_times is not None:
            # Validate time formats
            for time_str in update_data.alarm_times:
                try:
                    _parse_time_string(time_str)
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )
            alarm.alarm_times = update_data.alarm_times
        
        if update_data.frequency_value is not None:
            alarm.frequency_value = update_data.frequency_value
        
        if update_data.specific_date is not None:
            alarm.specific_date = update_data.specific_date
        
        if update_data.is_active is not None:
            alarm.is_active = update_data.is_active
        
        # Recalculate next trigger time
        alarm.next_trigger_time = _calculate_next_trigger(alarm)
        alarm.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alarm)
        
        logger.info(f"Updated alarm: {alarm_id}")
        return _format_alarm_response(alarm)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alarm: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alarm: {str(e)}"
        )

@router.delete("/{widget_id}/{alarm_id}")
async def delete_alarm(
    widget_id: str,
    alarm_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific alarm"""
    try:
        # Verify widget exists
        widget = RouterUtils.verify_widget_exists(db, widget_id, "alarm")
        
        # Get alarm
        alarm = db.query(Alarm).filter(
            Alarm.id == alarm_id,
            Alarm.dashboard_widget_id == widget_id
        ).first()
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm not found"
            )
        
        alarm_title = alarm.title
        db.delete(alarm)
        db.commit()
        
        logger.info(f"Deleted alarm: {alarm_id} - {alarm_title}")
        return {"message": f"Alarm '{alarm_title}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alarm: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alarm: {str(e)}"
        )
