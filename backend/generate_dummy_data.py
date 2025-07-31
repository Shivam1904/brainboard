#!/usr/bin/env python3
"""
Generate realistic dummy data for the backend by directly inserting into all tables.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import json
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models.base import Base
from models.dashboard_widget_details import DashboardWidgetDetails
from models.alarm_details import AlarmDetails
from models.daily_widget import DailyWidget
from models.alarm_item_activity import AlarmItemActivity
from models.todo_details import TodoDetails
from models.todo_item_activity import TodoItemActivity
from db.engine import DATABASE_URL

# ============================================================================
# DATA GENERATION
# ============================================================================
async def generate_dummy_data():
    """Generate realistic dummy data for all tables."""
    print("🔧 Generating dummy data for all tables...")
    
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
        # ============================================================================
        # 1. GENERATE DASHBOARD_WIDGET_DETAILS (Parent table)
        # ============================================================================
        print("📊 Creating dashboard widgets...")
        dashboard_widgets = []
        
        widget_configs = [
            {
                "user_id": "user_001",
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.9,
                "title": "Morning Wake Up",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001", 
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.7,
                "title": "Lunch Break",
                "category": "Work",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "alarm", 
                "frequency": "daily",
                "importance": 0.8,
                "title": "Evening Exercise",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_002",
                "widget_type": "alarm",
                "frequency": "daily", 
                "importance": 0.6,
                "title": "Team Standup",
                "category": "Work",
                "is_permanent": True,
                "created_by": "user_002"
            },
            {
                "user_id": "user_001",
                "widget_type": "alarm",
                "frequency": "weekly",
                "importance": 0.5,
                "title": "Weekly Review",
                "category": "Productivity",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-task",
                "frequency": "daily",
                "importance": 0.8,
                "title": "Daily Tasks",
                "category": "Work",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-habit",
                "frequency": "daily",
                "importance": 0.7,
                "title": "Habits Tracker",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-event",
                "frequency": "weekly",
                "importance": 0.6,
                "title": "Weekly Events",
                "category": "Productivity",
                "is_permanent": False,
                "created_by": "user_001"
            }
        ]
        
        for config in widget_configs:
            widget = DashboardWidgetDetails(**config)
            dashboard_widgets.append(widget)
            session.add(widget)
        
        await session.commit()
        print(f"✅ Created {len(dashboard_widgets)} dashboard widgets")
        
        # ============================================================================
        # 2. GENERATE ALARM_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("⏰ Creating alarm details...")
        alarm_details = []
        
        alarm_configs = [
            {
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "title": "Morning Wake Up",
                "description": "Time to start the day!",
                "alarm_times": ["07:00", "07:15"],
                "target_value": "Wake up early",
                "is_snoozable": True,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[1].id,  # Lunch Break
                "title": "Lunch Break",
                "description": "Take a break and eat lunch",
                "alarm_times": ["12:00", "12:30"],
                "target_value": "Healthy lunch",
                "is_snoozable": True,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[2].id,  # Evening Exercise
                "title": "Evening Exercise",
                "description": "Time for your daily workout",
                "alarm_times": ["18:00", "18:30"],
                "target_value": "30 min workout",
                "is_snoozable": False,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[3].id,  # Team Standup
                "title": "Team Standup",
                "description": "Daily team meeting",
                "alarm_times": ["09:00"],
                "target_value": "Attend meeting",
                "is_snoozable": False,
                "created_by": "user_002"
            },
            {
                "widget_id": dashboard_widgets[4].id,  # Weekly Review
                "title": "Weekly Review",
                "description": "Review weekly progress and plan next week",
                "alarm_times": ["16:00"],
                "target_value": "Complete weekly review",
                "is_snoozable": True,
                "created_by": "user_001"
            }
        ]
        
        for config in alarm_configs:
            alarm = AlarmDetails(**config)
            alarm_details.append(alarm)
            session.add(alarm)
        
        await session.commit()
        print(f"✅ Created {len(alarm_details)} alarm details")
        
        # ============================================================================
        # 3. GENERATE TODO_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("📋 Creating todo details...")
        todo_details = []
        
        today = date.today()
        todo_configs = [
            {
                "widget_id": dashboard_widgets[5].id,  # Daily Tasks
                "title": "Daily Tasks",
                "todo_type": "todo-task",
                "description": "Complete daily work tasks",
                "due_date": today,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[6].id,  # Habits Tracker
                "title": "Habits Tracker",
                "todo_type": "todo-habit",
                "description": "Track daily habits and routines",
                "due_date": None,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[7].id,  # Weekly Events
                "title": "Weekly Events",
                "todo_type": "todo-event",
                "description": "Track weekly events and milestones",
                "due_date": today + timedelta(days=7),
                "created_by": "user_001"
            }
        ]
        
        for config in todo_configs:
            todo = TodoDetails(**config)
            todo_details.append(todo)
            session.add(todo)
        
        await session.commit()
        print(f"✅ Created {len(todo_details)} todo details")
        
        # ============================================================================
        # 4. GENERATE DAILY_WIDGETS (Daily widget selections)
        # ============================================================================
        print("📅 Creating daily widgets...")
        daily_widgets = []
        
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        daily_widget_configs = [
            # Today's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Lunch
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Important daily routines for health and work",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[2].id],  # Evening Exercise
                "widget_type": "alarm",
                "priority": "MEDIUM",
                "reasoning": "Daily exercise routine",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[5].id],  # Daily Tasks
                "widget_type": "todo-task",
                "priority": "HIGH",
                "reasoning": "Daily task management",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[6].id],  # Habits
                "widget_type": "todo-habit",
                "priority": "HIGH",
                "reasoning": "Daily habit tracking",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[7].id],  # Events
                "widget_type": "todo-event",
                "priority": "MEDIUM",
                "reasoning": "Weekly event tracking",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            # Yesterday's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Standup
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Daily morning routine and team meeting",
                "date": yesterday,
                "is_active": True,
                "created_by": "user_001"
            },
            # Tomorrow's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Weekly Review
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Morning routine and weekly planning",
                "date": tomorrow,
                "is_active": True,
                "created_by": "user_001"
            }
        ]
        
        for config in daily_widget_configs:
            daily_widget = DailyWidget(**config)
            daily_widgets.append(daily_widget)
            session.add(daily_widget)
        
        await session.commit()
        print(f"✅ Created {len(daily_widgets)} daily widgets")
        
        # ============================================================================
        # 5. GENERATE ALARM_ITEM_ACTIVITIES (Activity tracking)
        # ============================================================================
        print("📈 Creating alarm activities...")
        alarm_activities = []
        
        activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[0].id,  # Today's high priority group
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(today, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(today, datetime.strptime("07:05", "%H:%M").time()),
                "snooze_until": datetime.combine(today, datetime.strptime("07:15", "%H:%M").time()),
                "snooze_count": 1,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[0].id,  # Today's high priority group
                "widget_id": dashboard_widgets[1].id,  # Lunch Break
                "alarmdetails_id": alarm_details[1].id,
                "started_at": datetime.combine(today, datetime.strptime("12:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[1].id,  # Today's medium priority group
                "widget_id": dashboard_widgets[2].id,  # Evening Exercise
                "alarmdetails_id": alarm_details[2].id,
                "started_at": datetime.combine(today, datetime.strptime("18:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_001"
            },
            # Yesterday's activities
            {
                "daily_widget_id": daily_widgets[3].id,  # Yesterday's group
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(yesterday, datetime.strptime("07:03", "%H:%M").time()),
                "snooze_until": datetime.combine(yesterday, datetime.strptime("07:10", "%H:%M").time()),
                "snooze_count": 2,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[3].id,  # Yesterday's group
                "widget_id": dashboard_widgets[3].id,  # Team Standup
                "alarmdetails_id": alarm_details[3].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("09:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_002"
            }
        ]
        
        for config in activity_configs:
            activity = AlarmItemActivity(**config)
            alarm_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(alarm_activities)} alarm activities")
        
        # ============================================================================
        # 6. GENERATE TODO_ITEM_ACTIVITIES (Todo activity tracking)
        # ============================================================================
        print("📋 Creating todo activities...")
        todo_activities = []
        
        todo_activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[2].id,  # Today's todo-task group
                "widget_id": dashboard_widgets[5].id,  # Daily Tasks
                "tododetails_id": todo_details[0].id,
                "status": "in progress",
                "progress": 60,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[3].id,  # Today's todo-habit group
                "widget_id": dashboard_widgets[6].id,  # Habits Tracker
                "tododetails_id": todo_details[1].id,
                "status": "completed",
                "progress": 100,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[4].id,  # Today's todo-event group
                "widget_id": dashboard_widgets[7].id,  # Weekly Events
                "tododetails_id": todo_details[2].id,
                "status": "pending",
                "progress": 0,
                "created_by": "user_001"
            }
        ]
        
        for config in todo_activity_configs:
            activity = TodoItemActivity(**config)
            todo_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(todo_activities)} todo activities")
    
    await engine.dispose()
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n🎉 Dummy data generation complete!")
    print("=" * 50)
    print("📊 Generated data summary:")
    print(f"   📋 Dashboard Widgets: {len(dashboard_widgets)}")
    print(f"   ⏰ Alarm Details: {len(alarm_details)}")
    print(f"   📋 Todo Details: {len(todo_details)}")
    print(f"   📅 Daily Widgets: {len(daily_widgets)}")
    print(f"   📈 Alarm Activities: {len(alarm_activities)}")
    print(f"   📋 Todo Activities: {len(todo_activities)}")
    print("\n🔗 All foreign key relationships satisfied!")
    print("\n📅 Date ranges:")
    print(f"   - Yesterday: {yesterday}")
    print(f"   - Today: {today}")
    print(f"   - Tomorrow: {tomorrow}")
    print("\n👥 Users: user_001, user_002")
    print("🎯 Widget Types: alarm, todo-habit, todo-task, todo-event")
    print("📊 Categories: Health, Work, Productivity")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(generate_dummy_data()) 