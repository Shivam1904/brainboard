#!/usr/bin/env python3
"""
Simple dummy data generator using the create_widget function.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from models.base import Base
from db.engine import DATABASE_URL
from db.session import AsyncSessionLocal
from services.widget_service import WidgetService
from schemas.widget import CreateWidgetRequest, WidgetType, Frequency

# Widget configurations
WIDGET_CONFIGS = [
    {
        "widget_type": WidgetType.ALARM,
        "frequency": Frequency.DAILY,
        "importance": 0.9,
        "title": "Morning Wake Up",
        "category": "Health",
        "alarm_time": "07:00"
    },
    {
        "widget_type": WidgetType.TODO_EVENT,
        "frequency": Frequency.WEEKLY,
        "importance": 0.9,
        "title": "Go for a run with Tam",
        "category": "Health",
        "description": "Weekly running session with Tam"
    },
    {
        "widget_type": WidgetType.SINGLEITEMTRACKER,
        "frequency": Frequency.DAILY,
        "importance": 0.1,
        "title": "Weight Tracking",
        "category": "Health",
        "value_type": "number",
        "value_unit": "kg",
        "target_value": "65"
    },
    {
        "widget_type": WidgetType.ALARM,
        "frequency": Frequency.DAILY,
        "importance": 0.7,
        "title": "Lunch Break",
        "category": "Work",
        "alarm_time": "12:00"
    },
    {
        "widget_type": WidgetType.TODO_TASK,
        "frequency": Frequency.DAILY,
        "importance": 0.8,
        "title": "Daily Tasks",
        "category": "Work",
        "description": "Complete daily work tasks"
    },
    {
        "widget_type": WidgetType.WEBSEARCH,
        "frequency": Frequency.DAILY,
        "importance": 0.7,
        "title": "AI Trends 2024",
        "category": "Research"
    }
]

async def init_database():
    """Initialize the database with all tables."""
    print("🔧 Initializing database...")
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database initialized!")

async def generate_dummy_data():
    """Generate dummy data using the create_widget function."""
    print("🔧 Generating dummy data...")
    
    async with AsyncSessionLocal() as db:
        service = WidgetService(db)
        user_id = "user_001"
        
        for i, config in enumerate(WIDGET_CONFIGS, 1):
            print(f"Creating widget {i}/{len(WIDGET_CONFIGS)}: {config['title']}")
            
            try:
                request = CreateWidgetRequest(**config)
                result = await service.create_widget(request, user_id)
                print(f"✅ Created: {result.title} (ID: {result.widget_id})")
            except Exception as e:
                print(f"❌ Failed: {config['title']} - {str(e)}")
    
    print(f"\n🎉 Generated {len(WIDGET_CONFIGS)} widgets!")

async def main():
    """Main function that initializes DB and generates data."""
    await init_database()
    await generate_dummy_data()

if __name__ == "__main__":
    asyncio.run(main()) 