"""Pytest configuration and shared fixtures for Home Assistant config tests."""
import asyncio
import pytest
from homeassistant import core as ha


@pytest.fixture
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def hass(tmp_path, event_loop):
    """Create a minimal Home Assistant instance for testing."""
    hass_instance = ha.HomeAssistant(str(tmp_path))
    await hass_instance.async_start()
    yield hass_instance
    await hass_instance.async_stop(force=True)
