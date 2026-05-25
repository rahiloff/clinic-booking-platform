"""
API Smoke Tests.
Verifies critical pathways.
"""

import pytest
from httpx import AsyncClient
from app.core.security import create_access_token

pytestmark = pytest.mark.asyncio

async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_list_doctors_empty(client: AsyncClient):
    response = await client.get("/api/v1/doctors/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    # Empty DB, should be 0
    assert len(data["data"]) == 0

async def test_unauthorized_access(client: AsyncClient):
    # Missing token
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403 # FastAPI HTTPBearer returns 403 on missing

async def test_protected_route_with_mock_token(client: AsyncClient):
    # This token has a random user_id that doesn't exist in the DB
    token = create_access_token(subject="123e4567-e89b-12d3-a456-426614174000", role="patient")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/api/v1/auth/me", headers=headers)
    # Should be 401 Unauthorized because user isn't in the DB
    assert response.status_code == 401
