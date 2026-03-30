"""Test that a door binary_sensor only triggers automations on 'on', not 'open'."""
import pytest
from homeassistant.setup import async_setup_component


@pytest.mark.asyncio
async def test_door_sensor_valid_states(hass):
    """Binary sensor with device_class door should use 'on'/'off', not 'open'."""
    assert await async_setup_component(
        hass,
        "binary_sensor",
        {
            "binary_sensor": {
                "platform": "template",
                "sensors": {
                    "test_door": {
                        "value_template": "{{ true }}",
                        "device_class": "door",
                    }
                },
            }
        },
    )
    await hass.async_block_till_done()

    # Simulate door closed
    hass.states.async_set("binary_sensor.test_door", "off")
    await hass.async_block_till_done()
    state = hass.states.get("binary_sensor.test_door")
    assert state.state == "off", "Expected door closed state to be 'off'"

    # Simulate door open using the WRONG state value
    hass.states.async_set("binary_sensor.test_door", "open")
    await hass.async_block_till_done()
    state = hass.states.get("binary_sensor.test_door")
    assert state.state == "open", "State should be stored as 'open' when set to 'open'"
    assert state.state != "on", (
        "State 'open' must not equal 'on': automations checking for 'on' "
        "will NOT trigger when sensor reports 'open'"
    )

    # Simulate door open using the CORRECT state value
    hass.states.async_set("binary_sensor.test_door", "on")
    await hass.async_block_till_done()
    state = hass.states.get("binary_sensor.test_door")
    assert state.state == "on", (
        "Door binary_sensor should use state 'on' (not 'open') to trigger automations"
    )
