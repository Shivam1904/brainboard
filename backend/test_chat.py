"""
Test script for AI chat functionality with database verification.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from orchestrators.chat_orchestrator import ChatOrchestrator
from services.alarm_service import AlarmService
from models.alarm_details import AlarmDetails
from models.dashboard_widget_details import DashboardWidgetDetails
from sqlalchemy import select
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# TEST FUNCTIONS
# ============================================================================
async def verify_alarm_creation_via_api(user_id: str, expected_title: str, expected_times: list) -> bool:
    """Verify that an alarm was actually created by calling the API."""
    try:
        import httpx
        import json
        
        # Call the alarm API to get user's alarms
        async with httpx.AsyncClient(timeout=5.0) as client:
            # First, try to get alarms via the alarm API endpoint
            try:
                response = await client.get(f"http://localhost:8000/api/v1/alarms/user/{user_id}")
                if response.status_code == 200:
                    alarms_data = response.json()
                    print(f"🔍 Found {len(alarms_data.get('alarms', []))} alarms via API for user {user_id}:")
                    for alarm in alarms_data.get('alarms', []):
                        print(f"   - Title: '{alarm.get('title')}', Times: {alarm.get('alarm_times')}")
                    
                    # Check if our expected alarm exists
                    for alarm in alarms_data.get('alarms', []):
                        if (alarm.get('title', '').lower() == expected_title.lower() and 
                            alarm.get('alarm_times') == expected_times):
                            print(f"✅ Alarm verified via API:")
                            print(f"   - ID: {alarm.get('id')}")
                            print(f"   - Title: {alarm.get('title')}")
                            print(f"   - Times: {alarm.get('alarm_times')}")
                            return True
                    
                    print(f"❌ Alarm with title '{expected_title}' and times {expected_times} not found via API")
                    return False
                    
            except Exception as api_error:
                print(f"⚠️  API call failed: {api_error}")
                print("   Falling back to database verification...")
                
                # Fallback to database verification if API is not available
                return await verify_alarm_creation_db(user_id, expected_title, expected_times)
        
    except Exception as e:
        print(f"❌ Error verifying alarm via API: {e}")
        return False

async def verify_alarm_creation_db(user_id: str, expected_title: str, expected_times: list) -> bool:
    """Fallback: Verify that an alarm was actually created in the database."""
    try:
        async for db_session in get_session():
            # Get all alarms for the user and show them
            stmt = select(AlarmDetails).join(DashboardWidgetDetails).where(
                DashboardWidgetDetails.user_id == user_id
            ).order_by(AlarmDetails.created_at.desc())
            result = await db_session.execute(stmt)
            all_alarms = result.scalars().all()
            
            print(f"🔍 Found {len(all_alarms)} alarms in database for user {user_id}:")
            for alarm in all_alarms:
                print(f"   - Title: '{alarm.title}', Times: {alarm.alarm_times}, Created: {alarm.created_at}")
            
            # Look for the most recently created alarm that matches our criteria
            for alarm in all_alarms:
                if (alarm.title.lower() == expected_title.lower() and 
                    alarm.alarm_times == expected_times):
                    print(f"✅ Alarm verified in database:")
                    print(f"   - ID: {alarm.id}")
                    print(f"   - Title: {alarm.title}")
                    print(f"   - Times: {alarm.alarm_times}")
                    print(f"   - Widget ID: {alarm.widget_id}")
                    print(f"   - Created: {alarm.created_at}")
                    return True
            
            print(f"❌ Alarm with title '{expected_title}' and times {expected_times} not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying alarm in database: {e}")
        return False

async def cleanup_test_alarms(db_session: AsyncSession, user_id: str):
    """Clean up test alarms from the database."""
    try:
        # Delete alarm details for test user
        stmt = select(AlarmDetails).join(DashboardWidgetDetails).where(
            DashboardWidgetDetails.user_id == user_id
        )
        result = await db_session.execute(stmt)
        test_alarms = result.scalars().all()
        
        for alarm in test_alarms:
            await db_session.delete(alarm)
        
        # Delete widget details for test user
        stmt = select(DashboardWidgetDetails).where(
            DashboardWidgetDetails.user_id == user_id
        )
        result = await db_session.execute(stmt)
        test_widgets = result.scalars().all()
        
        for widget in test_widgets:
            await db_session.delete(widget)
        
        await db_session.commit()
        print(f"🧹 Cleaned up {len(test_alarms)} test alarms and {len(test_widgets)} test widgets")
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")

async def test_chat_functionality():
    """Test the chat functionality with real AI calls and database verification."""
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return
    
    print("🧪 Testing AI Chat Functionality with Real AI and Database Verification")
    print("=" * 70)
    
    # Test user ID
    test_user_id = "test_user_001"
    
    # Clean up any existing test data
    async for db_session in get_session():
        await cleanup_test_alarms(db_session, test_user_id)
        break
    
    # Test scenarios - starting with single-shot commands only
    test_scenarios = [
        {
            "name": "Single Shot - Complete Information",
            "messages": ["Set an alarm for 7 AM called Wake up"],
            "expected_title": "Wake up",
            "expected_times": ["07:00"],
            "test_type": "single_shot"
        },
        {
            "name": "Single Shot - Different Time",
            "messages": ["Create an alarm for 8:30 AM named Morning Alarm"],
            "expected_title": "Morning Alarm",
            "expected_times": ["08:30"],
            "test_type": "single_shot"
        },
        {
            "name": "Single Shot - With Description",
            "messages": ["Set an alarm for 6 AM called Gym with description Workout reminder"],
            "expected_title": "Gym",
            "expected_times": ["06:00"],
            "test_type": "single_shot"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        print("-" * 50)
        
        # Clean up before each test to ensure fresh state
        async for db_session in get_session():
            await cleanup_test_alarms(db_session, test_user_id)
            break
        
        # For single-shot tests, we expect one message to complete the task
        message = scenario["messages"][0]  # Single message for single-shot
        print(f"User: {message}")
        
        try:
            # Get a fresh database session for each test
            async for db_session in get_session():
                # Create orchestrator with real database session
                orchestrator = ChatOrchestrator(db_session)
                
                # Process the single message
                result = await orchestrator.process_message(
                    user_message=message,
                    user_id=test_user_id,
                    session_id=None  # No session for single-shot
                )
                
                print(f"AI: {result['message']}")
                print(f"Session: {result['session_id']}")
                print(f"Complete: {result['is_complete']}")
                print(f"Intent: {result.get('intent')}")
                
                if result.get('missing_parameters'):
                    print(f"Missing: {result['missing_parameters']}")
                    print(f"❌ SINGLE-SHOT FAILED - Missing parameters in complete command")
                
                # For single-shot, we expect immediate completion
                if result['is_complete'] and result.get('success'):
                    print(f"\n🔍 Verifying alarm creation via API...")
                    print(f"   Expected title: '{scenario['expected_title']}'")
                    print(f"   Expected times: {scenario['expected_times']}")
                    print(f"   AI success: {result.get('success')}")
                    print(f"   Created resource: {result.get('created_resource')}")
                    print(f"   Test type: {scenario['test_type']}")
                    
                    # Commit any pending transactions
                    await db_session.commit()
                    
                    # Verify the alarm was actually created via API
                    verification_success = await verify_alarm_creation_via_api(
                        test_user_id, 
                        scenario["expected_title"], 
                        scenario["expected_times"]
                    )
                    
                    if verification_success:
                        print("✅ SINGLE-SHOT SUCCESS - Alarm created and verified!")
                    else:
                        print("❌ SINGLE-SHOT FAILED - Alarm creation verification failed!")
                        
                elif result['is_complete']:
                    print(f"\n❌ SINGLE-SHOT FAILED - Conversation complete but not successful:")
                    print(f"   Success: {result.get('success')}")
                    print(f"   Error: {result.get('error')}")
                    print(f"   Test type: {scenario['test_type']}")
                else:
                    print(f"\n❌ SINGLE-SHOT FAILED - Conversation not complete:")
                    print(f"   Complete: {result['is_complete']}")
                    print(f"   Missing parameters: {result.get('missing_parameters', [])}")
                    print(f"   Test type: {scenario['test_type']}")
                
                break  # Exit the async for loop
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("This might be due to:")
            print("1. Invalid OpenAI API key")
            print("2. Network connectivity issues")
            print("3. Database connection issues")
            print("4. OpenAI API rate limits")
        
        print()

def test_architecture():
    """Test the architecture components."""
    print("\n🏗️  Testing Architecture Components")
    print("=" * 50)
    
    try:
        # Test imports
        from ai_engine.models.llm_client import LLMClient
        from ai_engine.models.session_memory import SessionMemory
        from ai_engine.models.intent_models import IntentResponse
        from ai_engine.tools.base_tool import BaseTool
        from ai_engine.tools.alarm_tool import AlarmTool
        from ai_engine.tools.tool_registry import ToolRegistry
        from services.ai_service import AIService
        from services.intent_service import IntentService
        from services.session_service import SessionService
        from orchestrators.chat_orchestrator import ChatOrchestrator
        from schemas.chat import ChatRequest, ChatResponse
        
        print("✅ All imports successful")
        
        # Test session memory
        session = SessionMemory(user_id="test_user")
        print(f"✅ Session memory created: {session.session_id}")
        
        # Test intent response
        intent_response = IntentResponse(
            intent="create_alarm",
            confidence=0.95,
            parameters={"title": "Test", "alarm_times": ["07:00"]},
            reasoning="Test reasoning"
        )
        print(f"✅ Intent response created: {intent_response.intent}")
        
        print("\n🎉 All architecture components working correctly!")
        
    except Exception as e:
        print(f"❌ Architecture test failed: {e}")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("🚀 Starting AI Chat Tests with Database Verification")
    print("=" * 60)
    
    # Test architecture first
    test_architecture()
    
    # Test chat functionality with verification
    asyncio.run(test_chat_functionality())
    
    print("\n✨ Tests completed!") 