from datetime import datetime, timedelta
import os
import uuid
import pytest
import requests

@pytest.fixture(scope="session")
def base_url() -> str:
    """Single source of truth for where the API lives."""
    return os.environ.get("BASE_URL", "http://localhost:5000")

@pytest.fixture
def unique_username() -> str:
    """Fresh username per test, so re-runs never collide."""
    return f"testuser_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def credentials(unique_username: str) -> dict:
    return {"username": unique_username, "password": "password123"}

@pytest.fixture
def auth_headers(base_url: str, credentials: dict[str, str]) -> dict[str, str]:
    """Register a user, log in, return ready-to-use auth headers."""
    requests.post(f"{base_url}/api/auth/register", json=credentials)
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def event() -> dict[str, str|int|bool]:
    suffix = uuid.uuid4().hex[:8]
    return {
        "title": f"Test Event {suffix}",
        "description": f"A nice test description ({suffix})",
        "date": (datetime.now() + timedelta(days=30)).isoformat(),
        "location": "Online",
        "capacity": 30,
        "is_public": True,
        "requires_admin": False
    }