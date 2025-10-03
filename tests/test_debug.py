"""Minimal test to debug hanging issue"""


def test_minimal(client):
    """Minimal test."""
    response = client.get("/health")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_coffee_get_only(client):
    """Test only GET requests to coffee endpoint."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    print("✓ Coffee today GET passed")


def test_coffee_post_simple(client):
    """Test simple POST to coffee endpoint."""
    print("Starting POST test...")
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": 95},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    print(f"Response status: {response.status_code}")
    assert response.status_code == 200
    print("✓ Coffee POST passed")
