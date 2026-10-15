"""The Alexa Assist integration.

Serves an Alexa custom skill endpoint so Echo devices can talk to any Home
Assistant assistant. Alexa keeps the wake word, the speech recognition and the
voice; Home Assistant runs the assistant's intent stage.
"""

from __future__ import annotations

from homeassistant.components.assist_pipeline import async_get_pipeline, async_get_pipelines
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .alexa import async_setup_view
from .const import CONF_AGENT, CONF_ASSISTANT, DEFAULT_ASSISTANT, DOMAIN, LOGGER

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


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Move older entries to the current options."""
    if entry.version > 1:
        return False

    if entry.minor_version < 2:
        # 1.2 answers through an assistant instead of a bare conversation agent.
        options = dict(entry.options)
        assistant = _async_assistant_for_agent(hass, options.pop(CONF_AGENT, None))
        options[CONF_ASSISTANT] = assistant
        hass.config_entries.async_update_entry(entry, options=options, minor_version=2)
        LOGGER.info("Alexa now answers through assistant %s", assistant)

    return True


@callback
def _async_assistant_for_agent(hass: HomeAssistant, agent: str | None) -> str:
    """Return the assistant that answers with the agent an entry used to call.

    The preferred assistant wins when it uses that agent, then any other one.
    When no assistant does, the agent id itself is kept: Home Assistant runs a
    conversation entity as a plain assistant, so Alexa keeps answering as before.
    """
    if not agent:
        return DEFAULT_ASSISTANT

    preferred = async_get_pipeline(hass)
    for pipeline in (preferred, *async_get_pipelines(hass)):
        if pipeline.conversation_engine == agent:
            return pipeline.id

    LOGGER.warning(
        "No assistant answers with %s, so Alexa keeps calling it directly. Pick an "
        "assistant in the Alexa Assist options to use its settings",
        agent,
    )
    return agent
