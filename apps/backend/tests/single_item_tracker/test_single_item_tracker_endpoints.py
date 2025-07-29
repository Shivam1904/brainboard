import pytest
import requests

BASE_URL = "http://localhost:8000"

# Test creating tracker widget
@pytest.mark.parametrize("tracker_config", [
    {"title": "Weight Tracker", "widget_type": "singleitemtracker", "frequency": "daily", "category": "health", "importance": 4}
])
def test_create_tracker_widget(tracker_config):
    response = requests.post(f"{BASE_URL}/api/v1/widgets", json=tracker_config)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == tracker_config["title"]

# Test creating tracker entry (requires tracker_id)
@pytest.mark.skip(reason="Requires tracker_id from creation test")
def test_create_tracker_entry():
    tracker_id = "REPLACE_WITH_VALID_ID"
    entry_data = {"value": "74.8", "notes": "Morning weigh-in after workout"}
    response = requests.post(f"{BASE_URL}/api/v1/widgets/single-item-tracker/{tracker_id}/entry", json=entry_data)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data
