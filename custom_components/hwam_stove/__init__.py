"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from asyncio import CancelledError
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry, ConfigEntryNotReady
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_MONITORED_VARIABLES,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from pystove import Stove

from .const import DATA_STOVES, DOMAIN
from .coordinator import StoveCoordinator

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                cv.string: vol.Schema(
                    {
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_NAME): cv.string,
                        vol.Optional(CONF_MONITORED_VARIABLES, default=[]): vol.All(
                            cv.ensure_list, [cv.string]
                        ),
                    }
                ),
            },
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DATETIME,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the HWAM Stove component from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {DATA_STOVES: {}}

    try:
        stove = await Stove.create(config_entry.data[CONF_HOST])
    except (CancelledError, TimeoutError) as e:
        raise ConfigEntryNotReady() from e

    stove_hub = StoveCoordinator(hass, stove, config_entry)
    hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]] = stove_hub

    await stove_hub.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HWAM Stove component."""
    if DOMAIN in config:
        ir.async_create_issue(
            hass,
            DOMAIN,
            "deprecated_import_from_configuration_yaml",
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="deprecated_import_from_configuration_yaml",
        )
    if not hass.config_entries.async_entries(DOMAIN) and DOMAIN in config:
        conf = config[DOMAIN]
        for device_id, device_config in conf.items():
            device_config[CONF_NAME] = device_id

            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=device_config
                )
            )
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload the HWAM Stove component from a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        stove_hub = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
        await stove_hub.stove.destroy()

        hass.data[DOMAIN][DATA_STOVES].pop(config_entry.data[CONF_ID])
        if hass.data[DOMAIN][DATA_STOVES] == {}:
            hass.data[DOMAIN].pop(DATA_STOVES)
            # DATA_STOVES is the only key in hass.data[DOMAIN] at the moment...
            hass.data.pop(DOMAIN)

    return unload_ok
