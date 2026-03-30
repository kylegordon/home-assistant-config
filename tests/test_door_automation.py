"""Test that a door binary_sensor only uses 'on'/'off', never 'open'.

Home Assistant always represents binary_sensor states as 'on' or 'off',
regardless of device_class. Automations must use 'to: on', not 'to: open'.
"""
import pytest
from homeassistant.setup import async_setup_component


@pytest.mark.asyncio
async def test_door_sensor_valid_states(hass):
    """Binary sensor with device_class door uses 'on'/'off', not 'open'."""
    # Set up input_boolean to drive the template sensor state
    assert await async_setup_component(
        hass,
        "input_boolean",
        {
            "input_boolean": {
                "door_open": {}
            }
        },
    )
    await hass.async_block_till_done()

    # Set up template binary_sensor that mirrors the input_boolean
    assert await async_setup_component(
        hass,
        "binary_sensor",
        {
            "binary_sensor": {
                "platform": "template",
                "sensors": {
                    "test_door": {
                        "value_template": (
                            "{{ is_state('input_boolean.door_open', 'on') }}"
                        ),
                        "device_class": "door",
                    }
                },
            }
        },
    )
    await hass.async_block_till_done()

    # When input_boolean is off, sensor should be off (not 'closed' or 'open')
    hass.states.async_set("input_boolean.door_open", "off")
    await hass.async_block_till_done()
    state = hass.states.get("binary_sensor.test_door")
    assert state is not None
    assert state.state == "off", "Expected door sensor to be 'off'"
    assert state.state != "open", (
        "binary_sensor must never report 'open'; "
        "automations using 'to: open' will silently never trigger"
    )

    # When input_boolean is on, sensor should be on (not 'open')
    hass.states.async_set("input_boolean.door_open", "on")
    await hass.async_block_till_done()
    state = hass.states.get("binary_sensor.test_door")
    assert state is not None
    assert state.state == "on", "Expected door sensor to be 'on'"
    assert state.state != "open", (
        "binary_sensor must never report 'open' even when door is open; "
        "automations using 'to: open' will silently never trigger"
    )
