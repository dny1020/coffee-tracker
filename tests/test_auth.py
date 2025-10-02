"""Tests for authentication and security"""


def test_health_no_auth_required(client):
    """Test that health endpoint doesn't require auth."""
    response = client.get("/health")
    assert response.status_code == 200


def test_root_no_auth_required(client):
    """Test that root endpoint doesn't require auth."""
    response = client.get("/")
    assert response.status_code == 200


def test_coffee_requires_auth(client):
    """Test that coffee endpoints require auth."""
    response = client.get("/coffee/today")
    assert response.status_code == 403


def test_heartrate_requires_auth(client):
    """Test that heartrate endpoints require auth."""
    response = client.get("/heartrate/current")
    assert response.status_code == 403


def test_valid_api_key(client):
    """Test that valid API key works."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200


def test_invalid_api_key(client):
    """Test that invalid API key fails."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "Bearer invalid-key"}
    )
    assert response.status_code == 401


def test_missing_bearer_prefix(client):
    """Test that missing Bearer prefix fails."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 403


def test_security_headers_present(client):
    """Test that security headers are present."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    assert "X-Request-ID" in headers
    assert "X-Process-Time" in headers
