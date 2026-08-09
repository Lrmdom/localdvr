import pytest
from fastapi.testclient import TestClient
from src.api import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("src.api.settings")
def test_get_cameras(mock_settings):
    mock_cam = MagicMock()
    mock_cam.name = "test_cam"
    mock_settings.cameras = [mock_cam]
    
    response = client.get("/api/cameras")
    assert response.status_code == 200
    assert response.json() == ["test_cam"]

@patch("src.api.uploader")
def test_get_videos_empty(mock_uploader):
    mock_uploader.list_objects.return_value = []
    
    response = client.get("/api/videos?camera=test&date=2024-01-01")
    assert response.status_code == 200
    assert response.json() == []
