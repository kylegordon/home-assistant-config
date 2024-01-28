"""
Support for HWAM Stove sensors.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""
import logging

from datetime import datetime, timedelta

from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import async_generate_entity_id

from custom_components.hwam_stove import (DATA_HWAM_STOVE, DATA_PYSTOVE,
                                          DATA_STOVES)

DEPENDENCIES = ['hwam_stove']
UNIT_PERCENT = '%'
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the HWAM Stove sensors."""
    if discovery_info is None:
        return
    pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
    sensor_info = {
        # {name: [device_class, unit, friendly_name format]}
        pystove.DATA_ALGORITHM: [
            None, None, "Algorithm {}"],
        pystove.DATA_BURN_LEVEL: [
            None, None, "Burn Level {}"],
        pystove.DATA_MAINTENANCE_ALARMS: [
            None, None, "Maintenance Alarms {}"],
        pystove.DATA_MESSAGE_ID: [
            None, None, "Message ID {}"],
        pystove.DATA_NEW_FIREWOOD_ESTIMATE: [
            None, None, "New Firewood Estimate {}"],
        pystove.DATA_NIGHT_BEGIN_TIME: [
            None, None, "Night Begin Time {}"],
        pystove.DATA_NIGHT_END_TIME: [
            None, None, "Night End Time {}"],
        pystove.DATA_NIGHT_LOWERING: [
            None, None, "Night Lowering {}"],
        pystove.DATA_OPERATION_MODE: [
            None, None, "Operation Mode {}"],
        pystove.DATA_OXYGEN_LEVEL: [
            None, UNIT_PERCENT, "Oxygen Level {}"],
        pystove.DATA_PHASE: [
            None, None, "Phase {}"],
        pystove.DATA_REMOTE_VERSION: [
            None, None, "Remote Version {}"],
        pystove.DATA_ROOM_TEMPERATURE: [
            DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, "Room Temperature {}"],
        pystove.DATA_SAFETY_ALARMS: [
            None, None, "Safety Alarms {}"],
        pystove.DATA_STOVE_TEMPERATURE: [
            DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, "Stove Temperature {}"],
        pystove.DATA_TIME_SINCE_REMOTE_MSG: [
            None, None, "Time Since Remote Message {}"],
        pystove.DATA_DATE_TIME: [
            None, None, "Date and time {}"],
        pystove.DATA_TIME_TO_NEW_FIREWOOD: [
            None, None, "Time To New Firewood {}"],
        pystove.DATA_VALVE1_POSITION: [
            None, None, "Valve 1 Postition {}"],
        pystove.DATA_VALVE2_POSITION: [
            None, None, "Valve 2 Postition {}"],
        pystove.DATA_VALVE3_POSITION: [
            None, None, "Valve 3 Postition {}"],
        pystove.DATA_FIRMWARE_VERSION: [
            None, None, "Firmware Version {}"],
    }
    stove_name = discovery_info['stove_name']
    stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES][stove_name]
    sensor_list = discovery_info['sensors']
    sensors = []
    for var in sensor_list:
        device_class = sensor_info[var][0]
        unit = sensor_info[var][1]
        name_format = sensor_info[var][2]
        entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, "{}_{}".format(var, stove_device.name),
            hass=hass)
        sensors.append(
            HwamStoveSensor(entity_id, stove_device, var, device_class, unit,
                            name_format))
    async_add_entities(sensors)


class HwamStoveSensor(SensorEntity):
    """Representation of a HWAM Stove sensor."""

    def __init__(self, entity_id, stove_device, var, device_class, unit,
                 name_format):
        """Initialize the sensor."""
        self._stove_device = stove_device
        self.entity_id = entity_id
        self._var = var
        self._value = None
        self._device_class = device_class
        self._unit = unit
        self._name_format = name_format

    async def async_added_to_hass(self):
        """Subscribe to updates from the component."""
        _LOGGER.debug("Added HWAM Stove sensor %s", self.entity_id)
        async_dispatcher_connect(self.hass, self._stove_device.signal,
                                 self.receive_report)

    async def receive_report(self, status):
        """Handle status updates from the component."""
        value = status.get(self._var)
        pystove = self.hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
        if (status.get(pystove.DATA_PHASE) != pystove.PHASE[4]
                and self._var in [pystove.DATA_NEW_FIREWOOD_ESTIMATE,
                                  pystove.DATA_TIME_TO_NEW_FIREWOOD]):
            value = "Wait for Glow phase..."
        elif isinstance(value, datetime):
            value = value.strftime('%-d %b, %-H:%M')
        elif isinstance(value, timedelta):
            value = '{}'.format(value)
        self._value = value
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        """Return the friendly name of the sensor."""
        return self._name_format.format(self._stove_device.stove.name)

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def native_value(self):
        """Return the state of the device."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def should_poll(self):
        """Return False because entity pushes its state."""
        return False
