import pytest
import requests

def test_health_endpoint():
    """Basic test for Health endpoint (GET /api/health)"""
    response = requests.get("http://localhost:8000/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
