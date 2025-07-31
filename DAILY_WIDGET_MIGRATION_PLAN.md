# Daily Widget System Migration Plan (Simplified)

## 📋 Overview

The Daily Widget system is a core feature that determines which widgets to show users each day. For this initial implementation, we'll focus on:

1. **Adding widgets to today's list** - Manual widget selection
2. **Retrieving today's widgets** - Get the list of widgets for today

## 🎯 Focus: Two Core APIs

### Primary APIs to Implement
- `/api/v1/dashboard/widget/addtotoday/{widget_id}` - Add a widget to today's list
- `/api/v1/dashboard/getTodayWidgetList` - Get today's widget list

### Future APIs (Not in this phase)
- `/api/v1/ai/generate_today_plan` - AI-powered daily plan generation (later)
- Activity tracking endpoints (later)

## 🏗️ Current Architecture (Old Backend)

### Core Tables
- `DailyWidget` - Daily widget selections
- `AlarmItemActivity` - Daily alarm activities (already exists in new backend)

### Key Services
- `DashboardService` - Retrieves today's widgets
- `WidgetService` - Widget management (already exists in new backend)

## 🎯 New Architecture Plan (Following New Backend Guidelines)

### 1. Database Models (`/backend/models/`)

#### Core Model (Following existing patterns)
```python
# daily_widget.py
"""
Daily Widget model - Daily widget selections.
"""
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Date, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import uuid

class DailyWidget(BaseModel):
    """Daily Widget - Daily widget selections"""
    __tablename__ = "daily_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_ids = Column(JSON, nullable=False)  # Array of widget IDs: ["id0", "id1", "id2", "id3"]
    widget_type = Column(String, nullable=False)  # 'todo-habit', 'todo-task', 'alarm', 'singleitemtracker', 'websearch'
    priority = Column(String, nullable=False)  # 'HIGH', 'MEDIUM', 'LOW'
    reasoning = Column(Text, nullable=True)  # Manual reasoning or AI reasoning
    date = Column(Date, nullable=False)  # Date when this widget should be shown
    is_active = Column(Boolean, default=True)  # Indicates if the widget is active
    
    # Relationships
    alarm_activities = relationship("AlarmItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
```

#### Update Existing Alarm Activity Model
```python
# Update alarm_item_activity.py to include daily_widget_id
"""
Alarm Item Activity model - Daily alarm activities.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import uuid

class AlarmItemActivity(BaseModel):
    """Alarm Item Activity - Daily alarm activities"""
    __tablename__ = "alarm_item_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=True)  # Add this field
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    alarmdetails_id = Column(String, ForeignKey("alarm_details.id"), nullable=False)
    started_at = Column(DateTime, nullable=True)
    snoozed_at = Column(DateTime, nullable=True)
    snooze_until = Column(DateTime, nullable=True)
    snooze_count = Column(Integer, default=0)
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="alarm_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    alarm_details = relationship("AlarmDetails", back_populates="alarm_activities")
```

### 2. Services (`/backend/services/`)

