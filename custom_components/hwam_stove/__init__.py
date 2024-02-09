"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""
import logging
from datetime import datetime, date, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.binary_sensor import DOMAIN as COMP_BINARY_SENSOR
from homeassistant.components.fan import DOMAIN as COMP_FAN
from homeassistant.components.sensor import DOMAIN as COMP_SENSOR
from homeassistant.const import (ATTR_DATE, ATTR_TIME, CONF_HOST,
                                 CONF_MONITORED_VARIABLES, CONF_NAME,
                                 EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

DOMAIN = 'hwam_stove'

ATTR_START_TIME = 'start_time'
ATTR_END_TIME = 'end_time'
ATTR_STOVE_NAME = 'stove_name'

DATA_HWAM_STOVE = 'hwam_stove'
DATA_PYSTOVE = 'pystove'
DATA_STOVES = 'stoves'

SERVICE_DISABLE_NIGHT_LOWERING = 'disable_night_lowering'
SERVICE_ENABLE_NIGHT_LOWERING = 'enable_night_lowering'
SERVICE_DISABLE_REMOTE_REFILL_ALARM = 'disable_remote_refill_alarm'
SERVICE_ENABLE_REMOTE_REFILL_ALARM = 'enable_remote_refill_alarm'
SERVICE_SET_CLOCK = 'set_clock'
SERVICE_SET_NIGHT_LOWERING_HOURS = 'set_night_lowering_hours'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        cv.string: vol.Schema({
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_MONITORED_VARIABLES, default=[]): vol.All(
                cv.ensure_list, [cv.string]),
        }),
    }, cv.ensure_list),
}, extra=vol.ALLOW_EXTRA)

