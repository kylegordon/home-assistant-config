#!/usr/bin/env python3
"""Monkey patch HA helpers as workaround for hass.data KeyError bugs, then run config check."""

import subprocess
import sys


def apply_patch(filepath, search, replace):
    """Apply a text patch to a file; silently skip if pattern absent or file missing."""
    try:
        with open(filepath) as f:
            content = f.read()
        if search in content:
            with open(filepath, "w") as f:
                f.write(content.replace(search, replace))
            print(f"Patch applied to {filepath}", flush=True)
        else:
            print(f"Patch pattern not found in {filepath} - may already be fixed upstream", flush=True)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found - skipping patch", flush=True)


# Workaround for https://github.com/home-assistant/core/issues/167066
# Patch _register_trigger_platform to initialise hass.data dicts before accessing them.
# NOTE: SEARCH matches the exact indentation/formatting from HA core.
# If upstream reformats the code this pattern may need updating.
apply_patch(
    "/usr/src/homeassistant/homeassistant/helpers/trigger.py",
    "    new_triggers: set[str] = set()\n    triggers = hass.data[TRIGGERS]",
    (
        "    new_triggers: set[str] = set()\n"
        "    if TRIGGERS not in hass.data:\n"
        "        hass.data[TRIGGERS] = {}\n"
        "    if TRIGGER_PLATFORM_SUBSCRIPTIONS not in hass.data:\n"
        "        hass.data[TRIGGER_PLATFORM_SUBSCRIPTIONS] = []\n"
        "    triggers = hass.data[TRIGGERS]"
    ),
)

# Same bug in _register_condition_platform (condition.py) - KeyError: 'conditions'
apply_patch(
    "/usr/src/homeassistant/homeassistant/helpers/condition.py",
    "    new_conditions: set[str] = set()\n    conditions = hass.data[CONDITIONS]",
    (
        "    new_conditions: set[str] = set()\n"
        "    if CONDITIONS not in hass.data:\n"
        "        hass.data[CONDITIONS] = {}\n"
        "    if CONDITION_PLATFORM_SUBSCRIPTIONS not in hass.data:\n"
        "        hass.data[CONDITION_PLATFORM_SUBSCRIPTIONS] = []\n"
        "    conditions = hass.data[CONDITIONS]"
    ),
)

result = subprocess.run(
    ["python", "-m", "homeassistant", "--config", "./", "--script", "check_config", "--info", "all"],
    check=False,
    capture_output=True,
    text=True,
)

# Print captured output so it remains visible in CI logs.
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
sys.stdout.flush()
sys.stderr.flush()

# HA's check_config exits 0 even when it finds component-level config errors
# (automations with invalid keys, etc.).  Detect them via Python logging output
# which uses the format "LEVEL:logger:message".
error_lines = [
    line for line in (result.stdout + result.stderr).splitlines()
    if line.startswith("ERROR:")
]

if error_lines:
    print(f"\n{len(error_lines)} configuration error(s) detected in HA output:", flush=True)
    for line in error_lines:
        print(f"  {line}", flush=True)
    sys.exit(1)

sys.exit(result.returncode)
