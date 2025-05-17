import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_login_and_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/auth/login", json={"username": "testuser", "password": "testpass"})
        assert resp.status_code == 200
        token = resp.json().get("access_token")
        assert token
        # Validate token by accessing protected endpoint
        resp = await ac.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        # Test permission denied
        resp = await ac.get("/api/admin/secret", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (401, 403) 