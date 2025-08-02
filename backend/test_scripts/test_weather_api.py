"""
Simplified Weather API Test Suite
Tests the simplified weather endpoint that directly calls Open-Meteo API.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import sys
import os
import json
import httpx
from typing import Dict, Any, Optional

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.weather_service import WeatherService
from schemas.weather import WeatherResponse

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

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

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def validate_weather_data(data: Dict) -> bool:
    """Validate weather data structure and values."""
    required_fields = ["temperature", "humidity", "pressure", "description", "icon_code", "wind_speed", "wind_direction", "visibility", "data_timestamp", "location", "units"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate data types and reasonable ranges
    if not isinstance(data["temperature"], (int, float)) or data["temperature"] < -100 or data["temperature"] > 100:
        return False
    
    if not isinstance(data["humidity"], int) or data["humidity"] < 0 or data["humidity"] > 100:
        return False
    
    if not isinstance(data["pressure"], (int, float)) or data["pressure"] < 800 or data["pressure"] > 1200:
        return False
    
    if not isinstance(data["wind_speed"], (int, float)) or data["wind_speed"] < 0:
        return False
    
    if not isinstance(data["wind_direction"], int) or data["wind_direction"] < 0 or data["wind_direction"] > 360:
        return False
    
    return True

# ============================================================================
# SERVICE METHOD TESTS (Unit Tests)
# ============================================================================
async def test_service_weather_call() -> bool:
    """Test weather service method directly."""
    print("\n🔧 Testing Weather Service Method...")
    
    try:
        service = WeatherService()
        result = await service.get_weather(51.5074, -0.1278, "metric")
        
        # Validate response
        assert "error" not in result, f"Weather service should not return error: {result.get('error', 'Unknown error')}"
        assert validate_weather_data(result), "Weather data should have valid structure"
        
        print_test_result("Weather Service Method", True, f"Temperature: {result.get('temperature')}°C, Description: {result.get('description')}")
        return True
        
    except Exception as e:
        print_test_result("Weather Service Method", False, str(e))
        return False

# ============================================================================
# HTTP API ENDPOINT TESTS (Integration Tests)
# ============================================================================
async def test_api_get_weather() -> bool:
    """Test GET weather endpoint via HTTP API."""
    print("\n🌐 Testing GET Weather (HTTP API)...")
    
    try:
        # Get weather via API
        response = await make_api_request("GET", "/weather/", params={"lat": 51.5074, "lon": -0.1278, "units": "metric"})
        
        # Validate response
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        data = response["data"]
        assert validate_weather_data(data), "Weather data should have valid structure"
        
        print_test_result("GET Weather (API)", True, f"Temperature: {data.get('temperature')}°C, Description: {data.get('description')}")
        return True
        
    except Exception as e:
        print_test_result("GET Weather (API)", False, str(e))
        return False



# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================
async def test_api_error_handling() -> bool:
    """Test API error handling for invalid requests."""
    print("\n🚨 Testing API Error Handling...")
    
    all_passed = True
    
    try:
        # Test 1: Invalid latitude (out of range) - Open-Meteo returns 400 for invalid coordinates
        response = await make_api_request("GET", "/weather/", params={"lat": 100, "lon": 0})
        if response["status_code"] == 400:  # Open-Meteo API error
            print_test_result("Invalid latitude (API)", True, "400 returned as expected")
        else:
            print_test_result("Invalid latitude (API)", False, f"Expected 400, got {response['status_code']}")
            all_passed = False
        
        # Test 2: Missing parameters
        response = await make_api_request("GET", "/weather/")
        if response["status_code"] == 422:  # Validation error
            print_test_result("Missing parameters (API)", True, "422 returned as expected")
        else:
            print_test_result("Missing parameters (API)", False, f"Expected 422, got {response['status_code']}")
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

        
        # Test valid WeatherResponse
        valid_response_data = {
            "temperature": 18.5,
            "humidity": 65,
            "pressure": 1013.2,
            "description": "Partly cloudy",
            "icon_code": "2",
            "wind_speed": 12.5,
            "wind_direction": 180,
            "visibility": 10000,
            "data_timestamp": "2025-08-01T20:08:30.410122",
            "location": "51.5074,-0.1278",
            "units": "metric"
        }
        response = WeatherResponse(**valid_response_data)
        assert response.temperature == 18.5
        assert response.description == "Partly cloudy"
        print_test_result("Valid WeatherResponse", True)
        
        return all_passed
        
    except Exception as e:
        print_test_result("Schema Validation", False, str(e))
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_simplified_tests():
    """Run all simplified tests."""
    print("🌤️ Starting Simplified Weather API Tests")
    print("=" * 60)
    
    # Track test results
    test_results = {
        "service_tests": [],
        "api_tests": [],
        "error_handling": False,
        "schema_validation": False
    }
    
    # Phase 1: Service Method Tests
    print("\n📋 PHASE 1: Service Method Tests")
    print("-" * 40)
    
    test_results["service_tests"].append(await test_service_weather_call())
    
    # Phase 2: HTTP API Endpoint Tests
    print("\n📋 PHASE 2: HTTP API Endpoint Tests")
    print("-" * 40)
    
    test_results["api_tests"].append(await test_api_get_weather())
    
    # Phase 3: Error Handling Tests
    print("\n📋 PHASE 3: Error Handling Tests")
    print("-" * 40)
    
    test_results["error_handling"] = await test_api_error_handling()
    
    # Phase 4: Schema Validation Tests
    print("\n📋 PHASE 4: Schema Validation Tests")
    print("-" * 40)
    
    test_results["schema_validation"] = await test_schema_validation()
    
    # Print final results
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    
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
        print("\n🎉 ALL TESTS PASSED! Simplified weather API is working perfectly!")
        print("🌤️ Open-Meteo integration is working without any database dependencies!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed. Please review and fix issues.")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_simplified_tests()) 