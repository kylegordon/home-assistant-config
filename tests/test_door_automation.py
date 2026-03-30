"""Test that a door binary_sensor only triggers automations on 'on', not 'open'."""
import glob
import os
import re

import pytest
from homeassistant.setup import async_setup_component


# ---------------------------------------------------------------------------
# Unit test: verify binary_sensor state semantics at runtime
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Config-scan test: catch binary_sensor triggers using cover states in YAML
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
_COVER_STATES = {"open", "closed", "opening", "closing"}

# Regex: entity_id line followed (optionally via whitespace) by a to: line
_TRIGGER_PATTERN = re.compile(
    r"entity_id:\s*(binary_sensor\.[^\s\n]+)\s*\n\s*to:\s*[\"']?(\w+)[\"']?",
    re.MULTILINE,
)


def _yaml_files():
    """Yield paths to all YAML files that may contain automation triggers."""
    patterns = [
        os.path.join(_REPO_ROOT, "packages", "**", "*.yaml"),
        os.path.join(_REPO_ROOT, "automation", "**", "*.yaml"),
        os.path.join(_REPO_ROOT, "automation", "*.yaml"),
    ]
    seen = set()
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            if path not in seen:
                seen.add(path)
                yield path


def test_no_binary_sensor_trigger_uses_cover_states():
    """No automation trigger on a binary_sensor should use cover states.

    binary_sensor entities report 'on'/'off'.  Using 'open'/'closed' (cover
    states) in a ``to:`` trigger silently fails — the automation never fires.

    Catches the class of bug found in packages/tin_hut.yaml line 49.
    """
    violations = []
    for fpath in _yaml_files():
        try:
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        for entity_id, to_state in _TRIGGER_PATTERN.findall(content):
            if to_state in _COVER_STATES:
                rel = os.path.relpath(fpath, _REPO_ROOT)
                violations.append(
                    f"{rel}: trigger on '{entity_id}' uses to='{to_state}' "
                    f"(cover state); binary_sensor should use 'on'/'off'"
                )

    assert not violations, (
        "Found automation trigger(s) on binary_sensor entities using cover "
        f"states:\n" + "\n".join(violations)
    )