# REQUIREMENTS = ['pystove']

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the HWAM Stove component."""
    from .pystove import pystove
    hass.data[DATA_HWAM_STOVE] = {
        DATA_STOVES: {},
        DATA_PYSTOVE: pystove,
    }
    conf = config[DOMAIN]
    for name, cfg in conf.items():
        stove_device = await StoveDevice.create(hass, name, cfg, config)
        hass.data[DATA_HWAM_STOVE][DATA_STOVES][name] = stove_device
    hass.async_create_task(register_services(hass))
    return True


async def register_services(hass):
    """Register HWAM Stove services."""

    service_set_night_lowering_hours_schema = vol.Schema({
        vol.Required(ATTR_STOVE_NAME): vol.All(
            cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])),
        vol.Optional(ATTR_START_TIME): cv.time,
        vol.Optional(ATTR_END_TIME): cv.time,
    }, cv.has_at_least_one_key(ATTR_START_TIME, ATTR_END_TIME))
    service_set_clock_schema = vol.Schema({
        vol.Required(ATTR_STOVE_NAME): vol.All(
            cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])),
        vol.Optional(ATTR_DATE, default=date.today()): cv.date,
        vol.Optional(ATTR_TIME, default=datetime.now().time()): cv.time,
    })
    service_basic_schema = vol.Schema({
        vol.Required(ATTR_STOVE_NAME): vol.All(
            cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])),
    })

    async def set_night_lowering_hours(call):
        """Set night lowering hours on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        attr_start = call.data.get(ATTR_START_TIME)
        attr_end = call.data.get(ATTR_END_TIME)
        await stove_device.stove.set_night_lowering_hours(attr_start, attr_end)
    hass.services.async_register(
        DOMAIN, SERVICE_SET_NIGHT_LOWERING_HOURS, set_night_lowering_hours,
        service_set_night_lowering_hours_schema)

    async def enable_night_lowering(call):
        """Enable night lowering."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_night_lowering(True)
    hass.services.async_register(
        DOMAIN, SERVICE_ENABLE_NIGHT_LOWERING, enable_night_lowering,
        service_basic_schema)

    async def disable_night_lowering(call):
        """Disable night lowering."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_night_lowering(False)
    hass.services.async_register(
        DOMAIN, SERVICE_DISABLE_NIGHT_LOWERING, disable_night_lowering,
        service_basic_schema)

    async def enable_remote_refill_alarm(call):
        """Enable remote refill alarm."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_remote_refill_alarm(True)
    hass.services.async_register(
        DOMAIN, SERVICE_ENABLE_REMOTE_REFILL_ALARM, enable_remote_refill_alarm,
        service_basic_schema)

    async def disable_remote_refill_alarm(call):
        """Disable remote refill alarm."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_remote_refill_alarm(False)
    hass.services.async_register(
        DOMAIN, SERVICE_DISABLE_REMOTE_REFILL_ALARM,
        disable_remote_refill_alarm, service_basic_schema)

    async def set_device_clock(call):
        """Set the clock on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        attr_date = call.data[ATTR_DATE]
        attr_time = call.data[ATTR_TIME]
        await stove_device.stove.set_time(
            datetime.combine(attr_date, attr_time))
    hass.services.async_register(
        DOMAIN, SERVICE_SET_CLOCK, set_device_clock, service_set_clock_schema)


class StoveDevice:
    """Abstract description of a stove component."""

    @classmethod
    async def create(cls, hass, name, stove_config, hass_config):
        """Create a stove component."""
        self = cls()
        self.pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
        self.hass = hass
        self.name = name
        self.config = stove_config
        self.signal = 'hwam_stove_update_{}'.format(self.config[CONF_HOST])
        self.stove = await self.pystove.Stove.create(self.config[CONF_HOST],
                                                     skip_ident=True)

        async def cleanup(event):
            """Clean up stove object."""
            await self.stove.destroy()
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, cleanup)
        hass.async_create_task(self.init_stove(hass_config))
        return self

    async def init_stove(self, hass_config):
        """Run ident routine and schedule updates."""
        self.hass.loop.create_task(self.stove._identify())
        self.hass.async_create_task(async_load_platform(
            self.hass, COMP_FAN, DOMAIN, self.name, hass_config))
        monitored_vars = self.config.get(CONF_MONITORED_VARIABLES)
        if monitored_vars:
            self.hass.async_create_task(
                self.setup_monitored_vars(monitored_vars, hass_config))
        self.hass.loop.create_task(self.update())
        async_track_time_interval(self.hass, self.update,
                                  timedelta(seconds=10))

    async def setup_monitored_vars(self, monitored_vars, hass_config):
        """Add monitored_vars as sensors and binary sensors."""
        pystove = self.pystove
        sensor_type_map = {
            COMP_BINARY_SENSOR: [
                pystove.DATA_MAINTENANCE_ALARMS,
                pystove.DATA_REFILL_ALARM,
                pystove.DATA_REMOTE_REFILL_ALARM,
                pystove.DATA_SAFETY_ALARMS,
                pystove.DATA_UPDATING,
            ],
            COMP_SENSOR: [
                pystove.DATA_ALGORITHM,
                pystove.DATA_BURN_LEVEL,
                pystove.DATA_MESSAGE_ID,
                pystove.DATA_NEW_FIREWOOD_ESTIMATE,
                pystove.DATA_NIGHT_BEGIN_TIME,
                pystove.DATA_NIGHT_END_TIME,
                pystove.DATA_NIGHT_LOWERING,
                pystove.DATA_OPERATION_MODE,
                pystove.DATA_OXYGEN_LEVEL,
                pystove.DATA_PHASE,
                pystove.DATA_REMOTE_VERSION,
                pystove.DATA_ROOM_TEMPERATURE,
                pystove.DATA_STOVE_TEMPERATURE,
                pystove.DATA_TIME_SINCE_REMOTE_MSG,
                pystove.DATA_DATE_TIME,
                pystove.DATA_TIME_TO_NEW_FIREWOOD,
                pystove.DATA_VALVE1_POSITION,
                pystove.DATA_VALVE2_POSITION,
                pystove.DATA_VALVE3_POSITION,
                pystove.DATA_FIRMWARE_VERSION,
            ]
        }
        binary_sensors = []
        sensors = []
        for var in monitored_vars:
            if var in sensor_type_map[COMP_SENSOR]:
                sensors.append(var)
            elif var in sensor_type_map[COMP_BINARY_SENSOR]:
                binary_sensors.append(var)
            else:
                _LOGGER.error("Monitored variable not supported: %s", var)
        if binary_sensors:
            self.hass.async_create_task(async_load_platform(
                self.hass, COMP_BINARY_SENSOR, DOMAIN,
                {'stove_name': self.name, 'sensors': binary_sensors},
                hass_config))
        if sensors:
            self.hass.async_create_task(async_load_platform(
                self.hass, COMP_SENSOR, DOMAIN,
                {'stove_name': self.name, 'sensors': sensors},
                hass_config))

    async def update(self, *_):
        """Update and dispatch stove info."""
        data = await self.stove.get_data()
        if data is None:
            _LOGGER.error("Got empty response, skipping dispatch.")
            return
        async_dispatcher_send(self.hass, self.signal, data)
