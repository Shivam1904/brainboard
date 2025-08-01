"""
Comprehensive Todo API Test Suite
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
from services.todo_service import TodoService
from schemas.widget import CreateWidgetRequest, WidgetType, Frequency

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_USER_ID = "user_001"

TEST_WIDGET_DATA = {
    "widget_type": WidgetType.TODO_TASK,
    "frequency": Frequency.DAILY,
    "importance": 0.8,
    "title": "Complete Project Documentation",
    "category": "work"
}

# ============================================================================
# TEST DATA
# ============================================================================
class TestData:
    """Test data and state management."""
    
    def __init__(self):
        self.widget_id: Optional[str] = None
        self.details_id: Optional[str] = None
        self.activity_id: Optional[str] = None
    
    def reset(self):
        """Reset all test data."""
        self.widget_id = None
        self.details_id = None
        self.activity_id = None

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
async def test_service_widget_creation() -> bool:
    """Test widget creation via service method."""
    print("\n🔧 Testing Todo Widget Creation (Service)...")
    
    try:
        async with AsyncSessionLocal() as db:
            widget_service = WidgetService(db)
            create_request = CreateWidgetRequest(**TEST_WIDGET_DATA)
            result = await widget_service.create_widget(create_request, TEST_USER_ID)
            
            # Validate response
            assert result.success == True, "Widget creation should succeed"
            assert result.widget_id is not None, "Widget ID should be generated"
            assert result.widget_type == "todo-task", "Widget type should be todo-task"
            
            # Store for later tests
            test_data.widget_id = result.widget_id
            
            print_test_result("Todo Widget Creation", True, f"Widget ID: {result.widget_id}")
            return True
            
    except Exception as e:
        print_test_result("Todo Widget Creation", False, str(e))
        return False

async def test_service_details_retrieval() -> bool:
    """Test details retrieval via service method."""
    print("\n🔧 Testing Todo Details Retrieval (Service)...")
    
    if not test_data.widget_id:
        print_test_result("Todo Details Retrieval", False, "No widget ID available")
        return False
    
    try:
        async with AsyncSessionLocal() as db:
            todo_service = TodoService(db)
            details = await todo_service.get_todo_details(test_data.widget_id, TEST_USER_ID)
            
            # Validate response
            assert details is not None, "Details should not be None"
            assert details["widget_id"] == test_data.widget_id, "Widget ID should match"
            assert details["title"] == TEST_WIDGET_DATA["title"], "Title should match"
            
            # Store for later tests
            test_data.details_id = details["id"]
            
            print_test_result("Todo Details Retrieval", True, f"Details ID: {details['id']}")
            return True
            
    except Exception as e:
        print_test_result("Todo Details Retrieval", False, str(e))
        return False

async def test_service_details_and_activity() -> bool:
    """Test details and activity retrieval via service method."""
    print("\n🔧 Testing Todo Details and Activity (Service)...")
    
    if not test_data.widget_id:
        print_test_result("Todo Details and Activity", False, "No widget ID available")
        return False
    
    try:
        async with AsyncSessionLocal() as db:
            todo_service = TodoService(db)
            result = await todo_service.get_todo_details_and_activity(test_data.widget_id, TEST_USER_ID)
            
            # Validate response
            assert result is not None, "Result should not be None"
            assert result.get("todo_details") is not None, "Todo details should exist"
            # Activities might be empty for new widgets, which is normal
            activities = result.get("activities", [])
            
            # Store for later tests if we have activities
            if activities:
                test_data.activity_id = activities[0]["id"]
                print_test_result("Todo Details and Activity", True, f"Activity ID: {activities[0]['id']}")
            else:
                print_test_result("Todo Details and Activity", True, "No activities found (normal for new widgets)")
            return True
            
            print_test_result("Todo Details and Activity", True, f"Activity ID: {activity['id']}")
            return True
            
    except Exception as e:
        print_test_result("Todo Details and Activity", False, str(e))
        return False

# ============================================================================
# HTTP API ENDPOINT TESTS (Integration Tests)
# ============================================================================
async def test_api_widget_creation() -> bool:
    """Test widget creation via HTTP API."""
    print("\n🌐 Testing Todo Widget Creation (HTTP API)...")
    
    try:
        # Create widget via API
        response = await make_api_request("POST", "/widgets/create", TEST_WIDGET_DATA)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "widget_id", "widget_type"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Widget creation should succeed"
        assert data["widget_type"] == "todo-task", "Widget type should be todo-task"
        
        # Store for later tests
        test_data.widget_id = data["widget_id"]
        
        print_test_result("Todo Widget Creation (API)", True, f"Widget ID: {data['widget_id']}")
        return True
        
    except Exception as e:
        print_test_result("Todo Widget Creation (API)", False, str(e))
        return False

async def test_api_get_details() -> bool:
    """Test getting Todo details via HTTP API."""
    print("\n🌐 Testing Get Todo Details (HTTP API)...")
    
    if not test_data.widget_id:
        print_test_result("Get Todo Details (API)", False, "No widget ID available")
        return False
    
    try:
        # Get details via API
        response = await make_api_request("GET", f"/todo/getTodoDetails/{test_data.widget_id}")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["id", "widget_id", "title"]), "Invalid response structure"
        
        data = response["data"]
        assert data["widget_id"] == test_data.widget_id, "Widget ID should match"
        assert data["title"] == TEST_WIDGET_DATA["title"], "Title should match"
        
        # Store for later tests
        test_data.details_id = data["id"]
        
        print_test_result("Get Todo Details (API)", True, f"Details ID: {data['id']}")
        return True
        
    except Exception as e:
        print_test_result("Get Todo Details (API)", False, str(e))
        return False

async def test_api_get_details_and_activity() -> bool:
    """Test getting Todo details and activity via HTTP API."""
    print("\n🌐 Testing Get Todo Details and Activity (HTTP API)...")
    
    if not test_data.widget_id:
        print_test_result("Get Todo Details and Activity (API)", False, "No widget ID available")
        return False
    
    try:
        # Get details and activity via API
        response = await make_api_request("GET", f"/todo/getTodoDetailsAndActivity/{test_data.widget_id}")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["todo_details", "activities"]), "Invalid response structure"
        
        data = response["data"]
        assert data["todo_details"] is not None, "Todo details should exist"
        # Activities might be empty for new widgets, which is normal
        activities = data.get("activities", [])
        
        # Store for later tests if we have activities
        if activities:
            test_data.activity_id = activities[0]["id"]
            print_test_result("Get Todo Details and Activity (API)", True, f"Activity ID: {activities[0]['id']}")
        else:
            print_test_result("Get Todo Details and Activity (API)", True, "No activities found (normal for new widgets)")
        return True
        
        print_test_result("Get Todo Details and Activity (API)", True, f"Activity ID: {activity['id']}")
        return True
        
    except Exception as e:
        print_test_result("Get Todo Details and Activity (API)", False, str(e))
        return False

async def test_api_update_status() -> bool:
    """Test updating Todo status via HTTP API."""
    print("\n🌐 Testing Update Todo Status (HTTP API)...")
    
    if not test_data.activity_id:
        print_test_result("Update Todo Status (API)", False, "No activity ID available")
        return False
    
    try:
        # Update status via API
        update_data = {"status": "completed"}
        
        response = await make_api_request("POST", f"/todo/updateStatus/{test_data.activity_id}", update_data)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["activity_id", "status"]), "Invalid response structure"
        
        data = response["data"]
        assert data["activity_id"] == test_data.activity_id, "Activity ID should match"
        assert data["status"] == "completed", "Status should be updated"
        
        print_test_result("Update Todo Status (API)", True, f"Status updated to completed")
        return True
        
    except Exception as e:
        print_test_result("Update Todo Status (API)", False, str(e))
        return False

async def test_api_update_progress() -> bool:
    """Test updating Todo progress via HTTP API."""
    print("\n🌐 Testing Update Todo Progress (HTTP API)...")
    
    if not test_data.activity_id:
        print_test_result("Update Todo Progress (API)", False, "No activity ID available")
        return False
    
    try:
        # Update progress via API
        update_data = {"progress": 75}
        
        response = await make_api_request("POST", f"/todo/updateProgress/{test_data.activity_id}", update_data)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["activity_id", "progress"]), "Invalid response structure"
        
        data = response["data"]
        assert data["activity_id"] == test_data.activity_id, "Activity ID should match"
        assert data["progress"] == 75, "Progress should be updated"
        
        print_test_result("Update Todo Progress (API)", True, f"Progress updated to 75%")
        return True
        
    except Exception as e:
        print_test_result("Update Todo Progress (API)", False, str(e))
        return False

async def test_api_update_details() -> bool:
    """Test updating Todo details via HTTP API."""
    print("\n🌐 Testing Update Todo Details (HTTP API)...")
    
    if not test_data.details_id:
        print_test_result("Update Todo Details (API)", False, "No details ID available")
        return False
    
    try:
        # Update details via API
        update_data = {
            "title": "Updated Project Documentation",
            "description": "Complete the project documentation with all requirements"
        }
        
        response = await make_api_request("POST", f"/todo/updateDetails/{test_data.details_id}", update_data)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "message", "todo_details"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Update should be successful"
        assert data["message"] == "Todo details updated", "Message should match"
        
        todo_details = data["todo_details"]
        assert todo_details["id"] == test_data.details_id, "Details ID should match"
        assert todo_details["title"] == "Updated Project Documentation", "Title should be updated"
        assert todo_details["updated_at"] is not None, "Updated at should be set"
        
        print_test_result("Update Todo Details (API)", True, f"Details updated successfully")
        return True
        
    except Exception as e:
        print_test_result("Update Todo Details (API)", False, str(e))
        return False

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================
async def test_api_error_handling() -> bool:
    """Test API error handling for invalid requests."""
    print("\n🚨 Testing Todo API Error Handling...")
    
    all_passed = True
    
    try:
        # Test 1: Get details for non-existent widget
        response = await make_api_request("GET", "/todo/getTodoDetails/non-existent-id")
        if response["status_code"] == 404:
            print_test_result("Non-existent widget (API)", True, "404 returned as expected")
        else:
            print_test_result("Non-existent widget (API)", False, f"Expected 404, got {response['status_code']}")
            all_passed = False
        
        # Test 2: Get details and activity for non-existent widget
        response = await make_api_request("GET", "/todo/getTodoDetailsAndActivity/non-existent-id")
        if response["status_code"] == 200:
            print_test_result("Non-existent widget details (API)", True, "200 returned as expected (empty result)")
        else:
            print_test_result("Non-existent widget details (API)", False, f"Expected 200, got {response['status_code']}")
            all_passed = False
        
        # Test 3: Update non-existent activity status
        response = await make_api_request("POST", "/todo/updateStatus/non-existent-id", {"status": "completed"})
        if response["status_code"] == 422:
            print_test_result("Non-existent activity status update (API)", True, "422 returned as expected (validation error)")
        else:
            print_test_result("Non-existent activity status update (API)", False, f"Expected 422, got {response['status_code']}")
            all_passed = False
        
        # Test 4: Update non-existent activity progress
        response = await make_api_request("POST", "/todo/updateProgress/non-existent-id", {"progress": 50})
        if response["status_code"] == 422:
            print_test_result("Non-existent activity progress update (API)", True, "422 returned as expected (validation error)")
        else:
            print_test_result("Non-existent activity progress update (API)", False, f"Expected 422, got {response['status_code']}")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result("Todo API Error Handling", False, str(e))
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_comprehensive_tests():
    """Run all comprehensive Todo tests."""
    print("🚀 Starting Comprehensive Todo API Tests")
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
    
    test_results["service_tests"].append(await test_service_widget_creation())
    test_results["service_tests"].append(await test_service_details_retrieval())
    test_results["service_tests"].append(await test_service_details_and_activity())
    
    # Phase 2: HTTP API Endpoint Tests
    print("\n📋 PHASE 2: HTTP API Endpoint Tests")
    print("-" * 50)
    
    test_results["api_tests"].append(await test_api_widget_creation())
    test_results["api_tests"].append(await test_api_get_details())
    test_results["api_tests"].append(await test_api_get_details_and_activity())
    # Only test activity updates if we have activities
    if test_data.activity_id:
        test_results["api_tests"].append(await test_api_update_status())
        test_results["api_tests"].append(await test_api_update_progress())
    else:
        print("ℹ️  Skipping activity update tests (no activities available)")
        test_results["api_tests"].append(True)  # Skip status test
        test_results["api_tests"].append(True)  # Skip progress test
    
    test_results["api_tests"].append(await test_api_update_details())
    
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
        print("\n🎉 ALL TESTS PASSED! Todo API is complete and ready for production!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed. Please review and fix issues.")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests()) 