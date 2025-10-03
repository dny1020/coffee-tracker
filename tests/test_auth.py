"""Authentication tests."""


def test_health_no_auth_required(client):
    """Test health endpoint is public."""
    response = client.get("/health")
    assert response.status_code == 200


def test_root_no_auth_required(client):
    """Test root endpoint is public."""
    response = client.get("/")
    assert response.status_code == 200


def test_coffee_requires_auth(client):
    """Test coffee endpoints require auth."""
    response = client.get("/coffee/today")
    assert response.status_code == 403


def test_valid_api_key(client, auth_headers):
    """Test valid API key works."""
    response = client.get("/coffee/today", headers=auth_headers)
    assert response.status_code == 200


def test_invalid_api_key(client):
    """Test invalid API key fails."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "Bearer invalid-key"}
    )
    assert response.status_code == 401
