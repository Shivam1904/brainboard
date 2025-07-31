# Test Scripts

This directory contains comprehensive test scripts for the backend API.

## 📁 Structure

```
test_scripts/
├── __init__.py
├── README.md
├── run_tests.py                    # Main test runner
├── test_daily_widget_api.py        # Daily Widget API tests
└── [future test files...]
```

## 🚀 Running Tests

### Prerequisites

1. **Backend Server Running**: Make sure the backend server is running on `http://localhost:8000`
2. **Database Setup**: Ensure the database is initialized with some test data
3. **Dependencies**: Install required packages (`httpx`, `asyncio`, etc.)

### Running All Tests

```bash
cd backend
python test_scripts/run_tests.py
```

### Running Specific Tests

```bash
# Run only Daily Widget API tests
python test_scripts/run_tests.py daily_widget

# Run only Daily Widget API tests (alternative)
python test_scripts/test_daily_widget_api.py
```

## 🧪 Available Tests

### Daily Widget API Tests (`test_daily_widget_api.py`)

Tests the following endpoints:
- `GET /api/v1/dashboard/getTodayWidgetList` - Get today's widget list
- `POST /api/v1/dashboard/widget/addtotoday/{widget_id}` - Add widget to today
- `DELETE /api/v1/dashboard/widget/removefromtoday/{widget_id}` - Remove widget from today

**Test Cases:**
1. ✅ Get today's widget list (empty state)
2. ✅ Test with specific date parameter
3. ✅ Add nonexistent widget (error handling)
4. ✅ Add real widget to today's list
5. ✅ Test duplicate widget prevention
6. ✅ Remove widget from today's list
7. ✅ Verify changes in widget list

## 📊 Test Output

Tests provide detailed output including:
- ✅/❌ Pass/Fail status for each test
- 📊 Response status codes and headers
- 📋 Response data in JSON format
- 🔍 Detailed debugging information
- 📈 Summary of all test results

## 🔧 Test Configuration

### Environment Variables

Tests use the following configuration:
- `BASE_URL`: Backend server URL (default: `http://localhost:8000`)
- `API_PREFIX`: API prefix for dashboard endpoints (default: `/api/v1/dashboard`)
- `DEFAULT_USER_ID`: Default user for testing (default: `user_001`)

### Test Data

Tests automatically:
1. Fetch available widgets from the widgets API
2. Use real widget IDs for testing
3. Clean up after tests (remove added widgets)
4. Handle edge cases (nonexistent widgets, duplicates)

## 🐛 Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   ❌ Error: Connection refused
   ```
   **Solution**: Start the backend server with `python main.py`

2. **No Widgets Available**
   ```
   ⚠️  No widgets available for testing
   ```
   **Solution**: Generate test data with `python generate_dummy_data.py`

3. **Database Issues**
   ```
   ❌ Database error
   ```
   **Solution**: Check database connection and run `python init_db.py`

### Debug Mode

For detailed debugging, you can modify the test scripts to include more verbose output or add breakpoints.

## 📝 Adding New Tests

To add new test files:

1. Create a new test file following the naming convention: `test_<feature>_api.py`
2. Implement test functions with clear names and documentation
3. Add the test to `run_tests.py` in the `run_all_tests()` function
4. Update this README with the new test information

### Test File Template

```python
"""
Test script for [Feature] API functionality.
"""

import asyncio
import httpx
from typing import Dict, Any

async def test_feature_functionality() -> bool:
    """Test [feature] functionality."""
    # Implementation here
    pass

async def run_comprehensive_test():
    """Run comprehensive test suite for [feature] API."""
    # Test implementation here
    pass

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
```

## 🎯 Test Coverage

Current test coverage includes:
- ✅ API endpoint availability
- ✅ Request/response validation
- ✅ Error handling
- ✅ Business logic validation
- ✅ Edge case handling

Future improvements:
- 🔄 Database state verification
- 🔄 Performance testing
- 🔄 Load testing
- 🔄 Integration testing with frontend 