#### Core Service (Following existing patterns)
```python
# daily_widget_service.py
"""
Daily Widget service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

from models.daily_widget import DailyWidget
from models.dashboard_widget_details import DashboardWidgetDetails

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# SERVICE CLASS
# ============================================================================
class DailyWidgetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_widget_list(self, user_id: str, target_date: date) -> List[Dict[str, Any]]:
        """Get today's widget list from table DailyWidget."""
        try:
            stmt = select(DailyWidget).where(
                DailyWidget.date == target_date,
                DailyWidget.is_active == True,
                DailyWidget.delete_flag == False
            ).order_by(DailyWidget.priority.desc())
            
            result = await self.db.execute(stmt)
            daily_widgets = result.scalars().all()
            
            widgets_data = []
            for daily_widget in daily_widgets:
                widgets_data.append({
                    "id": daily_widget.id,
                    "widget_ids": daily_widget.widget_ids,
                    "widget_type": daily_widget.widget_type,
                    "priority": daily_widget.priority,
                    "reasoning": daily_widget.reasoning,
                    "date": daily_widget.date.isoformat(),
                    "is_active": daily_widget.is_active
                })
            
            return widgets_data
            
        except Exception as e:
            logger.error(f"Error getting today's widget list: {e}")
            raise

    async def add_widget_to_today(self, widget_id: str, user_id: str, target_date: date) -> Dict[str, Any]:
        """Add a widget to today's list."""
        try:
            # First, check if the widget exists and belongs to the user
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.id == widget_id,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                return {
                    "success": False,
                    "message": "Widget not found or does not belong to user"
                }
            
            # Check if widget is already in today's list
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == target_date,
                    DailyWidget.is_active == True,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            existing_daily_widgets = result.scalars().all()
            
            # Check if widget is already in any existing daily widget
            for daily_widget in existing_daily_widgets:
                if widget_id in daily_widget.widget_ids:
                    return {
                        "success": False,
                        "message": "Widget is already in today's list"
                    }
            
            # Find existing daily widget of the same type, or create new one
            existing_daily_widget = None
            for daily_widget in existing_daily_widgets:
                if daily_widget.widget_type == widget.widget_type:
                    existing_daily_widget = daily_widget
                    break
            
            if existing_daily_widget:
                # Add widget to existing daily widget
                widget_ids = existing_daily_widget.widget_ids
                widget_ids.append(widget_id)
                existing_daily_widget.widget_ids = widget_ids
                await self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Widget added to existing {widget.widget_type} group",
                    "daily_widget_id": existing_daily_widget.id,
                    "widget_ids": widget_ids
                }
            else:
                # Create new daily widget
                new_daily_widget = DailyWidget(
                    widget_ids=[widget_id],
                    widget_type=widget.widget_type,
                    priority="MEDIUM",  # Default priority
                    reasoning=f"Manually added widget: {widget.title}",
                    date=target_date,
                    is_active=True
                )
                
                self.db.add(new_daily_widget)
                await self.db.commit()
                await self.db.refresh(new_daily_widget)
                
                return {
                    "success": True,
                    "message": f"New {widget.widget_type} group created with widget",
                    "daily_widget_id": new_daily_widget.id,
                    "widget_ids": [widget_id]
                }
                
        except Exception as e:
            logger.error(f"Error adding widget to today: {e}")
            await self.db.rollback()
            raise

    async def remove_widget_from_today(self, widget_id: str, user_id: str, target_date: date) -> Dict[str, Any]:
        """Remove a widget from today's list."""
        try:
            # Find daily widgets containing this widget
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == target_date,
                    DailyWidget.is_active == True,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            daily_widgets = result.scalars().all()
            
            for daily_widget in daily_widgets:
                if widget_id in daily_widget.widget_ids:
                    widget_ids = daily_widget.widget_ids
                    widget_ids.remove(widget_id)
                    
                    if len(widget_ids) == 0:
                        # No widgets left, deactivate the daily widget
                        daily_widget.is_active = False
                    else:
                        # Update with remaining widgets
                        daily_widget.widget_ids = widget_ids
                    
                    await self.db.commit()
                    
                    return {
                        "success": True,
                        "message": "Widget removed from today's list",
                        "daily_widget_id": daily_widget.id,
                        "remaining_widgets": widget_ids
                    }
            
            return {
                "success": False,
                "message": "Widget not found in today's list"
            }
                
        except Exception as e:
            logger.error(f"Error removing widget from today: {e}")
            await self.db.rollback()
            raise
```

### 3. Routes (`/backend/routes/`)

#### Dashboard Routes (Following existing patterns)
```python
# dashboard.py
"""
Dashboard routes for dashboard management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from datetime import date

from db.dependency import get_db_session_dependency
from services.daily_widget_service import DailyWidgetService
from schemas.dashboard import (
    TodayWidgetListResponse,
    AddWidgetToTodayResponse,
    RemoveWidgetFromTodayResponse
)
from utils.errors import raise_not_found, raise_database_error

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# DEPENDENCIES
# ============================================================================
def get_default_user_id(db: AsyncSession = Depends(get_db_session_dependency)) -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================
@router.get("/getTodayWidgetList", response_model=List[TodayWidgetListResponse])
async def get_today_widget_list(
    target_date: Optional[date] = Query(None, description="Date for widget list (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get today's widget list from table DailyWidget."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.get_today_widget_list(user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to get today's widget list: {str(e)}")

@router.post("/widget/addtotoday/{widget_id}", response_model=AddWidgetToTodayResponse)
async def add_widget_to_today(
    widget_id: str,
    target_date: Optional[date] = Query(None, description="Date to add widget to (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Add a widget to today's list."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.add_widget_to_today(widget_id, user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to add widget to today: {str(e)}")

@router.delete("/widget/removefromtoday/{widget_id}", response_model=RemoveWidgetFromTodayResponse)
async def remove_widget_from_today(
    widget_id: str,
    target_date: Optional[date] = Query(None, description="Date to remove widget from (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Remove a widget from today's list."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.remove_widget_from_today(widget_id, user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to remove widget from today: {str(e)}")
```

