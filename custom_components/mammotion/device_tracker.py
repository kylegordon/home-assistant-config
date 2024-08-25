from __future__ import annotations
import logging
from typing import Any

from cryptography.utils import cached_property
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MammotionConfigEntry
from .const import ATTR_DIRECTION
from .coordinator import MammotionDataUpdateCoordinator
from .entity import MammotionBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MammotionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RTK tracker from config entry."""
    coordinator = config_entry.runtime_data

    async_add_entities(
       [MammotionTracker(coordinator)]
        )


class MammotionTracker(MammotionBaseEntity, TrackerEntity):
    """Mammotion device tracker."""

    _attr_force_update = False
    _attr_translation_key = "device_tracker"
    _attr_icon = "mdi:car"

    def __init__(
        self,
        coordinator: MammotionDataUpdateCoordinator
    ) -> None:
        """Initialize the Tracker."""
        super().__init__(coordinator, f"{coordinator.device_name}_gps")

        self._attr_name = coordinator.device_name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_DIRECTION: self.coordinator.device.luba_msg.location.orientation}

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self.coordinator.device.luba_msg.location.device.latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self.coordinator.device.luba_msg.location.device.longitude

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        return self.coordinator.data.report_data.dev.battery_val

    @property
    def source_type(self) -> SourceType:
        """Return the source type, e.g., GPS or router, of the device."""
        return SourceType.GPS
