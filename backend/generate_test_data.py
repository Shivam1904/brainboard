#!/usr/bin/env python3
"""
Generate realistic test data for the backend.
"""
import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.base import Base
from models.dashboard_widget_details import DashboardWidgetDetails
from models.alarm_details import AlarmDetails
from models.alarm_item_activity import AlarmItemActivity
from db.engine import DATABASE_URL

async def generate_test_data():
    """Generate realistic test data."""
    print("🔧 Generating test data...")
    
    # Create engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # Clear existing data
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Generate DashboardWidgetDetails first (parent table)
        dashboard_widgets = []
        
        # Create some realistic widget configurations
        widget_configs = [
            {
                "user_id": "user_001",
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.8,
                "title": "Morning Wake Up",
                "category": "Health",
                "is_permanent": True
            },
            {
                "user_id": "user_001", 
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.6,
                "title": "Lunch Break",
                "category": "Work",
                "is_permanent": False
            },
            {
                "user_id": "user_001",
                "widget_type": "alarm", 
                "frequency": "daily",
                "importance": 0.9,
                "title": "Evening Exercise",
                "category": "Health",
                "is_permanent": True
            },
            {
                "user_id": "user_002",
                "widget_type": "alarm",
                "frequency": "daily", 
                "importance": 0.7,
                "title": "Team Standup",
                "category": "Work",
                "is_permanent": True
            }
        ]
        
        for config in widget_configs:
            widget = DashboardWidgetDetails(**config)
            dashboard_widgets.append(widget)
            session.add(widget)
        
        await session.commit()
        print(f"✅ Created {len(dashboard_widgets)} dashboard widgets")
        
        # Generate AlarmDetails (child of DashboardWidgetDetails)
        alarm_configs = [
            {
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "title": "Morning Wake Up",
                "description": "Time to start the day!",
                "alarm_times": ["07:00", "07:15"],
                "target_value": "Wake up early",
                "is_snoozable": True
            },
            {
                "widget_id": dashboard_widgets[1].id,  # Lunch Break
                "title": "Lunch Break",
                "description": "Take a break and eat lunch",
                "alarm_times": ["12:00", "12:30"],
                "target_value": "Healthy lunch",
                "is_snoozable": True
            },
            {
                "widget_id": dashboard_widgets[2].id,  # Evening Exercise
                "title": "Evening Exercise",
                "description": "Time for your daily workout",
                "alarm_times": ["18:00", "18:30"],
                "target_value": "30 min workout",
                "is_snoozable": False
            },
            {
                "widget_id": dashboard_widgets[3].id,  # Team Standup
                "title": "Team Standup",
                "description": "Daily team meeting",
                "alarm_times": ["09:00"],
                "target_value": "Attend meeting",
                "is_snoozable": False
            }
        ]
        
        alarm_details = []
        for config in alarm_configs:
            alarm = AlarmDetails(**config)
            alarm_details.append(alarm)
            session.add(alarm)
        
        await session.commit()
        print(f"✅ Created {len(alarm_details)} alarm details")
        
        # Generate AlarmItemActivity (child of both DashboardWidgetDetails and AlarmDetails)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        activity_configs = [
            # Today's activities
            {
                "widget_id": dashboard_widgets[0].id,
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(today, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(today, datetime.strptime("07:05", "%H:%M").time()),
                "snooze_until": datetime.combine(today, datetime.strptime("07:15", "%H:%M").time()),
                "snooze_count": 1
            },
            {
                "widget_id": dashboard_widgets[1].id,
                "alarmdetails_id": alarm_details[1].id,
                "started_at": datetime.combine(today, datetime.strptime("12:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0
            },
            # Yesterday's activities
            {
                "widget_id": dashboard_widgets[0].id,
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(yesterday, datetime.strptime("07:03", "%H:%M").time()),
                "snooze_until": datetime.combine(yesterday, datetime.strptime("07:10", "%H:%M").time()),
                "snooze_count": 2
            },
            {
                "widget_id": dashboard_widgets[2].id,
                "alarmdetails_id": alarm_details[2].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("18:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0
            }
        ]
        
        for config in activity_configs:
            activity = AlarmItemActivity(**config)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(activity_configs)} alarm activities")
    
    await engine.dispose()
    print("🎉 Test data generation complete!")
    print("\n📊 Generated data:")
    print(f"   - {len(dashboard_widgets)} dashboard widgets")
    print(f"   - {len(alarm_details)} alarm details") 
    print(f"   - {len(activity_configs)} alarm activities")
    print("\n🔗 All foreign key constraints satisfied!")

if __name__ == "__main__":
    asyncio.run(generate_test_data()) 