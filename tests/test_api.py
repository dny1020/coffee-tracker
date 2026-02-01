"""Simple API tests for CI/CD"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200


def test_docs_endpoint():
    """Test API docs are accessible"""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
