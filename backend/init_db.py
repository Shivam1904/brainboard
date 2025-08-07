#!/usr/bin/env python3
"""
Database initialization script for consolidated JSON schema.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models.base import Base
from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widget import DailyWidget
from models.daily_widgets_ai_output import DailyWidgetsAIOutput
from models.websearch_summary_ai_output import WebSearchSummaryAIOutput
from db.engine import DATABASE_URL

async def init_database():
    """Initialize the database with consolidated JSON schema."""
    print("🔧 Initializing database with consolidated JSON schema...")
    
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
    print(f"   - {DashboardWidgetDetails.__tablename__} (consolidated widget configurations)")
    print(f"   - {DailyWidget.__tablename__} (consolidated daily activities)")
    print(f"   - {DailyWidgetsAIOutput.__tablename__} (AI outputs)")
    print(f"   - {WebSearchSummaryAIOutput.__tablename__} (web search summaries)")
    print()
    print("🎉 Benefits of new schema:")
    print("   - Only 2 main tables instead of 10+")
    print("   - JSON columns for flexible data storage")
    print("   - MongoDB-ready document structure")
    print("   - Easy to add new widget types")
    print("   - No null fields, better storage efficiency")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database()) 