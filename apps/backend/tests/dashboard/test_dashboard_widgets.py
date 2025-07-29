import pytest
import requests

BASE_URL = "http://localhost:8000"

# Test widget creation
@pytest.mark.parametrize("widget_config", [
    {"title": "Daily Task Manager", "widget_type": "todo", "frequency": "daily", "category": "productivity", "importance": 5},
    {"title": "Research Assistant", "widget_type": "websearch", "frequency": "weekly", "category": "research", "importance": 3}
])
def test_create_dashboard_widget(widget_config):
    response = requests.post(f"{BASE_URL}/api/v1/widgets", json=widget_config)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == widget_config["title"]

# Test widget retrieval
def test_get_all_widgets():
    response = requests.get(f"{BASE_URL}/api/v1/widgets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0

# Test today's dashboard
def test_dashboard_today_flow():
    # 1. Ensure GET returns empty before generation
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/widgets/today")
    assert response.status_code == 200
    data = response.json()
    assert "widgets" in data
    assert isinstance(data["widgets"], list)
    # Should be empty before generation (unless previous test data exists)
    # 2. Generate today's widgets
    gen_response = requests.post(f"{BASE_URL}/api/v1/dashboard/widgets/today/ai_generate")
    assert gen_response.status_code == 200
    gen_data = gen_response.json()
    assert "widgets" in gen_data
    assert isinstance(gen_data["widgets"], list)
    assert gen_data["total_widgets"] > 0
    # 3. GET should now return generated widgets
    response2 = requests.get(f"{BASE_URL}/api/v1/dashboard/widgets/today")
    assert response2.status_code == 200
    data2 = response2.json()
    assert "widgets" in data2
    assert isinstance(data2["widgets"], list)
    assert data2["total_widgets"] == gen_data["total_widgets"]

# Test widget update
@pytest.mark.skip(reason="Requires widget id from creation test")
def test_update_dashboard_widget():
    # Example: update importance for a widget
    widget_id = "REPLACE_WITH_VALID_ID"
    update_data = {"importance": 10}
    response = requests.put(f"{BASE_URL}/api/v1/widgets/{widget_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["importance"] == 10

# Test widget deletion
@pytest.mark.skip(reason="Requires widget id from creation test")
def test_delete_dashboard_widget():
    widget_id = "REPLACE_WITH_VALID_ID"
    response = requests.delete(f"{BASE_URL}/api/v1/widgets/{widget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success", True)
