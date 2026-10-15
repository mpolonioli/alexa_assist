"""The Alexa Assist integration.

Serves an Alexa custom skill endpoint so Echo devices can talk to any Home
Assistant conversation agent. Alexa keeps the wake word, the speech recognition
and the voice; Home Assistant only runs the agent.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .alexa import async_setup_view
from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alexa Assist from a config entry."""
    # Views cannot be unregistered: the endpoint reads the loaded entry on every
    # request, so options apply at once and an unloaded entry answers 404.
    async_setup_view(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
