"""Coffee endpoint tests."""


def test_log_coffee_valid(client, auth_headers):
    """Test logging valid coffee entry."""
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": 95, "coffee_type": "espresso"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["caffeine_mg"] == 95


def test_log_coffee_invalid(client, auth_headers):
    """Test invalid caffeine amount."""
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": -10},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_today_caffeine(client, auth_headers):
    """Test getting today's caffeine."""
    response = client.get("/coffee/today", headers=auth_headers)
    assert response.status_code == 200
    assert "total_caffeine_mg" in response.json()
