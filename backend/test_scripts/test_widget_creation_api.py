"""
Comprehensive Widget Creation API Test Suite
Tests both service methods and actual HTTP endpoints for complete validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import sys
import os
import json
import httpx
from datetime import datetime, date
from typing import Dict, Any, Optional

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from services.widget_service import WidgetService
from schemas.widget import CreateWidgetRequest, WidgetType, Frequency

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_USER_ID = "user_001"

# Test data for different widget types
TEST_WIDGET_DATA = {
    "alarm": {
        "widget_type": WidgetType.ALARM,
        "frequency": Frequency.DAILY,
        "importance": 0.9,
        "title": "Morning Alarm",
        "category": "health",
        "alarm_time": "08:00"
    },
    "todo_task": {
        "widget_type": WidgetType.TODO_TASK,
        "frequency": Frequency.DAILY,
        "importance": 0.8,
        "title": "Complete Project",
        "category": "work",
        "description": "Finish the project documentation"
    },
    "singleitemtracker": {
        "widget_type": WidgetType.SINGLEITEMTRACKER,
        "frequency": Frequency.DAILY,
        "importance": 0.7,
        "title": "Weight Tracker",
        "category": "health",
        "value_type": "decimal",
        "value_unit": "kg",
        "target_value": "70.0"
    }
}

# ============================================================================
# TEST DATA
# ============================================================================
class TestData:
    """Test data and state management."""
    
    def __init__(self):
        self.created_widgets: Dict[str, str] = {}  # widget_type -> widget_id
    
    def reset(self):
        """Reset all test data."""
        self.created_widgets = {}

test_data = TestData()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
async def make_api_request(
    method: str, 
    endpoint: str, 
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make HTTP API request and return response."""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else None,
                "headers": dict(response.headers)
            }
        except httpx.RequestError as e:
            return {
                "status_code": 0,
                "error": f"Request failed: {str(e)}",
                "data": None
            }

def validate_response_structure(response: Dict, expected_fields: list) -> bool:
    """Validate that response contains expected fields."""
    if not response.get("data"):
        return False
    
    data = response["data"]
    for field in expected_fields:
        if field not in data:
            return False
    return True

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

# ============================================================================
# SERVICE METHOD TESTS (Unit Tests)
# ============================================================================
async def test_service_alarm_widget_creation() -> bool:
    """Test alarm widget creation via service method."""
    print("\n🔧 Testing Alarm Widget Creation (Service)...")
    
    try:
        async with AsyncSessionLocal() as db:
            widget_service = WidgetService(db)
            create_request = CreateWidgetRequest(**TEST_WIDGET_DATA["alarm"])
            result = await widget_service.create_widget(create_request, TEST_USER_ID)
            
            # Validate response
            assert result.success == True, "Widget creation should succeed"
            assert result.widget_id is not None, "Widget ID should be generated"
            assert result.widget_type == "alarm", "Widget type should be alarm"
            
            # Store for later tests
            test_data.created_widgets["alarm"] = result.widget_id
            
            print_test_result("Alarm Widget Creation", True, f"Widget ID: {result.widget_id}")
            return True
            
    except Exception as e:
        print_test_result("Alarm Widget Creation", False, str(e))
        return False

async def test_service_todo_widget_creation() -> bool:
    """Test todo widget creation via service method."""
    print("\n🔧 Testing Todo Widget Creation (Service)...")
    
    try:
        async with AsyncSessionLocal() as db:
            widget_service = WidgetService(db)
            create_request = CreateWidgetRequest(**TEST_WIDGET_DATA["todo_task"])
            result = await widget_service.create_widget(create_request, TEST_USER_ID)
            
            # Validate response
            assert result.success == True, "Widget creation should succeed"
            assert result.widget_id is not None, "Widget ID should be generated"
            assert result.widget_type == "todo-task", "Widget type should be todo-task"
            
            # Store for later tests
            test_data.created_widgets["todo_task"] = result.widget_id
            
            print_test_result("Todo Widget Creation", True, f"Widget ID: {result.widget_id}")
            return True
            
    except Exception as e:
        print_test_result("Todo Widget Creation", False, str(e))
        return False

