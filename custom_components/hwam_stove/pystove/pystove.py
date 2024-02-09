# This file is part of pystove.
#
# pystove is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pystove is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pystove.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 Milan van Nugteren
#

import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, time, timedelta

import aiohttp

_LOGGER = logging.getLogger(__name__)

DATA_ALGORITHM = 'algorithm'
DATA_BEGIN_HOUR = 'begin_hour'
DATA_BEGIN_MINUTE = 'begin_minute'
DATA_ENABLE = 'enable'
DATA_END_HOUR = 'end_hour'
DATA_END_MINUTE = 'end_minute'
DATA_BURN_LEVEL = 'burn_level'
DATA_DATE_TIME = 'date_time'
DATA_FILENAME = 'file_name'
DATA_FIRMWARE_VERSION = 'firmware_version'
DATA_FIRMWARE_VERSION_BUILD = 'version_build'
DATA_FIRMWARE_VERSION_MAJOR = 'version_major'
DATA_FIRMWARE_VERSION_MINOR = 'version_minor'
DATA_IP = 'ip'
DATA_LEVEL = 'level'
DATA_MAINTENANCE_ALARMS = 'maintenance_alarms'
DATA_MESSAGE_ID = 'message_id'
DATA_MODE = 'mode'
DATA_NAME = 'name'
DATA_NEW_FIREWOOD_ESTIMATE = 'new_fire_wood_estimate'
DATA_NEW_FIREWOOD_HOURS = 'new_fire_wood_hours'
DATA_NEW_FIREWOOD_MINUTES = 'new_fire_wood_minutes'
DATA_NIGHT_BEGIN_HOUR = 'night_begin_hour'
DATA_NIGHT_BEGIN_MINUTE = 'night_begin_minute'
DATA_NIGHT_BEGIN_TIME = 'night_begin_time'
DATA_NIGHT_END_HOUR = 'night_end_hour'
DATA_NIGHT_END_MINUTE = 'night_end_minute'
DATA_NIGHT_END_TIME = 'night_end_time'
DATA_NIGHT_LOWERING = 'night_lowering'
DATA_OPERATION_MODE = 'operation_mode'
DATA_OXYGEN_LEVEL = 'oxygen_level'
DATA_PHASE = 'phase'
DATA_REFILL_ALARM = 'refill_alarm'
DATA_REMOTE_REFILL_ALARM = 'remote_refill_alarm'
DATA_REMOTE_VERSION = 'remote_version'
DATA_REMOTE_VERSION_BUILD = 'remote_version_build'
DATA_REMOTE_VERSION_MAJOR = 'remote_version_major'
DATA_REMOTE_VERSION_MINOR = 'remote_version_minor'
DATA_RESPONSE = 'response'
DATA_ROOM_TEMPERATURE = 'room_temperature'
DATA_SAFETY_ALARMS = 'safety_alarms'
DATA_SSID = 'ssid'
DATA_STOVE_TEMPERATURE = 'stove_temperature'
DATA_SUCCESS = 'success'
DATA_TEST_CONFIGURATION = 'configuration'
DATA_TEST_O2_SENSOR = 'o2_sensor'
DATA_TEST_TEMP_SENSOR = 't10_sensor'
DATA_TEST_VALVE1 = 'valve_primary'
DATA_TEST_VALVE2 = 'valve_secondary'
DATA_TEST_VALVE3 = 'valve_tertiary'
DATA_TIME_SINCE_REMOTE_MSG = 'time_since_remote_msg'
DATA_TIME_TO_NEW_FIREWOOD = 'time_to_new_fire_wood'
DATA_UPDATING = 'updating'
DATA_VALVE1_POSITION = 'valve1_position'
DATA_VALVE2_POSITION = 'valve2_position'
DATA_VALVE3_POSITION = 'valve3_position'

