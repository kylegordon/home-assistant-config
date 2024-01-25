"""
Hwam stove fan entity.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""
import logging

from homeassistant.components.fan import DOMAIN, SUPPORT_SET_SPEED, FanEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import slugify

from custom_components.hwam_stove import (DATA_HWAM_STOVE, DATA_PYSTOVE,
                                          DATA_STOVES)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HWAM stove device."""
    stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES][discovery_info]
    stove = StoveBurnLevel(hass, stove_device)
    async_add_entities([stove])


class StoveBurnLevel(FanEntity):
    """Representation of a fan."""

    def __init__(self, hass, stove_device):
        self._pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
        self._burn_level = 0
        self._state = False
        self._stove_device = stove_device
        self._device_name = slugify('burn_level_{}'.format(stove_device.name))
        self.entity_id = '{}.{}'.format(DOMAIN, self._device_name)
        self._icon = 'mdi:fire'

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        async_dispatcher_connect(self.hass, self._stove_device.signal,
                                 self.receive_report)

    async def receive_report(self, data):
        """Receive updates."""
        self._burn_level = data[self._pystove.DATA_BURN_LEVEL]
        self._state = data[self._pystove.DATA_PHASE] != self._pystove.PHASE[5]
        self.async_schedule_update_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        await self._stove_device.stove.set_burn_level(int(percentage/20))

    async def async_turn_on(self, speed: str = None, **kwargs):
        """Turn on the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        if not self._state:
            await self._stove_device.stove.start()

    async def async_turn_off(self, **kwargs):
        """Disable turn off."""
        pass

    @property
    def is_on(self):
        """Return true if the entity is on."""
        return self._state

    @property
    def percentage(self) -> int:
        """Return the current speed."""
        return self._burn_level * 20;

    @property
    def speed_count(self) -> int:
        """Get the list of available speeds."""
        return 5

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    @property
    def icon(self) -> str:
        """Set the icon."""
        return self._icon

    @property
    def name(self) -> str:
        """Set the friendly name."""
        return 'Burn Level {}'.format(self._stove_device.stove.name)

    @property
    def should_poll(self) -> str:
        """Return False because entity pushes its state."""
        return False