async def test_service_tracker_widget_creation() -> bool:
    """Test tracker widget creation via service method."""
    print("\n🔧 Testing Tracker Widget Creation (Service)...")
    
    try:
        async with AsyncSessionLocal() as db:
            widget_service = WidgetService(db)
            create_request = CreateWidgetRequest(**TEST_WIDGET_DATA["singleitemtracker"])
            result = await widget_service.create_widget(create_request, TEST_USER_ID)
            
            # Validate response
            assert result.success == True, "Widget creation should succeed"
            assert result.widget_id is not None, "Widget ID should be generated"
            assert result.widget_type == "singleitemtracker", "Widget type should be singleitemtracker"
            
            # Store for later tests
            test_data.created_widgets["singleitemtracker"] = result.widget_id
            
            print_test_result("Tracker Widget Creation", True, f"Widget ID: {result.widget_id}")
            return True
            
    except Exception as e:
        print_test_result("Tracker Widget Creation", False, str(e))
        return False

# ============================================================================
# HTTP API ENDPOINT TESTS (Integration Tests)
# ============================================================================
async def test_api_alarm_widget_creation() -> bool:
    """Test alarm widget creation via HTTP API."""
    print("\n🌐 Testing Alarm Widget Creation (HTTP API)...")
    
    try:
        # Create widget via API
        response = await make_api_request("POST", "/widgets/create", TEST_WIDGET_DATA["alarm"])
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "widget_id", "widget_type"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Widget creation should succeed"
        assert data["widget_type"] == "alarm", "Widget type should be alarm"
        
        # Store for later tests
        test_data.created_widgets["alarm_api"] = data["widget_id"]
        
        print_test_result("Alarm Widget Creation (API)", True, f"Widget ID: {data['widget_id']}")
        return True
        
    except Exception as e:
        print_test_result("Alarm Widget Creation (API)", False, str(e))
        return False

async def test_api_todo_widget_creation() -> bool:
    """Test todo widget creation via HTTP API."""
    print("\n🌐 Testing Todo Widget Creation (HTTP API)...")
    
    try:
        # Create widget via API
        response = await make_api_request("POST", "/widgets/create", TEST_WIDGET_DATA["todo_task"])
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "widget_id", "widget_type"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Widget creation should succeed"
        assert data["widget_type"] == "todo-task", "Widget type should be todo-task"
        
        # Store for later tests
        test_data.created_widgets["todo_task_api"] = data["widget_id"]
        
        print_test_result("Todo Widget Creation (API)", True, f"Widget ID: {data['widget_id']}")
        return True
        
    except Exception as e:
        print_test_result("Todo Widget Creation (API)", False, str(e))
        return False

async def test_api_tracker_widget_creation() -> bool:
    """Test tracker widget creation via HTTP API."""
    print("\n🌐 Testing Tracker Widget Creation (HTTP API)...")
    
    try:
        # Create widget via API
        response = await make_api_request("POST", "/widgets/create", TEST_WIDGET_DATA["singleitemtracker"])
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "widget_id", "widget_type"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Widget creation should succeed"
        assert data["widget_type"] == "singleitemtracker", "Widget type should be singleitemtracker"
        
        # Store for later tests
        test_data.created_widgets["singleitemtracker_api"] = data["widget_id"]
        
        print_test_result("Tracker Widget Creation (API)", True, f"Widget ID: {data['widget_id']}")
        return True
        
    except Exception as e:
        print_test_result("Tracker Widget Creation (API)", False, str(e))
        return False

async def test_api_get_all_widgets() -> bool:
    """Test getting all widgets via HTTP API."""
    print("\n🌐 Testing Get All Widgets (HTTP API)...")
    
    try:
        # Get all widgets via API
        response = await make_api_request("GET", "/widgets/getAllWidgetList")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        data = response["data"]
        assert isinstance(data, list), "Response should be a list of widgets"
        
        # Check if our created widgets are in the list
        created_widget_ids = list(test_data.created_widgets.values())
        found_widgets = [w for w in data if w.get("id") in created_widget_ids]
        
        assert len(found_widgets) > 0, "Should find at least one created widget"
        
        print_test_result("Get All Widgets (API)", True, f"Found {len(found_widgets)} created widgets")
        return True
        
    except Exception as e:
        print_test_result("Get All Widgets (API)", False, str(e))
        return False

