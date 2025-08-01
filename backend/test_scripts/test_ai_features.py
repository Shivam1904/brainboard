#!/usr/bin/env python3
"""
Test script for AI Features migration.
Tests both service methods and live API endpoints.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import json
import requests
from datetime import date, datetime
from typing import Dict, Any

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
TEST_USER_ID = "user_001"
TEST_DATE = date.today()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   📝 {details}")

def print_json(data: Dict[str, Any], title: str = "Response"):
    """Print JSON data in a formatted way."""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, default=str))

# ============================================================================
# API TESTS
# ============================================================================

async def test_ai_health_check():
    """Test AI health check endpoint."""
    print_section("AI Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/ai/health")
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test_result("AI Health Check", True, f"Status: {data.get('status')}")
            print_json(data, "Health Check Response")
        else:
            print_test_result("AI Health Check", False, f"Status code: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("AI Health Check", False, f"Error: {str(e)}")
        return False

async def test_generate_today_plan():
    """Test daily plan generation endpoint."""
    print_section("Daily Plan Generation")
    
    try:
        # Test with default date (today)
        response = requests.post(f"{API_BASE}/ai/generate_today_plan")
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test_result("Generate Today Plan (Default)", True, 
                            f"Widgets processed: {data.get('data', {}).get('widgets_processed', 0)}")
            print_json(data, "Daily Plan Response")
        else:
            print_test_result("Generate Today Plan (Default)", False, f"Status code: {response.status_code}")
            
        # Test with specific date
        specific_date = "2024-01-15"
        response = requests.post(f"{API_BASE}/ai/generate_today_plan?target_date={specific_date}")
        success2 = response.status_code == 200
        
        if success2:
            data = response.json()
            print_test_result("Generate Today Plan (Specific Date)", True, 
                            f"Target date: {data.get('target_date')}")
        else:
            print_test_result("Generate Today Plan (Specific Date)", False, f"Status code: {response.status_code}")
            
        return success and success2
    except Exception as e:
        print_test_result("Generate Today Plan", False, f"Error: {str(e)}")
        return False

async def test_generate_web_summary_list():
    """Test web summary generation endpoint."""
    print_section("Web Summary Generation")
    
    try:
        # Test with default date (today)
        response = requests.post(f"{API_BASE}/ai/generate_web_summary_list")
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test_result("Generate Web Summary List (Default)", True, 
                            f"Summaries generated: {data.get('data', {}).get('summaries_generated', 0)}")
            print_json(data, "Web Summary Response")
        else:
            print_test_result("Generate Web Summary List (Default)", False, f"Status code: {response.status_code}")
            
        # Test with specific date
        specific_date = "2024-01-15"
        response = requests.post(f"{API_BASE}/ai/generate_web_summary_list?target_date={specific_date}")
        success2 = response.status_code == 200
        
        if success2:
            data = response.json()
            print_test_result("Generate Web Summary List (Specific Date)", True, 
                            f"Target date: {data.get('target_date')}")
        else:
            print_test_result("Generate Web Summary List (Specific Date)", False, f"Status code: {response.status_code}")
            
        return success and success2
    except Exception as e:
        print_test_result("Generate Web Summary List", False, f"Error: {str(e)}")
        return False

async def test_generate_activity_from_plan():
    """Test activity generation from AI plan endpoint."""
    print_section("Activity Generation from Plan")
    
    try:
        # Test with default date (today)
        response = requests.post(f"{API_BASE}/ai/generate_activity_from_plan")
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test_result("Generate Activity from Plan (Default)", True, 
                            f"Activities created: {data.get('data', {}).get('activities_created', 0)}")
            print_json(data, "Activity Generation Response")
        else:
            print_test_result("Generate Activity from Plan (Default)", False, f"Status code: {response.status_code}")
            
        # Test with specific date
        specific_date = "2024-01-15"
        response = requests.post(f"{API_BASE}/ai/generate_activity_from_plan?target_date={specific_date}")
        success2 = response.status_code == 200
        
        if success2:
            data = response.json()
            print_test_result("Generate Activity from Plan (Specific Date)", True, 
                            f"Target date: {data.get('target_date')}")
        else:
            print_test_result("Generate Activity from Plan (Specific Date)", False, f"Status code: {response.status_code}")
            
        return success and success2
    except Exception as e:
        print_test_result("Generate Activity from Plan", False, f"Error: {str(e)}")
        return False

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

async def test_full_ai_workflow():
    """Test the complete AI workflow."""
    print_section("Full AI Workflow Test")
    
    try:
        # Step 1: Generate daily plan
        print("🔄 Step 1: Generating daily plan...")
        response = requests.post(f"{API_BASE}/ai/generate_today_plan")
        if response.status_code != 200:
            print_test_result("Full AI Workflow", False, "Step 1 failed: Daily plan generation")
            return False
        
        plan_data = response.json()
        print(f"   ✅ Daily plan generated: {plan_data.get('data', {}).get('widgets_processed', 0)} widgets processed")
        
        # Step 2: Generate web summaries
        print("🔄 Step 2: Generating web summaries...")
        response = requests.post(f"{API_BASE}/ai/generate_web_summary_list")
        if response.status_code != 200:
            print_test_result("Full AI Workflow", False, "Step 2 failed: Web summary generation")
            return False
        
        summary_data = response.json()
        print(f"   ✅ Web summaries generated: {summary_data.get('data', {}).get('summaries_generated', 0)} summaries")
        
        # Step 3: Generate activities from plan
        print("🔄 Step 3: Generating activities from plan...")
        response = requests.post(f"{API_BASE}/ai/generate_activity_from_plan")
        if response.status_code != 200:
            print_test_result("Full AI Workflow", False, "Step 3 failed: Activity generation")
            return False
        
        activity_data = response.json()
        print(f"   ✅ Activities generated: {activity_data.get('data', {}).get('activities_created', 0)} activities")
        
        print_test_result("Full AI Workflow", True, "All steps completed successfully")
        return True
        
    except Exception as e:
        print_test_result("Full AI Workflow", False, f"Error: {str(e)}")
        return False

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

async def test_error_handling():
    """Test error handling scenarios."""
    print_section("Error Handling Tests")
    
    try:
        # Test with invalid date format
        response = requests.post(f"{API_BASE}/ai/generate_today_plan?target_date=invalid-date")
        success1 = response.status_code == 422  # Validation error expected
        
        if success1:
            print_test_result("Invalid Date Format", True, "Properly handled validation error")
        else:
            print_test_result("Invalid Date Format", False, f"Unexpected status code: {response.status_code}")
        
        # Test with future date (should still work)
        future_date = "2025-12-31"
        response = requests.post(f"{API_BASE}/ai/generate_today_plan?target_date={future_date}")
        success2 = response.status_code == 200
        
        if success2:
            print_test_result("Future Date", True, "Successfully handled future date")
        else:
            print_test_result("Future Date", False, f"Status code: {response.status_code}")
        
        return success1 and success2
        
    except Exception as e:
        print_test_result("Error Handling", False, f"Error: {str(e)}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_tests():
    """Run all AI feature tests."""
    print("🚀 Starting AI Features Migration Tests")
    print(f"📅 Test Date: {TEST_DATE}")
    print(f"👤 Test User: {TEST_USER_ID}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    test_results = []
    
    # Run individual tests
    test_results.append(await test_ai_health_check())
    test_results.append(await test_generate_today_plan())
    test_results.append(await test_generate_web_summary_list())
    test_results.append(await test_generate_activity_from_plan())
    test_results.append(await test_full_ai_workflow())
    test_results.append(await test_error_handling())
    
    # Print summary
    print_section("Test Summary")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"📊 Results: {passed}/{total} tests passed")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! AI Features migration is successful!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1) 