#!/usr/bin/env python3
"""Monkey patch HA trigger.py as workaround for issue #167066, then run config check."""

import subprocess
import sys

TRIGGER_FILE = "/usr/src/homeassistant/homeassistant/helpers/trigger.py"

# Workaround for https://github.com/home-assistant/core/issues/167066
# Patch _register_trigger_platform to initialise hass.data dicts before accessing them.
# NOTE: SEARCH matches the exact indentation/formatting from HA core commit ee4c941.
# If upstream reformats the code this pattern may need updating.
SEARCH = "    new_triggers: set[str] = set()\n    triggers = hass.data[TRIGGERS]"
REPLACE = (
    "    new_triggers: set[str] = set()\n"
    "    if TRIGGERS not in hass.data:\n"
    "        hass.data[TRIGGERS] = {}\n"
    "    if TRIGGER_PLATFORM_SUBSCRIPTIONS not in hass.data:\n"
    "        hass.data[TRIGGER_PLATFORM_SUBSCRIPTIONS] = []\n"
    "    triggers = hass.data[TRIGGERS]"
)

try:
    with open(TRIGGER_FILE) as f:
        content = f.read()
    if SEARCH in content:
        with open(TRIGGER_FILE, "w") as f:
            f.write(content.replace(SEARCH, REPLACE))
        print(f"Patch applied to {TRIGGER_FILE}")
    else:
        print(f"Patch pattern not found in {TRIGGER_FILE} - may already be fixed upstream")
except FileNotFoundError:
    print(f"Warning: {TRIGGER_FILE} not found - skipping patch")

sys.exit(
    subprocess.run(
        ["python", "-m", "homeassistant", "--config", "./", "--script", "check_config", "--info", "all"],
        check=False,
    ).returncode
)
