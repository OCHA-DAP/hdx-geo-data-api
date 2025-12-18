import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import app as fastapi_app

os.environ.setdefault("MIXPANEL_TOKEN", "fake_token")


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    """Create an instance of AsyncClient for testing FastAPI app."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