DATA_YEAR = 'year'
DATA_MONTH = 'month'
DATA_DAY = 'day'
DATA_HOURS = 'hours'
DATA_MINUTES = 'minutes'
DATA_SECONDS = 'seconds'

HTTP_HEADERS = {
    "Accept": "application/json"
}

MAINTENANCE_ALARMS = [
    'Stove Backup Battery Low',
    'O2 Sensor Fault',
    'O2 Sensor Offset',
    'Stove Temperature Sensor Fault',
    'Room Temperature Sensor Fault',
    'Communication Fault',
    'Room Temperature Sensor Battery Low',
]

NIGHT_LOWERING_STATES = [
    'Disabled',
    'Init',
    'Day',
    'Night',
    'Manual Night',
]

OPERATION_MODES = [
    'Init',
    'Self Test',
    'Normal',
    'Temperature Fault',
    'O2 Fault',
    'Calibration',
    'Safety',
    'Manual',
    'MotorTest',
    'Slow Combustion',
    'Low Voltage',
]

PHASE = [
    'Ignition',
    'Burn',
    'Burn',
    'Burn',
    'Glow',
    'Standby',
]

RESPONSE_OK = 'OK'

SAFETY_ALARMS = [
    'Valve Fault',
    'Valve Fault',
    'Valve Fault',
    'Bad Configuration',
    'Valve Disconnected',
    'Valve Disconnected',
    'Valve Disconnected',
    'Valve Calibration Error',
    'Valve Calibration Error',
    'Valve Calibration Error',
    'Chimney Overheat',
    'Door Open Too Long',
    'Manual Safety Alarm',
    'Stove Sensor Fault',
]

SELF_TEST_VALUES = [
    'Failed',
    'Passed',
    'Running',
    'Not Completed',
    'Not Started',
]

STOVE_ACCESSPOINT_URL = '/esp/get_current_accesspoint'
STOVE_BURN_LEVEL_URL = '/set_burn_level'
STOVE_DATA_URL = '/get_stove_data'
STOVE_ID_URL = '/esp/get_identification'
STOVE_LIVE_DATA_URL = '/get_live_data'
STOVE_NIGHT_LOWERING_OFF_URL = '/set_night_lowering_off'
STOVE_NIGHT_LOWERING_ON_URL = '/set_night_lowering_on'
STOVE_NIGHT_TIME_URL = '/set_night_time'
STOVE_OPEN_FILE_URL = '/open_file'
STOVE_READ_OPEN_FILE_URL = '/read_open_file'
STOVE_REMOTE_REFILL_ALARM_URL = '/set_remote_refill_alarm'
STOVE_SET_TIME_URL = '/set_time'
STOVE_SELFTEST_RESULT_URL = '/get_selftest_result'
STOVE_SELFTEST_START_URL = '/start_selftest'
STOVE_START_URL = '/start'

UNKNOWN = 'Unknown'


