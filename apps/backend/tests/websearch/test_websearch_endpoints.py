import pytest
import requests

BASE_URL = "http://localhost:8000"

# Test creating websearch widget with search
@pytest.mark.parametrize("search_data", [
    {"title": "AI Development Research", "search_term": "FastAPI best practices and advanced features", "frequency": "weekly", "category": "development", "importance": 4}
])
def test_create_websearch_widget(search_data):
    response = requests.post(f"{BASE_URL}/api/v1/widgets/websearch/generateSearch", json=search_data)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "widget_id" in data
    assert "search_query_id" in data

# Test getting summaries (requires widget_id)
@pytest.mark.skip(reason="Requires widget_id from creation test")
def test_get_websearch_summaries():
    widget_id = "REPLACE_WITH_VALID_ID"
    response = requests.get(f"{BASE_URL}/api/v1/widgets/websearch/{widget_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
