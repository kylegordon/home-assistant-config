"""
Support for HWAM Stove sensors.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import logging
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ID,
    PERCENTAGE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveSensorEntityDescription(
    SensorEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove sensor entity."""

    state_func: Callable[
        [dict, str], str | int | float | date | datetime | Decimal | None
    ] = lambda data, key: data[key]


NIGHT_LOWERING_STATES_LOOKUP = dict(
    zip(
        pystove.NIGHT_LOWERING_STATES,
        [
            "disabled",
            "init",
            "on_day",
            "on_night",
            "on_manual_night",
        ],
    )
)

OPERATION_MODES_LOOKUP = dict(
    zip(
        pystove.OPERATION_MODES,
        [
            "init",
            "self_test",
            "normal",
            "temperature_fault",
            "o2_fault",
            "calibration",
            "safety",
            "manual",
            "motor_test",
            "slow_combustion",
            "low_voltage",
        ],
    )
)

PHASE_LOOKUP = dict(
    zip(
        pystove.PHASE,
        [
            "ignition",
            "burn",
            "burn",
            "burn",
            "glow",
            "standby",
        ],
    )
)


SENSOR_DESCRIPTIONS = [
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_ALGORITHM,
        translation_key="algorithm",
        device_identifier=StoveDeviceIdentifier.STOVE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:function-variant",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_MESSAGE_ID,
        translation_key="message_id",
        device_identifier=StoveDeviceIdentifier.STOVE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:message-processing",
        entity_registry_enabled_default=False,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NEW_FIREWOOD_ESTIMATE,
        translation_key="new_firewood_estimate",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.TIMESTAMP,
        state_func=lambda data, key: (
            datetime.combine(
                data[key].date(), data[key].time(), dt.get_default_time_zone()
            )
            if data[pystove.DATA_PHASE] == pystove.PHASE[4]
            else None
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NIGHT_LOWERING,
        translation_key="night_lowering",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.ENUM,
        options=[value for value in NIGHT_LOWERING_STATES_LOOKUP.values()],
        state_func=lambda data, key: NIGHT_LOWERING_STATES_LOOKUP.get(data[key]),
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:theme-light-dark",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_OPERATION_MODE,
        translation_key="operation_mode",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.ENUM,
        options=[value for value in OPERATION_MODES_LOOKUP.values()],
        state_func=lambda data, key: OPERATION_MODES_LOOKUP.get(data[key]),
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:cogs",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_OXYGEN_LEVEL,
        translation_key="oxygen_level",
        device_identifier=StoveDeviceIdentifier.STOVE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_PHASE,
        translation_key="phase",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.ENUM,
        options=[value for value in PHASE_LOOKUP.values()],
        state_func=lambda data, key: PHASE_LOOKUP.get(data[key]),
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:progress-star-four-points",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_ROOM_TEMPERATURE,
        translation_key="room_temperature",
        device_identifier=StoveDeviceIdentifier.REMOTE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_STOVE_TEMPERATURE,
        translation_key="stove_temperature",
        device_identifier=StoveDeviceIdentifier.STOVE,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_TIME_SINCE_REMOTE_MSG,
        translation_key="time_since_remote_message",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=2,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_TIME_TO_NEW_FIREWOOD,
        translation_key="time_to_new_firewood",
        device_identifier=StoveDeviceIdentifier.STOVE,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_func=lambda data, key: data[key].seconds,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=2,
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE1_POSITION,
        translation_key="valve_1_position",
        device_identifier=StoveDeviceIdentifier.STOVE,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:valve",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE2_POSITION,
        translation_key="valve_2_position",
        device_identifier=StoveDeviceIdentifier.STOVE,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:valve",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE3_POSITION,
        translation_key="valve_3_position",
        device_identifier=StoveDeviceIdentifier.STOVE,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:valve",
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove sensors."""
    stove_device = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveSensor(
            stove_device,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class HwamStoveSensor(HWAMStoveCoordinatorEntity, SensorEntity):
    """Representation of a HWAM Stove sensor."""

    entity_description: HWAMStoveSensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle status updates from the component."""
        self._attr_native_value = self.entity_description.state_func(
            self.coordinator.data, self.entity_description.key
        )
        self.async_write_ha_state()
