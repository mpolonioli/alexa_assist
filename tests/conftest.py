"""Fixtures for the Alexa Assist tests."""

from __future__ import annotations

import socket
import sys

import pytest

if sys.platform == "win32":
    # The HA test plugin blocks socket creation, but Windows event loops need an
    # internal loopback socket pair. Let socketpair() use the real socket class.
    import pytest_socket

    _orig_socketpair = socket.socketpair

    def _socketpair(*args, **kwargs):  # type: ignore[no-untyped-def]
        guarded = socket.socket
        socket.socket = pytest_socket._true_socket  # noqa: SLF001
        try:
            return _orig_socketpair(*args, **kwargs)
        finally:
            socket.socket = guarded

    socket.socketpair = _socketpair

from custom_components.alexa_assist.const import (
    CONF_AGENT,
    CONF_ANNOUNCE_LATE,
    CONF_DEADLINE,
    CONF_REMEMBER,
    CONF_SKILL_ID,
    CONF_VERIFY_SIGNATURE,
    DOMAIN,
    TITLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

pytest_plugins = "pytest_homeassistant_custom_component"

SKILL_ID = "amzn1.ask.skill.00000000-0000-0000-0000-000000000000"
AGENT_ID = "conversation.home_assistant"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom integrations in every test."""


@pytest.fixture(autouse=True)
async def setup_homeassistant(hass: HomeAssistant) -> None:
    """Set up the core component (exposed entities, intents) before each test."""
    assert await async_setup_component(hass, "homeassistant", {})


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry for the test skill."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={},
        options={
            CONF_SKILL_ID: SKILL_ID,
            CONF_AGENT: AGENT_ID,
            CONF_DEADLINE: 0.3,
            CONF_REMEMBER: True,
            CONF_ANNOUNCE_LATE: True,
            # The signed-request path is covered on its own; the protocol tests
            # would otherwise need a private key to sign with.
            CONF_VERIFY_SIGNATURE: False,
        },
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up the integration."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