class Stove():
    """Abstraction of a Stove object."""

    @classmethod
    async def create(cls, stove_host, loop=asyncio.get_event_loop(),
                     skip_ident=False):
        """Async create the Stove object."""
        self = cls()
        self._loop = loop
        self.stove_host = stove_host
        self.algo_version = UNKNOWN
        self.name = UNKNOWN
        self.series = UNKNOWN
        self.stove_ip = UNKNOWN
        self.stove_ssid = UNKNOWN
        self._session = aiohttp.ClientSession(headers=HTTP_HEADERS)
        if not skip_ident:
            await self._identify()
        return self

    async def destroy(self):
        await self._session.close()

    async def get_data(self):
        """Call get_raw_data, process result before returning."""
        data = await self.get_raw_data()
        if data is None:
            return
        phase = PHASE[data[DATA_PHASE]]
        stove_datetime = datetime(data[DATA_YEAR], data[DATA_MONTH],
                                  data[DATA_DAY], data[DATA_HOURS],
                                  data[DATA_MINUTES], data[DATA_SECONDS])
        time_to_refuel = timedelta(hours=data[DATA_NEW_FIREWOOD_HOURS],
                                   minutes=data[DATA_NEW_FIREWOOD_MINUTES])
        refuel_estimate = stove_datetime + time_to_refuel
        maintenance_alarms = self._get_maintenance_alarms_text(
            data[DATA_MAINTENANCE_ALARMS])
        safety_alarms = self._get_safety_alarms_text(data[DATA_SAFETY_ALARMS])
        operation_mode = OPERATION_MODES[data[DATA_OPERATION_MODE]]
        night_lowering = NIGHT_LOWERING_STATES[data[DATA_NIGHT_LOWERING]]
        nighttime_start = time(hour=data[DATA_NIGHT_BEGIN_HOUR],
                               minute=data[DATA_NIGHT_BEGIN_MINUTE])
        nighttime_end = time(hour=data[DATA_NIGHT_END_HOUR],
                             minute=data[DATA_NIGHT_END_MINUTE])
        stove_version = "{}.{}.{}".format(data[DATA_FIRMWARE_VERSION_MAJOR],
                                          data[DATA_FIRMWARE_VERSION_MINOR],
                                          data[DATA_FIRMWARE_VERSION_BUILD])
        remote_version = "{}.{}.{}".format(data[DATA_REMOTE_VERSION_MAJOR],
                                           data[DATA_REMOTE_VERSION_MINOR],
                                           data[DATA_REMOTE_VERSION_BUILD])
        for item in (DATA_STOVE_TEMPERATURE, DATA_ROOM_TEMPERATURE,
                     DATA_OXYGEN_LEVEL):
            data[item] = int(data[item]/100)
        processed_data = {
            DATA_ALGORITHM: data[DATA_ALGORITHM],
            DATA_BURN_LEVEL: data[DATA_BURN_LEVEL],
            DATA_MAINTENANCE_ALARMS: maintenance_alarms,
            DATA_MESSAGE_ID: data[DATA_MESSAGE_ID],
            DATA_NEW_FIREWOOD_ESTIMATE: refuel_estimate,
            DATA_NIGHT_BEGIN_TIME: nighttime_start,
            DATA_NIGHT_END_TIME: nighttime_end,
            DATA_NIGHT_LOWERING: night_lowering,
            DATA_OPERATION_MODE: operation_mode,
            DATA_OXYGEN_LEVEL: data[DATA_OXYGEN_LEVEL],
            DATA_PHASE: phase,
            DATA_REFILL_ALARM: data[DATA_REFILL_ALARM],
            DATA_REMOTE_REFILL_ALARM: data[DATA_REMOTE_REFILL_ALARM],
            DATA_REMOTE_VERSION: remote_version,
            DATA_ROOM_TEMPERATURE: data[DATA_ROOM_TEMPERATURE],
            DATA_SAFETY_ALARMS: safety_alarms,
            DATA_STOVE_TEMPERATURE: data[DATA_STOVE_TEMPERATURE],
            DATA_TIME_SINCE_REMOTE_MSG: data[DATA_TIME_SINCE_REMOTE_MSG],
            DATA_DATE_TIME: stove_datetime,
            DATA_TIME_TO_NEW_FIREWOOD: time_to_refuel,
            DATA_UPDATING: data[DATA_UPDATING],
            DATA_VALVE1_POSITION: data[DATA_VALVE1_POSITION],
            DATA_VALVE2_POSITION: data[DATA_VALVE2_POSITION],
            DATA_VALVE3_POSITION: data[DATA_VALVE3_POSITION],
            DATA_FIRMWARE_VERSION: stove_version,
        }
        return processed_data

    async def get_live_data(self):
        """Get 'live' temp and o2 data from the last 2 hours."""
        bin_arr = bytearray(await self._get('http://' + self.stove_host
                                            + STOVE_LIVE_DATA_URL), 'utf-8')
        if len(bin_arr) != 120:
            _LOGGER.error("Got unexpected response from stove.")
            return
        data_out = {
            DATA_STOVE_TEMPERATURE: [],
            DATA_OXYGEN_LEVEL: [],
        }
        for i in range(120):
            data_out[DATA_STOVE_TEMPERATURE].append((
                bin_arr[i*4] << 4 | bin_arr[i*4+1] << 0 | bin_arr[i*4+2] << 12
                | bin_arr[i*4+3] << 8) / 100)
            data_out[DATA_OXYGEN_LEVEL].append((
                bin_arr[i*4+480] << 4 | bin_arr[i*4+481] << 0
                | bin_arr[i*4+482] << 12 | bin_arr[i*4+483] << 8) / 100)
        return data_out

    async def get_raw_data(self):
        """Request an update from the stove, return raw result."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_DATA_URL)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return
        data = json.loads(json_str)
        return data

    def self_test(self, delay=3, processed=True):
        """Return self test async generator."""
        return _SelfTest(self, delay, processed)

    async def set_burn_level(self, burn_level):
        """Set the desired burnlevel."""
        data = {DATA_LEVEL: burn_level}
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_BURN_LEVEL_URL, data)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_night_lowering(self, state=None):
        """Switch/toggle night lowering (True=on, False=off, None=toggle)."""
        if state is None:
            data = await self.get_raw_data()
            # 0 == Off
            # 2 == On outside night hours
            # 3 == On inside night hours
            # When does night_lowering == 1 happen?
            cur_state = data[DATA_NIGHT_LOWERING] > 0
        else:
            cur_state = not state
        url = (STOVE_NIGHT_LOWERING_OFF_URL if cur_state
               else STOVE_NIGHT_LOWERING_ON_URL)
        json_str = await self._get('http://' + self.stove_host + url)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_night_lowering_hours(self, start=None, end=None):
        """Set night lowering start and end time."""
        if start is None or end is None:
            data = await self.get_data()
        start = start or data[DATA_NIGHT_BEGIN_TIME]
        end = end or data[DATA_NIGHT_END_TIME]
        data = {
            DATA_BEGIN_HOUR: start.hour,
            DATA_BEGIN_MINUTE: start.minute,
            DATA_END_HOUR: end.hour,
            DATA_END_MINUTE: end.minute,
        }
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_NIGHT_TIME_URL, data)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_remote_refill_alarm(self, state=None):
        """Set or toggle remote_refill_alarm setting."""
        if state is None:
            data = await self.get_raw_data()
            cur_state = data[DATA_REMOTE_REFILL_ALARM] == 1
        else:
            cur_state = not state
        data = {DATA_ENABLE: 0 if cur_state else 1}
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_REMOTE_REFILL_ALARM_URL, data)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_time(self, new_time=datetime.now()):
        """Set the time and date of the stove."""
        data = {
            'year': new_time.year,
            'month': new_time.month - 1,  # Stove month input is 0 based.
            'day': new_time.day,
            'hours': new_time.hour,
            'minutes': new_time.minute,
            'seconds': new_time.second,
        }
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_SET_TIME_URL, data)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def start(self):
        """Start the ignition phase."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_START_URL)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def _identify(self):
        """Get identification and set the properties on the object."""

        async def get_name_and_ip():
            """Get stove name and IP."""
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_ID_URL)
            if json_str is None:
                _LOGGER.error("Got empty or no response from stove.")
                return
            stove_id = json.loads(json_str)
            if None in [stove_id.get(DATA_NAME), stove_id.get(DATA_IP)]:
                _LOGGER.warning("Unable to read stove name and/or IP.")
                return
            self.name = stove_id[DATA_NAME]
            self.stove_ip = stove_id[DATA_IP]

        async def get_ssid():
            """Get stove SSID."""
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_ACCESSPOINT_URL)
            if json_str is None:
                _LOGGER.error("Got empty or no response from stove.")
                return
            stove_ssid = json.loads(json_str).get(DATA_SSID)
            if stove_ssid is None:
                _LOGGER.warning("Unable to read stove SSID.")
                return
            self.stove_ssid = stove_ssid

        async def get_version_info():
            """Get stove version info."""
            data = {
                DATA_FILENAME: 'info.xml',
                DATA_MODE: 1
            }
            json_str = await self._post('http://' + self.stove_host
                                        + STOVE_OPEN_FILE_URL, data)
            if json_str is None:
                _LOGGER.error("Got empty or no response from stove.")
                return
            success = json.loads(json_str)
            if success[DATA_SUCCESS] == 1:
                xml_str = await self._post('http://' + self.stove_host
                                           + STOVE_READ_OPEN_FILE_URL, data)
                try:
                    xml_root = ET.fromstring(xml_str)
                    self.algo_version = xml_root.find('Name').text
                    self.series = xml_root.find('StoveType').text
                except ET.ParseError:
                    _LOGGER.warning("Invalid XML. Could not get version info.")
                except AttributeError:
                    _LOGGER.warning("Missing key in version info XML.")
            else:
                _LOGGER.warning("Unable to open stove version info file.")

        await asyncio.gather(*[
            get_name_and_ip(),
            get_ssid(),
            get_version_info(),
        ])

    async def _self_test_result(self):
        """Get self test result."""
        count = 0
        result = None
        while True:
            # Error prone, retry up to 3 times
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_SELFTEST_RESULT_URL)
            if json_str is None:
                _LOGGER.error("Got empty or no response from stove.")
                continue
            result = json.loads(json_str)
            if not result.get('reponse'):  # NOT A TYPO!!!
                break
            if count >= 3:
                return
            count = count + 1
            await asyncio.sleep(3)
        return result

    async def _self_test_start(self):
        """Request self test start."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_SELFTEST_START_URL)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    def _get_maintenance_alarms_text(self, bitmask):
        """Process maintenance alarms bitmask, return a list of strings."""
        num_alarms = len(MAINTENANCE_ALARMS)
        ret = []
        for i in range(num_alarms):
            if 1 << i & bitmask:
                ret.append(MAINTENANCE_ALARMS[i])
        return ret

    def _get_safety_alarms_text(self, bitmask):
        """Process safety alarms bitmask, return a list of strings."""
        num_alarms = len(SAFETY_ALARMS)
        ret = []
        for i in range(num_alarms):
            if 1 << i & bitmask:
                ret.append(SAFETY_ALARMS[i])
        return ret

    async def _get(self, url):
        """Get data from url, return response."""
        try:
            async with self._session.get(url) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")

    async def _post(self, url, data):
        """Post data to url, return response."""
        try:
            async with self._session.post(url, data=json.dumps(
                    data, separators=(',', ':'))) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")


class _SelfTest:
    """Self test async generator."""

    def __init__(self, stove, delay, processed=True):
        self.stove = stove
        self.delay = delay
        self.processed = processed
        self.test_started = False
        self.test_finished = False

    def __aiter__(self):
        return self

    async def __anext__(self):

        async def get_result():
            """Get intermediate test results."""

            def process_dict(in_dict):
                """Process dict values."""
                if not self.processed:
                    return in_dict
                out_dict = {}
                for k, v in in_dict.items():
                    out_dict[k] = SELF_TEST_VALUES[v]
                return out_dict

            intermediate_raw = await self.stove._self_test_result()
            if intermediate_raw is None:
                return None
            else:
                intermediate = process_dict(intermediate_raw)
                if 2 not in intermediate_raw.values():
                    self.test_finished = True
                return intermediate

        if not self.test_started:
            if await self.stove._self_test_start():
                self.test_started = True
                return await get_result()
            else:
                raise StopAsyncIteration
        if self.test_finished:
            raise StopAsyncIteration

        await asyncio.sleep(self.delay)
        return await get_result()
