#!/usr/bin/env python3
"""
Test Data Insertion Script for New Schema
This script creates test data for the restructured backend.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db, init_db
from models.database import (
    User, DashboardWidgetDetails, ToDoDetails, SingleItemTrackerDetails,
    WebSearchDetails, AlarmDetails
)
from datetime import datetime, date
import uuid

def create_test_data():
    """Create test data for the new schema"""
    
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if default user exists
        user = db.query(User).filter(User.email == "default@brainboard.com").first()
        if not user:
            # Create default user
            user = User(
                id="u1",
                email="default@brainboard.com",
                name="Default User",
                created_by="system"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("✅ Created default user")
        else:
            print("✅ Default user already exists")
        
        # Check if widgets already exist
        existing_widgets = db.query(DashboardWidgetDetails).filter(
            DashboardWidgetDetails.user_id == user.id
        ).count()
        
        if existing_widgets > 0:
            print(f"✅ {existing_widgets} widgets already exist, skipping widget creation")
            return
        
        # Create dashboard widgets (as per your example)
        widgets_data = [
            {
                "id": "id0", "widget_type": "todo-task", "frequency": "weekly", 
                "importance": 0.9, "title": "AWS", "category": "Job"
            },
            {
                "id": "id1", "widget_type": "todo-event", "frequency": "daily", 
                "importance": 0.5, "title": "Meditation", "category": "Health"
            },
            {
                "id": "id2", "widget_type": "todo-habit", "frequency": "daily", 
                "importance": 1.0, "title": "Gym", "category": "Health"
            },
            {
                "id": "id3", "widget_type": "todo-habit", "frequency": "daily", 
                "importance": 1.0, "title": "Take meds", "category": "Health"
            },
            {
                "id": "id4", "widget_type": "alarm", "frequency": "daily", 
                "importance": 1.0, "title": "Gym Alarm", "category": "Health"
            },
            {
                "id": "id5", "widget_type": "singleitemtracker", "frequency": "daily", 
                "importance": 0.5, "title": "Weight Tracker", "category": "Health"
            },
            {
                "id": "id6", "widget_type": "websearch", "frequency": "daily", 
                "importance": 1.0, "title": "YC funded AI companies", "category": "Productivity"
            }
        ]
        
        # Create dashboard widgets
        for widget_data in widgets_data:
            widget = DashboardWidgetDetails(
                id=widget_data["id"],
                user_id=user.id,
                widget_type=widget_data["widget_type"],
                frequency=widget_data["frequency"],
                importance=widget_data["importance"],
                title=widget_data["title"],
                category=widget_data["category"],
                created_by=user.id
            )
            db.add(widget)
        
        db.commit()
        print(f"✅ Created {len(widgets_data)} dashboard widgets")
        
        # Create todo details
        todo_details_data = [
            {"widget_id": "id0", "title": "AWS", "todo_type": "task"},
            {"widget_id": "id1", "title": "Meditation", "todo_type": "event"},
            {"widget_id": "id2", "title": "Gym", "todo_type": "habit"},
            {"widget_id": "id3", "title": "Take meds", "todo_type": "habit"}
        ]
        
        for todo_data in todo_details_data:
            todo_detail = ToDoDetails(
                widget_id=todo_data["widget_id"],
                title=todo_data["title"],
                todo_type=todo_data["todo_type"],
                created_by=user.id
            )
            db.add(todo_detail)
        
        # Create single item tracker details
        tracker_detail = SingleItemTrackerDetails(
            widget_id="id5",
            title="Weight Tracker",
            value_type="number",
            value_unit="kg",
            target_value="59",
            created_by=user.id
        )
        db.add(tracker_detail)
        
        # Create websearch details
        websearch_detail = WebSearchDetails(
            widget_id="id6",
            title="YC funded AI companies",
            created_by=user.id
        )
        db.add(websearch_detail)
        
        # Create alarm details
        alarm_detail = AlarmDetails(
            widget_id="id4",
            title="Gym Alarm",
            description="Morning gym reminder",
            alarm_times=["06:00", "18:00"],
            is_snoozable=True,
            created_by=user.id
        )
        db.add(alarm_detail)
        
        db.commit()
        
        print("✅ Test data created successfully!")
        print(f"📝 Created {len(todo_details_data)} todo details")
        print(f"⚖️ Created 1 single item tracker")
        print(f"🔍 Created 1 websearch detail")
        print(f"⏰ Created 1 alarm detail")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 