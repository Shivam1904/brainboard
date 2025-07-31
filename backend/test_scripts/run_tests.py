"""
Test runner script for all backend tests.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from test_scripts.test_daily_widget_api import run_comprehensive_test as run_daily_widget_tests
from test_scripts.test_widget_creation_api import run_widget_creation_test as run_widget_creation_tests

# ============================================================================
# TEST RUNNER
# ============================================================================
async def run_all_tests():
    """Run all available tests."""
    print("🚀 Starting Backend Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Daily Widget API Tests
    print("\n📋 Running Daily Widget API Tests...")
    try:
        daily_widget_result = await run_daily_widget_tests()
        test_results.append(("Daily Widget API", daily_widget_result))
    except Exception as e:
        print(f"❌ Error running Daily Widget API tests: {e}")
        test_results.append(("Daily Widget API", False))
    
    # Test 2: Widget Creation API Tests
    print("\n📋 Running Widget Creation API Tests...")
    try:
        widget_creation_result = await run_widget_creation_tests()
        test_results.append(("Widget Creation API", widget_creation_result))
    except Exception as e:
        print(f"❌ Error running Widget Creation API tests: {e}")
        test_results.append(("Widget Creation API", False))
    
    # Print overall summary
    print("\n" + "=" * 60)
    print("📊 OVERALL TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_suite, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_suite}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All test suites passed! Backend is working correctly.")
        return True
    else:
        print("⚠️  Some test suites failed. Please check the implementation.")
        return False

def run_specific_test(test_name: str):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    
    if test_name.lower() in ["daily_widget", "daily_widget_api", "widget"]:
        return asyncio.run(run_daily_widget_tests())
    elif test_name.lower() in ["widget_creation", "create_widget", "creation"]:
        return asyncio.run(run_widget_creation_tests())
    else:
        print(f"❌ Unknown test: {test_name}")
        print("Available tests: daily_widget, widget_creation")
        return False

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1) 