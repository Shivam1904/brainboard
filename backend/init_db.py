#!/usr/bin/env python3
"""
Database initialization script.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models.base import Base
from models.alarm_details import AlarmDetails
from models.alarm_item_activity import AlarmItemActivity
from models.dashboard_widget_details import DashboardWidgetDetails
from db.engine import DATABASE_URL

async def init_database():
    """Initialize the database with all tables."""
    print("🔧 Initializing database...")
    
    # Create engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Show SQL queries
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully!")
    print(f"📊 Created tables:")
    print(f"   - {DashboardWidgetDetails.__tablename__}")
    print(f"   - {AlarmDetails.__tablename__}")
    print(f"   - {AlarmItemActivity.__tablename__}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database()) 