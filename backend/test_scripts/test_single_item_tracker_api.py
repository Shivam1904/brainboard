#!/usr/bin/env python3
"""
Test script for SingleItemTracker API endpoints.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import json
import uuid
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from models.dashboard_widget_details import DashboardWidgetDetails
from models.single_item_tracker_details import SingleItemTrackerDetails
from models.single_item_tracker_item_activity import SingleItemTrackerItemActivity
from models.daily_widget import DailyWidget
from db.engine import DATABASE_URL
from services.single_item_tracker_service import SingleItemTrackerService

# ============================================================================
# TEST DATA
# ============================================================================
TEST_USER_ID = "test_user_001"
TEST_WIDGET_ID = str(uuid.uuid4())
TEST_TRACKER_DETAILS_ID = str(uuid.uuid4())
TEST_ACTIVITY_ID = str(uuid.uuid4())

# ============================================================================
# TEST FUNCTIONS
# ============================================================================
async def setup_test_data():
    """Set up test data in the database."""
    print("🔧 Setting up test data...")
    
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
        # Create test dashboard widget
        widget = DashboardWidgetDetails(
            id=TEST_WIDGET_ID,
            user_id=TEST_USER_ID,
            widget_type="singleitemtracker",
            frequency="daily",
            importance=0.8,
            title="Test Weight Tracker",
            category="Health",
            is_permanent=True,
            created_by=TEST_USER_ID
        )
        session.add(widget)
        
        # Create test tracker details
        tracker_details = SingleItemTrackerDetails(
            id=TEST_TRACKER_DETAILS_ID,
            widget_id=TEST_WIDGET_ID,
            title="Test Weight Tracker",
            value_type="decimal",
            value_unit="kg",
            target_value="70.0",
            created_by=TEST_USER_ID
        )
        session.add(tracker_details)
        
        # Create test daily widget
        daily_widget = DailyWidget(
            widget_ids=[TEST_WIDGET_ID],
            widget_type="singleitemtracker",
            priority="HIGH",
            reasoning="Test daily widget",
            date=date.today(),
            is_active=True,
            created_by=TEST_USER_ID
        )
        session.add(daily_widget)
        
        await session.commit()
        await session.refresh(daily_widget)
        
        # Create test activity
        activity = SingleItemTrackerItemActivity(
            id=TEST_ACTIVITY_ID,
            daily_widget_id=daily_widget.id,
            widget_id=TEST_WIDGET_ID,
            singleitemtrackerdetails_id=TEST_TRACKER_DETAILS_ID,
            value="72.5",
            time_added=datetime.now(),
            created_by=TEST_USER_ID
        )
        session.add(activity)
        
        await session.commit()
        print("✅ Test data created successfully")

async def test_get_tracker_details_and_activity():
    """Test getting tracker details and activity."""
    print("\n🧪 Testing getTrackerDetailsAndActivity...")
    
    # This would normally make an HTTP request to the API
    # For now, we'll simulate the service call
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        result = await service.get_tracker_details_and_activity(TEST_WIDGET_ID, TEST_USER_ID)
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response structure
        assert result.get("tracker_details") is not None
        assert result.get("activity") is not None
        assert result["tracker_details"]["widget_id"] == TEST_WIDGET_ID
        assert result["tracker_details"]["title"] == "Test Weight Tracker"
        assert result["tracker_details"]["value_type"] == "decimal"
        assert result["tracker_details"]["value_unit"] == "kg"
        assert result["tracker_details"]["target_value"] == "70.0"
        
        print("✅ getTrackerDetailsAndActivity test passed")

async def test_update_activity():
    """Test updating tracker activity."""
    print("\n🧪 Testing updateActivity...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        
        # Test updating activity
        update_data = {
            "value": "71.2",
            "time_added": datetime.now()
        }
        
        result = await service.update_activity(TEST_ACTIVITY_ID, TEST_USER_ID, update_data)
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response
        assert result.get("success") is True
        assert result.get("activity") is not None
        assert result["activity"]["value"] == "71.2"
        
        print("✅ updateActivity test passed")

async def test_get_tracker_details():
    """Test getting tracker details."""
    print("\n🧪 Testing getTrackerDetails...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        result = await service.get_tracker_details(TEST_WIDGET_ID, TEST_USER_ID)
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response
        assert result.get("tracker_details") is not None
        assert result["tracker_details"]["widget_id"] == TEST_WIDGET_ID
        assert result["tracker_details"]["title"] == "Test Weight Tracker"
        
        print("✅ getTrackerDetails test passed")

async def test_update_tracker_details():
    """Test updating tracker details."""
    print("\n🧪 Testing updateDetails...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        
        # Test updating tracker details
        update_data = {
            "title": "Updated Weight Tracker",
            "target_value": "68.0"
        }
        
        result = await service.update_tracker_details(TEST_TRACKER_DETAILS_ID, TEST_USER_ID, update_data)
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response
        assert result.get("success") is True
        assert result.get("tracker_details") is not None
        assert result["tracker_details"]["title"] == "Updated Weight Tracker"
        assert result["tracker_details"]["target_value"] == "68.0"
        
        print("✅ updateDetails test passed")

async def test_get_user_trackers():
    """Test getting user trackers."""
    print("\n🧪 Testing getUserTrackers...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        result = await service.get_user_trackers(TEST_USER_ID)
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response
        assert result.get("trackers") is not None
        assert len(result["trackers"]) > 0
        assert result["trackers"][0]["widget_id"] == TEST_WIDGET_ID
        
        print("✅ getUserTrackers test passed")

async def test_create_tracker_details():
    """Test creating tracker details."""
    print("\n🧪 Testing createTrackerDetails...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        
        # Test creating new tracker details
        new_widget_id = str(uuid.uuid4())
        result = await service.create_tracker_details(
            widget_id=new_widget_id,
            title="New Steps Tracker",
            value_type="number",
            value_unit="steps",
            target_value="8000",
            user_id=TEST_USER_ID
        )
        
        print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
        
        # Verify the response
        assert result.get("success") is True
        assert result.get("tracker_details") is not None
        assert result["tracker_details"]["title"] == "New Steps Tracker"
        assert result["tracker_details"]["value_type"] == "number"
        assert result["tracker_details"]["value_unit"] == "steps"
        assert result["tracker_details"]["target_value"] == "8000"
        
        print("✅ createTrackerDetails test passed")

async def test_create_tracker_activity_for_today():
    """Test creating tracker activity for today."""
    print("\n🧪 Testing createTrackerActivityForToday...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        service = SingleItemTrackerService(session)
        
        # Get daily widget ID
        stmt = text("SELECT id FROM daily_widgets LIMIT 1")
        result = await session.execute(stmt)
        daily_widget_id = result.scalar()
        
        if daily_widget_id:
            result = await service.create_tracker_activity_for_today(
                daily_widget_id=daily_widget_id,
                widget_id=TEST_WIDGET_ID,
                user_id=TEST_USER_ID
            )
            
            print(f"✅ Result: {json.dumps(result, default=str, indent=2)}")
            
            # Verify the response
            assert result is not None
            assert result["widget_id"] == TEST_WIDGET_ID
            assert result["singleitemtrackerdetails_id"] == TEST_TRACKER_DETAILS_ID
            
            print("✅ createTrackerActivityForToday test passed")
        else:
            print("⚠️ No daily widget found, skipping test")

async def test_update_or_create_tracker_details():
    """Test update_or_create_tracker_details method."""
    print("\n=== Testing update_or_create_tracker_details ===")
    
    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # Get a test widget ID
        stmt = text("SELECT id FROM dashboard_widget_details WHERE widget_type = 'singleitemtracker' LIMIT 1")
        result = await session.execute(stmt)
        widget_id = result.scalar()
        
        if not widget_id:
            print("❌ No singleitemtracker widget found for testing")
            return
        
        service = SingleItemTrackerService(session)
        
        # Test creating new tracker details
        print(f"Testing creation for widget: {widget_id}")
        result = await service.update_or_create_tracker_details(
            widget_id=widget_id,
            title="Test Weight Tracker",
            value_type="number",
            value_unit="kg",
            target_value="75",
            user_id=TEST_USER_ID
        )
        
        print(f"Result: {result}")
        assert result["success"] == True
        assert result["action"] == "updated" or "tracker_details" in result
        print("✅ update_or_create_tracker_details test passed")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_all_tests():
    """Run all SingleItemTracker tests."""
    print("🚀 Starting SingleItemTracker API Tests")
    print("=" * 50)
    
    try:
        # Setup test data
        await setup_test_data()
        
        # Run all tests
        await test_get_tracker_details_and_activity()
        await test_update_activity()
        await test_get_tracker_details()
        await test_update_tracker_details()
        await test_get_user_trackers()
        await test_create_tracker_details()
        await test_create_tracker_activity_for_today()
        await test_update_or_create_tracker_details()  # Added new test
        
        print("\n" + "=" * 50)
        print("🎉 All SingleItemTracker tests passed successfully!")
        print("✅ SingleItemTracker migration is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 