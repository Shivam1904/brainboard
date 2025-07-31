"""
Test script for Daily Widget API functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import httpx
import json
from datetime import date, datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/dashboard"
DEFAULT_USER_ID = "user_001"

# ============================================================================
# TEST FUNCTIONS
# ============================================================================
async def test_get_today_widget_list() -> bool:
    """Test getting today's widget list."""
    print("\n🧪 Testing GET /getTodayWidgetList")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with default date (today)
            response = await client.get(f"{BASE_URL}{API_PREFIX}/getTodayWidgetList")
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully retrieved today's widget list")
                print(f"📋 Found {len(data)} daily widget groups:")
                
                for i, daily_widget in enumerate(data, 1):
                    print(f"   {i}. ID: {daily_widget.get('id')}")
                    print(f"      Type: {daily_widget.get('widget_type')}")
                    print(f"      Priority: {daily_widget.get('priority')}")
                    print(f"      Widget IDs: {daily_widget.get('widget_ids')}")
                    print(f"      Active: {daily_widget.get('is_active')}")
                    print(f"      Date: {daily_widget.get('date')}")
                    print()
                
                return True
            else:
                print(f"❌ Failed to get today's widget list")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing get today widget list: {e}")
        return False

async def test_add_widget_to_today(widget_id: str) -> bool:
    """Test adding a widget to today's list."""
    print(f"\n🧪 Testing POST /widget/addtotoday/{widget_id}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{BASE_URL}{API_PREFIX}/widget/addtotoday/{widget_id}")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully added widget to today's list")
                print(f"📋 Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Failed to add widget to today's list")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing add widget to today: {e}")
        return False

async def test_remove_widget_from_today(widget_id: str) -> bool:
    """Test removing a widget from today's list."""
    print(f"\n🧪 Testing DELETE /widget/removefromtoday/{widget_id}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(f"{BASE_URL}{API_PREFIX}/widget/removefromtoday/{widget_id}")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully removed widget from today's list")
                print(f"📋 Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Failed to remove widget from today's list")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing remove widget from today: {e}")
        return False

async def test_add_duplicate_widget(widget_id: str) -> bool:
    """Test adding a widget that's already in today's list."""
    print(f"\n🧪 Testing duplicate widget addition: {widget_id}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First add the widget
            response1 = await client.post(f"{BASE_URL}{API_PREFIX}/widget/addtotoday/{widget_id}")
            
            if response1.status_code == 200:
                print(f"✅ First addition successful")
                
                # Try to add the same widget again
                response2 = await client.post(f"{BASE_URL}{API_PREFIX}/widget/addtotoday/{widget_id}")
                
                if response2.status_code == 200:
                    data = response2.json()
                    if not data.get('success', True):
                        print(f"✅ Correctly prevented duplicate widget addition")
                        print(f"📋 Response: {json.dumps(data, indent=2)}")
                        return True
                    else:
                        print(f"❌ Should have prevented duplicate widget addition")
                        return False
                else:
                    print(f"❌ Unexpected error on duplicate addition: {response2.status_code}")
                    return False
            else:
                print(f"❌ Failed to add widget initially: {response1.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing duplicate widget: {e}")
        return False

async def test_add_nonexistent_widget() -> bool:
    """Test adding a widget that doesn't exist."""
    print(f"\n🧪 Testing adding nonexistent widget")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            fake_widget_id = "nonexistent-widget-id-12345"
            response = await client.post(f"{BASE_URL}{API_PREFIX}/widget/addtotoday/{fake_widget_id}")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success', True):
                    print(f"✅ Correctly handled nonexistent widget")
                    print(f"📋 Response: {json.dumps(data, indent=2)}")
                    return True
                else:
                    print(f"❌ Should have failed for nonexistent widget")
                    return False
            else:
                print(f"❌ Unexpected error for nonexistent widget: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing nonexistent widget: {e}")
        return False

async def test_with_specific_date() -> bool:
    """Test API with a specific date parameter."""
    print(f"\n🧪 Testing with specific date parameter")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with a specific date
            test_date = "2024-01-15"
            response = await client.get(f"{BASE_URL}{API_PREFIX}/getTodayWidgetList?target_date={test_date}")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully retrieved widget list for {test_date}")
                print(f"📋 Found {len(data)} daily widget groups for {test_date}")
                return True
            else:
                print(f"❌ Failed to get widget list for specific date")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing with specific date: {e}")
        return False

async def get_available_widgets() -> List[str]:
    """Get available widget IDs for testing."""
    print("\n🔍 Getting available widgets for testing...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get widgets from the widgets API
            response = await client.get(f"{BASE_URL}/api/v1/widgets/")
            
            if response.status_code == 200:
                widgets = response.json()
                widget_ids = [widget.get('id') for widget in widgets if widget.get('id')]
                print(f"✅ Found {len(widget_ids)} available widgets: {widget_ids}")
                return widget_ids
            else:
                print(f"❌ Failed to get available widgets: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"❌ Error getting available widgets: {e}")
        return []

async def run_comprehensive_test():
    """Run comprehensive test suite for daily widget API."""
    print("🚀 Starting Daily Widget API Test Suite")
    print("=" * 50)
    
    # Track test results
    test_results = []
    
    # Test 1: Get today's widget list (should work even if empty)
    result1 = await test_get_today_widget_list()
    test_results.append(("Get Today Widget List", result1))
    
    # Test 2: Test with specific date
    result2 = await test_with_specific_date()
    test_results.append(("Test with Specific Date", result2))
    
    # Test 3: Test adding nonexistent widget
    result3 = await test_add_nonexistent_widget()
    test_results.append(("Add Nonexistent Widget", result3))
    
    # Test 4: Get available widgets for further testing
    available_widgets = await get_available_widgets()
    
    if available_widgets:
        # Test 5: Add a real widget to today's list
        result4 = await test_add_widget_to_today(available_widgets[0])
        test_results.append(("Add Widget to Today", result4))
        
        # Test 6: Test duplicate widget addition (use a different widget)
        if len(available_widgets) > 1:
            result5 = await test_add_duplicate_widget(available_widgets[1])
            test_results.append(("Test Duplicate Widget", result5))
        else:
            print("⚠️  Only one widget available, skipping duplicate test")
            test_results.append(("Test Duplicate Widget", True))
        
        # Test 7: Remove the widget from today's list
        result6 = await test_remove_widget_from_today(available_widgets[0])
        test_results.append(("Remove Widget from Today", result6))
        
        # Test 8: Get today's widget list again (should be empty or different)
        result7 = await test_get_today_widget_list()
        test_results.append(("Get Today Widget List (After Changes)", result7))
    else:
        print("⚠️  No widgets available for testing add/remove functionality")
        test_results.append(("Add/Remove Widget Tests", False))
    
    # Print test summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Daily Widget API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_comprehensive_test()) 