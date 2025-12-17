import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.db.session import AsyncSessionLocal


@pytest.fixture
async def client():
    """Test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """Test DB session"""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_health(client):
    """Test health endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    assert "endpoints" in response.json()
