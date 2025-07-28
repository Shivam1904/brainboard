from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta, time
import logging
import json

from core.database import get_db
from models.database_models import Alarm, DashboardWidget
from models.schemas import (
    CreateAlarmRequest,
    UpdateAlarmRequest,
    UpdateAlarmStatusRequest,
    AlarmResponse,
    AlarmWidgetDataResponse,
    AlarmType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/widgets/alarm", tags=["alarm"])

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
        
        # Find next occurrence on the specific date
        target_date = alarm.specific_date
        if target_date < today:
            return None  # Past date, no future trigger
        
        # Find next time today or on the specific date
        for alarm_time in sorted(times):
            trigger_datetime = datetime.combine(target_date, alarm_time)
            if trigger_datetime > now:
                return trigger_datetime
        return None
    
    elif alarm.alarm_type == AlarmType.DAILY:
        # Find next daily occurrence
        frequency = alarm.frequency_value or 1
        
        # Check today first
        for alarm_time in sorted(times):
            trigger_datetime = datetime.combine(today, alarm_time)
            if trigger_datetime > now:
                return trigger_datetime
        
        # If no more times today, find next occurrence based on frequency
        next_date = today + timedelta(days=frequency)
        next_time = min(times)  # Earliest time of the day
        return datetime.combine(next_date, next_time)
    
    elif alarm.alarm_type == AlarmType.WEEKLY:
        # Find next weekly occurrence
        frequency = alarm.frequency_value or 1
        days_ahead = frequency * 7
        
        # Check remaining times today
        for alarm_time in sorted(times):
            trigger_datetime = datetime.combine(today, alarm_time)
            if trigger_datetime > now:
                return trigger_datetime
        
        # Next week
        next_date = today + timedelta(days=days_ahead)
        next_time = min(times)
        return datetime.combine(next_date, next_time)
    
    elif alarm.alarm_type == AlarmType.MONTHLY:
        # Find next monthly occurrence (approximate)
        frequency = alarm.frequency_value or 1
        
        # Check remaining times today
        for alarm_time in sorted(times):
            trigger_datetime = datetime.combine(today, alarm_time)
            if trigger_datetime > now:
                return trigger_datetime
        
        # Next month (approximate)
        next_date = today + timedelta(days=frequency * 30)
        next_time = min(times)
        return datetime.combine(next_date, next_time)
    
    elif alarm.alarm_type == AlarmType.YEARLY:
        # Find next yearly occurrence
        frequency = alarm.frequency_value or 1
        
        # Check remaining times today
        for alarm_time in sorted(times):
            trigger_datetime = datetime.combine(today, alarm_time)
            if trigger_datetime > now:
                return trigger_datetime
        
        # Next year
        next_date = today + timedelta(days=frequency * 365)
        next_time = min(times)
        return datetime.combine(next_date, next_time)
    
    return None

@router.get("", response_model=List[AlarmResponse])
async def get_alarms(
    widget_id: Optional[str] = Query(None, description="Filter by widget ID"),
    active_only: bool = Query(True, description="Only return active alarms"),
    db: Session = Depends(get_db)
):
    """Get alarms, optionally filtered by widget"""
    try:
        query = db.query(Alarm)
        
        if widget_id:
            query = query.filter(Alarm.dashboard_widget_id == widget_id)
        
        if active_only:
            query = query.filter(Alarm.is_active == True)
        
        alarms = query.order_by(Alarm.next_trigger_time.asc()).all()
        
        # Update next trigger times
        for alarm in alarms:
            alarm.next_trigger_time = _calculate_next_trigger(alarm)
        
        db.commit()
        
        logger.info(f"Retrieved {len(alarms)} alarms")
        return [AlarmResponse.from_orm(alarm) for alarm in alarms]
        
    except Exception as e:
        logger.error(f"Error getting alarms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add", response_model=AlarmResponse)
async def create_alarm(
    alarm_data: CreateAlarmRequest,
    db: Session = Depends(get_db)
):
    """Create a new alarm"""
    try:
        # Verify widget exists
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == alarm_data.dashboard_widget_id
        ).first()
        
        if not widget:
            raise HTTPException(status_code=404, detail="Dashboard widget not found")
        
        # Validate time formats
        for time_str in alarm_data.alarm_times:
            try:
                _parse_time_string(time_str)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Validate specific date for one-time alarms
        if alarm_data.alarm_type == AlarmType.ONCE and not alarm_data.specific_date:
            raise HTTPException(status_code=400, detail="Specific date required for one-time alarms")
        
        # Create alarm
        alarm = Alarm(
            dashboard_widget_id=alarm_data.dashboard_widget_id,
            title=alarm_data.title,
            alarm_type=alarm_data.alarm_type,
            alarm_times=alarm_data.alarm_times,
            frequency_value=alarm_data.frequency_value,
            specific_date=alarm_data.specific_date
        )
        
        # Calculate next trigger time
        alarm.next_trigger_time = _calculate_next_trigger(alarm)
        
        db.add(alarm)
        db.commit()
        db.refresh(alarm)
        
        logger.info(f"Created alarm: {alarm.id} - {alarm.title}")
        return AlarmResponse.from_orm(alarm)
        
    except Exception as e:
        logger.error(f"Error creating alarm: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alarm_id}/updateStatus", response_model=AlarmResponse)