async def test_api_get_today_widgets() -> bool:
    """Test getting today's widgets via HTTP API."""
    print("\n🌐 Testing Get Today Widgets (HTTP API)...")
    
    try:
        # Get today's widgets via API
        response = await make_api_request("GET", "/dashboard/getTodayWidgetList")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        data = response["data"]
        assert isinstance(data, list), "Response should be a list of today's widgets"
        
        print_test_result("Get Today Widgets (API)", True, f"Found {len(data)} today's widgets")
        return True
        
    except Exception as e:
        print_test_result("Get Today Widgets (API)", False, str(e))
        return False

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================
async def test_api_error_handling() -> bool:
    """Test API error handling for invalid requests."""
    print("\n🚨 Testing Widget Creation API Error Handling...")
    
    all_passed = True
    
    try:
        # Test 1: Invalid widget type
        invalid_data = {
            "widget_type": "invalid_type",
            "frequency": "daily",
            "importance": 0.8,
            "title": "Test Widget"
        }
        response = await make_api_request("POST", "/widgets/create", invalid_data)
        if response["status_code"] == 422:
            print_test_result("Invalid widget type (API)", True, "422 returned as expected")
        else:
            print_test_result("Invalid widget type (API)", False, f"Expected 422, got {response['status_code']}")
            all_passed = False
        
        # Test 2: Missing required fields
        incomplete_data = {
            "widget_type": "alarm"
            # Missing frequency, importance, title
        }
        response = await make_api_request("POST", "/widgets/create", incomplete_data)
        if response["status_code"] == 422:
            print_test_result("Missing required fields (API)", True, "422 returned as expected")
        else:
            print_test_result("Missing required fields (API)", False, f"Expected 422, got {response['status_code']}")
            all_passed = False
        
        # Test 3: Invalid importance value
        invalid_importance_data = {
            "widget_type": "alarm",
            "frequency": "daily",
            "importance": 1.5,  # Should be <= 1.0
            "title": "Test Widget"
        }
        response = await make_api_request("POST", "/widgets/create", invalid_importance_data)
        if response["status_code"] == 422:
            print_test_result("Invalid importance value (API)", True, "422 returned as expected")
        else:
            print_test_result("Invalid importance value (API)", False, f"Expected 422, got {response['status_code']}")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result("Widget Creation API Error Handling", False, str(e))
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_comprehensive_tests():
    """Run all comprehensive Widget Creation tests."""
    print("🚀 Starting Comprehensive Widget Creation API Tests")
    print("=" * 70)
    
    # Reset test data
    test_data.reset()
    
    # Track test results
    test_results = {
        "service_tests": [],
        "api_tests": [],
        "error_handling": False
    }
    
    # Phase 1: Service Method Tests
    print("\n📋 PHASE 1: Service Method Tests")
    print("-" * 50)
    
    test_results["service_tests"].append(await test_service_alarm_widget_creation())
    test_results["service_tests"].append(await test_service_todo_widget_creation())
    test_results["service_tests"].append(await test_service_tracker_widget_creation())
    
    # Phase 2: HTTP API Endpoint Tests
    print("\n📋 PHASE 2: HTTP API Endpoint Tests")
    print("-" * 50)
    
    test_results["api_tests"].append(await test_api_alarm_widget_creation())
    test_results["api_tests"].append(await test_api_todo_widget_creation())
    test_results["api_tests"].append(await test_api_tracker_widget_creation())
    test_results["api_tests"].append(await test_api_get_all_widgets())
    test_results["api_tests"].append(await test_api_get_today_widgets())
    
    # Phase 3: Error Handling Tests
    print("\n📋 PHASE 3: Error Handling Tests")
    print("-" * 50)
    
    test_results["error_handling"] = await test_api_error_handling()
    
    # Print final results
    print("\n" + "=" * 70)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 70)
    
    service_passed = sum(test_results["service_tests"])
    service_total = len(test_results["service_tests"])
    api_passed = sum(test_results["api_tests"])
    api_total = len(test_results["api_tests"])
    
    print(f"✅ Service Tests: {service_passed}/{service_total} passed")
    print(f"✅ API Tests: {api_passed}/{api_total} passed")
    print(f"✅ Error Handling: {'PASS' if test_results['error_handling'] else 'FAIL'}")
    
    total_passed = service_passed + api_passed + (1 if test_results["error_handling"] else 0)
    total_tests = service_total + api_total + 1
    
    print(f"\n📊 OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Widget Creation API is complete and ready for production!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed. Please review and fix issues.")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests()) 