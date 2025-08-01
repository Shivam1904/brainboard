"""
Comprehensive WebSearch API Test Suite
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
from services.websearch_service import WebSearchService
from schemas.widget import CreateWidgetRequest, WidgetType, Frequency
from schemas.websearch import UpdateActivityRequest, UpdateWebSearchDetailsRequest

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_USER_ID = "user_001"

TEST_WIDGET_DATA = {
    "widget_type": WidgetType.WEBSEARCH,
    "frequency": Frequency.DAILY,
    "importance": 0.8,
    "title": "AI Trends 2024",
    "category": "research"
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
        self.ai_summary_id: Optional[str] = None
    
    def reset(self):
        """Reset all test data."""
        self.widget_id = None
        self.details_id = None
        self.activity_id = None
        self.ai_summary_id = None

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
    print("\n🔧 Testing Widget Creation (Service)...")
    
    try:
        async with AsyncSessionLocal() as db:
            widget_service = WidgetService(db)
            create_request = CreateWidgetRequest(**TEST_WIDGET_DATA)
            result = await widget_service.create_widget(create_request, TEST_USER_ID)
            
            # Validate response
            assert result.success == True, "Widget creation should succeed"
            assert result.widget_id is not None, "Widget ID should be generated"
            assert result.widget_type == "websearch", "Widget type should be websearch"
            
            # Store for later tests
            test_data.widget_id = result.widget_id
            
            print_test_result("Widget Creation", True, f"Widget ID: {result.widget_id}")
            return True
            
    except Exception as e:
        print_test_result("Widget Creation", False, str(e))
        return False

async def test_service_details_retrieval() -> bool:
    """Test details retrieval via service method."""
    print("\n🔧 Testing Details Retrieval (Service)...")
    
    if not test_data.widget_id:
        print_test_result("Details Retrieval", False, "No widget ID available")
        return False
    
    try:
        async with AsyncSessionLocal() as db:
            websearch_service = WebSearchService(db)
            details = await websearch_service.get_websearch_details(test_data.widget_id, TEST_USER_ID)
            
            # Validate response
            assert details is not None, "Details should not be None"
            assert details["widget_id"] == test_data.widget_id, "Widget ID should match"
            assert details["title"] == TEST_WIDGET_DATA["title"], "Title should match"
            
            # Store for later tests
            test_data.details_id = details["id"]
            
            print_test_result("Details Retrieval", True, f"Details ID: {details['id']}")
            return True
            
    except Exception as e:
        print_test_result("Details Retrieval", False, str(e))
        return False

async def test_service_summary_and_activity() -> bool:
    """Test summary and activity retrieval via service method."""
    print("\n🔧 Testing Summary and Activity (Service)...")
    
    if not test_data.widget_id:
        print_test_result("Summary and Activity", False, "No widget ID available")
        return False
    
    try:
        async with AsyncSessionLocal() as db:
            websearch_service = WebSearchService(db)
            result = await websearch_service.get_summary_and_activity(test_data.widget_id, TEST_USER_ID)
            
            # Validate response
            assert result is not None, "Result should not be None"
            assert result.get("websearch_details") is not None, "WebSearch details should exist"
            assert result.get("activity") is not None, "Activity should be created"
            
            activity = result["activity"]
            assert activity["widget_id"] == test_data.widget_id, "Activity widget ID should match"
            assert activity["status"] == "pending", "New activity should have pending status"
            
            # Store for later tests
            test_data.activity_id = activity["id"]
            
            print_test_result("Summary and Activity", True, f"Activity ID: {activity['id']}")
            return True
            
    except Exception as e:
        print_test_result("Summary and Activity", False, str(e))
        return False

# ============================================================================
# HTTP API ENDPOINT TESTS (Integration Tests)
# ============================================================================
async def test_api_widget_creation() -> bool:
    """Test widget creation via HTTP API."""
    print("\n🌐 Testing Widget Creation (HTTP API)...")
    
    try:
        # Create widget via API
        response = await make_api_request("POST", "/widgets/create", TEST_WIDGET_DATA)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["success", "widget_id", "widget_type"]), "Invalid response structure"
        
        data = response["data"]
        assert data["success"] == True, "Widget creation should succeed"
        assert data["widget_type"] == "websearch", "Widget type should be websearch"
        
        # Store for later tests
        test_data.widget_id = data["widget_id"]
        
        print_test_result("Widget Creation (API)", True, f"Widget ID: {data['widget_id']}")
        return True
        
    except Exception as e:
        print_test_result("Widget Creation (API)", False, str(e))
        return False

async def test_api_get_details() -> bool:
    """Test getting WebSearch details via HTTP API."""
    print("\n🌐 Testing Get Details (HTTP API)...")
    
    if not test_data.widget_id:
        print_test_result("Get Details (API)", False, "No widget ID available")
        return False
    
    try:
        # Get details via API
        response = await make_api_request("GET", f"/websearch/getWebsearchDetails/{test_data.widget_id}")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["id", "widget_id", "title"]), "Invalid response structure"
        
        data = response["data"]
        assert data["widget_id"] == test_data.widget_id, "Widget ID should match"
        assert data["title"] == TEST_WIDGET_DATA["title"], "Title should match"
        
        # Store for later tests
        test_data.details_id = data["id"]
        
        print_test_result("Get Details (API)", True, f"Details ID: {data['id']}")
        return True
        
    except Exception as e:
        print_test_result("Get Details (API)", False, str(e))
        return False

async def test_api_get_summary_and_activity() -> bool:
    """Test getting summary and activity via HTTP API."""
    print("\n🌐 Testing Get Summary and Activity (HTTP API)...")
    
    if not test_data.widget_id:
        print_test_result("Get Summary and Activity (API)", False, "No widget ID available")
        return False
    
    try:
        # Get summary and activity via API
        response = await make_api_request("GET", f"/websearch/getSummaryAndActivity/{test_data.widget_id}")
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["websearch_details", "activity"]), "Invalid response structure"
        
        data = response["data"]
        assert data["websearch_details"] is not None, "WebSearch details should exist"
        assert data["activity"] is not None, "Activity should exist"
        
        activity = data["activity"]
        assert activity["widget_id"] == test_data.widget_id, "Activity widget ID should match"
        assert activity["status"] == "pending", "New activity should have pending status"
        
        # Store for later tests
        test_data.activity_id = activity["id"]
        
        print_test_result("Get Summary and Activity (API)", True, f"Activity ID: {activity['id']}")
        return True
        
    except Exception as e:
        print_test_result("Get Summary and Activity (API)", False, str(e))
        return False

async def test_api_update_activity() -> bool:
    """Test updating activity via HTTP API."""
    print("\n🌐 Testing Update Activity (HTTP API)...")
    
    if not test_data.activity_id:
        print_test_result("Update Activity (API)", False, "No activity ID available")
        return False
    
    try:
        # Update activity via API
        update_data = {
            "status": "completed",
            "reaction": "Great search results!",
            "summary": "AI trends are evolving rapidly in 2024",
            "source_json": {
                "sources": [
                    {"title": "AI Trends 2024", "url": "https://example.com/ai-trends"}
                ]
            }
        }
        
        response = await make_api_request("POST", f"/websearch/updateActivity/{test_data.activity_id}", update_data)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["activity_id", "status", "reaction", "summary"]), "Invalid response structure"
        
        data = response["data"]
        assert data["activity_id"] == test_data.activity_id, "Activity ID should match"
        assert data["status"] == "completed", "Status should be updated"
        assert data["reaction"] == "Great search results!", "Reaction should be updated"
        
        print_test_result("Update Activity (API)", True, f"Activity updated successfully")
        return True
        
    except Exception as e:
        print_test_result("Update Activity (API)", False, str(e))
        return False

async def test_api_update_details() -> bool:
    """Test updating details via HTTP API."""
    print("\n🌐 Testing Update Details (HTTP API)...")
    
    if not test_data.details_id:
        print_test_result("Update Details (API)", False, "No details ID available")
        return False
    
    try:
        # Update details via API
        update_data = {
            "title": "Updated AI Trends 2024"
        }
        
        response = await make_api_request("POST", f"/websearch/updateDetails/{test_data.details_id}", update_data)
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert validate_response_structure(response, ["id", "title", "updated_at"]), "Invalid response structure"
        
        data = response["data"]
        assert data["id"] == test_data.details_id, "Details ID should match"
        assert data["title"] == "Updated AI Trends 2024", "Title should be updated"
        assert data["updated_at"] is not None, "Updated at should be set"
        
        print_test_result("Update Details (API)", True, f"Details updated successfully")
        return True
        
    except Exception as e:
        print_test_result("Update Details (API)", False, str(e))
        return False

async def test_api_get_ai_summary() -> bool:
    """Test getting AI summary via HTTP API."""
    print("\n🌐 Testing Get AI Summary (HTTP API)...")
    
    if not test_data.widget_id:
        print_test_result("Get AI Summary (API)", False, "No widget ID available")
        return False
    
    try:
        # Get AI summary via API
        response = await make_api_request("GET", f"/websearch/getaisummary/{test_data.widget_id}")
        
        # This should return 404 or empty result since no AI processing has been done
        if response["status_code"] == 404:
            print_test_result("Get AI Summary (API)", True, "No AI summary found (expected)")
            return True
        elif response["status_code"] == 200 and not response["data"]:
            print_test_result("Get AI Summary (API)", True, "No AI summary found (expected)")
            return True
        elif response["status_code"] == 200 and response["data"]:
            # If there is data, validate the structure
            data = response["data"]
            assert "ai_summary_id" in data, "AI summary ID should exist"
            assert "widget_id" in data, "Widget ID should exist"
            assert "query" in data, "Query should exist"
            assert "summary" in data, "Summary should exist"
            
            test_data.ai_summary_id = data["ai_summary_id"]
            print_test_result("Get AI Summary (API)", True, f"AI Summary ID: {data['ai_summary_id']}")
            return True
        else:
            print_test_result("Get AI Summary (API)", False, f"Unexpected status: {response['status_code']}")
            return False
        
    except Exception as e:
        print_test_result("Get AI Summary (API)", False, str(e))
        return False

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================
async def test_api_error_handling() -> bool:
    """Test API error handling for invalid requests."""
    print("\n🚨 Testing API Error Handling...")
    
    all_passed = True
    
    try:
        # Test 1: Get details for non-existent widget
        response = await make_api_request("GET", "/websearch/getWebsearchDetails/non-existent-id")
        if response["status_code"] == 404:
            print_test_result("Non-existent widget (API)", True, "404 returned as expected")
        else:
            print_test_result("Non-existent widget (API)", False, f"Expected 404, got {response['status_code']}")
            all_passed = False
        
        # Test 2: Get summary for non-existent widget
        response = await make_api_request("GET", "/websearch/getSummaryAndActivity/non-existent-id")
        if response["status_code"] == 404:
            print_test_result("Non-existent widget summary (API)", True, "404 returned as expected")
        else:
            print_test_result("Non-existent widget summary (API)", False, f"Expected 404, got {response['status_code']}")
            all_passed = False
        
        # Test 3: Update non-existent activity
        response = await make_api_request("POST", "/websearch/updateActivity/non-existent-id", {"status": "completed"})
        if response["status_code"] == 404:
            print_test_result("Non-existent activity update (API)", True, "404 returned as expected")
        else:
            print_test_result("Non-existent activity update (API)", False, f"Expected 404, got {response['status_code']}")
            all_passed = False
        
        # Test 4: Update non-existent details
        response = await make_api_request("POST", "/websearch/updateDetails/non-existent-id", {"title": "test"})
        if response["status_code"] == 404:
            print_test_result("Non-existent details update (API)", True, "404 returned as expected")
        else:
            print_test_result("Non-existent details update (API)", False, f"Expected 404, got {response['status_code']}")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result("API Error Handling", False, str(e))
        return False

# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================
async def test_schema_validation() -> bool:
    """Test Pydantic schema validation."""
    print("\n📋 Testing Schema Validation...")
    
    all_passed = True
    
    try:
        # Test valid UpdateActivityRequest
        valid_activity_data = {
            "status": "completed",
            "reaction": "Great results!",
            "summary": "Test summary",
            "source_json": {"sources": []}
        }
        activity_request = UpdateActivityRequest(**valid_activity_data)
        assert activity_request.status == "completed"
        print_test_result("Valid UpdateActivityRequest", True)
        
        # Test valid UpdateWebSearchDetailsRequest
        valid_details_data = {
            "title": "Updated Title"
        }
        details_request = UpdateWebSearchDetailsRequest(**valid_details_data)
        assert details_request.title == "Updated Title"
        print_test_result("Valid UpdateWebSearchDetailsRequest", True)
        
        # Test invalid data (should raise validation error)
        try:
            invalid_activity_data = {
                "status": "invalid_status",  # Invalid status
                "reaction": "A" * 1001  # Too long
            }
            UpdateActivityRequest(**invalid_activity_data)
            print_test_result("Invalid data validation", False, "Should have raised validation error")
            all_passed = False
        except Exception:
            print_test_result("Invalid data validation", True, "Validation error raised as expected")
        
        return all_passed
        
    except Exception as e:
        print_test_result("Schema Validation", False, str(e))
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive WebSearch API Tests")
    print("=" * 70)
    
    # Reset test data
    test_data.reset()
    
    # Track test results
    test_results = {
        "service_tests": [],
        "api_tests": [],
        "error_handling": False,
        "schema_validation": False
    }
    
    # Phase 1: Service Method Tests
    print("\n📋 PHASE 1: Service Method Tests")
    print("-" * 50)
    
    test_results["service_tests"].append(await test_service_widget_creation())
    test_results["service_tests"].append(await test_service_details_retrieval())
    test_results["service_tests"].append(await test_service_summary_and_activity())
    
    # Phase 2: HTTP API Endpoint Tests
    print("\n📋 PHASE 2: HTTP API Endpoint Tests")
    print("-" * 50)
    
    test_results["api_tests"].append(await test_api_widget_creation())
    test_results["api_tests"].append(await test_api_get_details())
    test_results["api_tests"].append(await test_api_get_summary_and_activity())
    test_results["api_tests"].append(await test_api_update_activity())
    test_results["api_tests"].append(await test_api_update_details())
    test_results["api_tests"].append(await test_api_get_ai_summary())
    
    # Phase 3: Error Handling Tests
    print("\n📋 PHASE 3: Error Handling Tests")
    print("-" * 50)
    
    test_results["error_handling"] = await test_api_error_handling()
    
    # Phase 4: Schema Validation Tests
    print("\n📋 PHASE 4: Schema Validation Tests")
    print("-" * 50)
    
    test_results["schema_validation"] = await test_schema_validation()
    
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
    print(f"✅ Schema Validation: {'PASS' if test_results['schema_validation'] else 'FAIL'}")
    
    total_passed = service_passed + api_passed + (1 if test_results["error_handling"] else 0) + (1 if test_results["schema_validation"] else 0)
    total_tests = service_total + api_total + 2
    
    print(f"\n📊 OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! WebSearch migration is complete and ready for production!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed. Please review and fix issues.")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests()) 