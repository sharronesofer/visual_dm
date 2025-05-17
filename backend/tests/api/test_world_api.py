import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_and_get_world():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create world
        resp = await ac.post("/api/worlds", json={"name": "TestWorld", "time": 0})
        assert resp.status_code == 201
        world_id = resp.json()["id"]
        # Get world
        resp = await ac.get(f"/api/worlds/{world_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "TestWorld"
        # Update world
        resp = await ac.put(f"/api/worlds/{world_id}", json={"name": "UpdatedWorld"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "UpdatedWorld"
        # Delete world
        resp = await ac.delete(f"/api/worlds/{world_id}")
        assert resp.status_code == 204 