### 4. Schemas (`/backend/schemas/`)

```python
# dashboard.py
"""
Dashboard schemas for request/response validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================
class TodayWidgetListResponse(BaseModel):
    """Response schema for today's widget list."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    widget_ids: List[str]
    widget_type: str
    priority: str
    reasoning: Optional[str]
    date: str  # ISO format
    is_active: bool

class AddWidgetToTodayResponse(BaseModel):
    """Response schema for adding widget to today."""
    success: bool
    message: str
    daily_widget_id: Optional[str] = None
    widget_ids: Optional[List[str]] = None

class RemoveWidgetFromTodayResponse(BaseModel):
    """Response schema for removing widget from today."""
    success: bool
    message: str
    daily_widget_id: Optional[str] = None
    remaining_widgets: Optional[List[str]] = None
```

## 🚀 Implementation Phases

### Phase 1: Core Models & Database ✅
- [x] Base model structure
- [ ] DailyWidget model (keep same fields as old backend)
- [ ] Update AlarmItemActivity model to include daily_widget_id
- [ ] Database migrations

### Phase 2: Services Layer 🔄
- [ ] DailyWidgetService (following new backend patterns)
- [ ] Add/remove widget functionality
- [ ] Get today's widget list functionality

### Phase 3: API Routes 🚧
- [ ] Dashboard routes (following new backend patterns)
- [ ] Integration with existing routes

### Phase 4: Testing & Integration 🚧
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end testing

## 🔧 Key Technical Decisions

### 1. Database Field Preservation ✅
- **Keep all existing fields** from old backend models
- **Add daily_widget_id to AlarmItemActivity** for proper relationships
- **Maintain same relationships** and foreign keys
- **Focus on code reorganization**, not schema changes

### 2. New Backend Patterns ✅
- **Async/await** for all database operations
- **Proper error handling** with custom error classes
- **Dependency injection** for database sessions
- **Pydantic validation** for all requests/responses
- **Consistent naming** and file structure

### 3. Service Architecture ✅
- **Single responsibility** for each service
- **Async methods** for all operations
- **Proper logging** and error handling
- **Type hints** for all methods

### 4. API Design ✅
- **RESTful conventions** following existing patterns
- **Consistent response formats**
- **Proper HTTP status codes**
- **Request/response validation**

## 📊 Migration Checklist

### Database Migration
- [ ] Create DailyWidget model in `/backend/models/` (keep same fields)
- [ ] Update AlarmItemActivity model to include daily_widget_id
- [ ] Set up database migrations
- [ ] Test data migration from old backend

### Service Migration
- [ ] Implement DailyWidgetService (async patterns)
- [ ] Add widget to today functionality
- [ ] Remove widget from today functionality
- [ ] Get today's widget list functionality

### API Migration
- [ ] Create dashboard routes (following existing patterns)
- [ ] Implement endpoint logic (async patterns)
- [ ] Add request/response validation (Pydantic)
- [ ] Test API endpoints

### Integration
- [ ] Update main.py to include new routes
- [ ] Integrate with existing services
- [ ] Update dependency injection
- [ ] Test end-to-end functionality

## 🎯 Success Criteria

1. **Feature Parity**: Core daily widget functionality works
2. **Database Compatibility**: Same fields and relationships preserved
3. **Performance**: API response times < 200ms
4. **Reliability**: 99% uptime with proper error handling
5. **Maintainability**: Clean, well-documented code following new patterns

## 📝 Notes

- **Focus on core functionality** - just add/remove and get today's widgets
- **Preserve all existing functionality** while improving code quality
- **Follow new backend patterns** for consistency
- **Maintain backward compatibility** with existing data
- **AI functionality will be added later** to avoid complexity

---

**Next Steps**: Start with Phase 1 (Core Models) and implement the DailyWidget model and update AlarmItemActivity. 