async def update_alarm_status(
    alarm_id: str,
    status_data: UpdateAlarmStatusRequest,
    db: Session = Depends(get_db)
):
    """Update alarm status (active, snoozed, etc.)"""
    try:
        alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
        
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
        # Update status fields
        if status_data.is_active is not None:
            alarm.is_active = status_data.is_active
        
        if status_data.is_snoozed is not None:
            alarm.is_snoozed = status_data.is_snoozed
            
            if status_data.is_snoozed and status_data.snooze_minutes:
                alarm.snooze_until = datetime.now() + timedelta(minutes=status_data.snooze_minutes)
            elif not status_data.is_snoozed:
                alarm.snooze_until = None
        
        # Recalculate next trigger time
        alarm.next_trigger_time = _calculate_next_trigger(alarm)
        alarm.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alarm)
        
        logger.info(f"Updated alarm status: {alarm_id}")
        return AlarmResponse.from_orm(alarm)
        
    except Exception as e:
        logger.error(f"Error updating alarm status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{alarm_id}", response_model=AlarmResponse)
async def update_alarm(
    alarm_id: str,
    update_data: UpdateAlarmRequest,
    db: Session = Depends(get_db)
):
    """Update alarm details"""
    try:
        alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
        
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
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
                    raise HTTPException(status_code=400, detail=str(e))
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
        return AlarmResponse.from_orm(alarm)
        
    except Exception as e:
        logger.error(f"Error updating alarm: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget/{widget_id}/data", response_model=AlarmWidgetDataResponse)
async def get_widget_data(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Get complete alarm widget data for dashboard display"""
    try:
        # Get all alarms for this widget
        alarms = db.query(Alarm).filter(
            Alarm.dashboard_widget_id == widget_id
        ).order_by(Alarm.next_trigger_time.asc()).all()
        
        # Update next trigger times
        for alarm in alarms:
            alarm.next_trigger_time = _calculate_next_trigger(alarm)
        
        db.commit()
        
        # Calculate stats
        total_alarms = len(alarms)
        active_alarms = sum(1 for a in alarms if a.is_active)
        next_alarm = next((a for a in alarms if a.is_active and a.next_trigger_time), None)
        
        stats = {
            "total_alarms": total_alarms,
            "active_alarms": active_alarms,
            "next_alarm_time": next_alarm.next_trigger_time.isoformat() if next_alarm and next_alarm.next_trigger_time else None,
            "next_alarm_title": next_alarm.title if next_alarm else None
        }
        
        return AlarmWidgetDataResponse(
            widget_id=widget_id,
            alarms=[AlarmResponse.from_orm(alarm) for alarm in alarms],
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting widget data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{alarm_id}", status_code=204)
async def delete_alarm(
    alarm_id: str,
    db: Session = Depends(get_db)
):
    """Delete an alarm"""
    try:
        alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
        
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
        db.delete(alarm)
        db.commit()
        
        logger.info(f"Deleted alarm: {alarm_id}")
        
    except Exception as e:
        logger.error(f"Error deleting alarm: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(
    alarm_id: str,
    db: Session = Depends(get_db)
):
    """Get specific alarm details"""
    try:
        alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
        
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
        # Update next trigger time
        alarm.next_trigger_time = _calculate_next_trigger(alarm)
        db.commit()
        
        return AlarmResponse.from_orm(alarm)
        
    except Exception as e:
        logger.error(f"Error getting alarm: {e}")
        raise HTTPException(status_code=500, detail=str(e))
