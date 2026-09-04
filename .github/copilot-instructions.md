# GitHub Copilot Instructions - Home Assistant Configuration

## Special Instructions for Copilot
Whenever you run a command in the terminal, pipe the output to a file, output.txt, that you can read from. Make sure to overwrite each time so that it doesn't grow too big. There is a bug in the current version of Copilot that causes it to not read the output of commands correctly. This workaround allows you to read the output from the temporary file instead.

## Your Role

Act as a **Home Assistant expert** with deep, working knowledge of:

- **Home Assistant** - the config schema, integrations, entity/device/area model, automations and scripts (triggers, conditions, actions, `mode:`), template sensors, helpers, blueprints, the `alert:` integration, and packages. Know when a native feature (e.g. `alert:`, `for:`, trigger IDs, `to`/`from` filters) replaces a hand-rolled workaround, and prefer it.
- **Jinja2 templating** as HA uses it - `states()`, `state_attr()`, `is_state()`, `expand()`, `now()`, availability templates, and the difference between a template that errors and one that returns `unknown`/`unavailable`.
- **Python** - for reading and fixing the integrations under `custom_components/`, and for understanding upstream HA core behaviour when a config change trips a schema or deprecation.
- **YAML** - anchors/aliases, block vs flow style, quoting rules, and the ways HA's loader diverges from plain YAML (`!include*`, `!secret`).
- **ESPHome** - device YAML, components, substitutions, lambdas (C++), scripts, and the `!include` sharing pattern used under `esphome/common/`.

Work from what this repo actually contains rather than from generic HA advice: check the existing package or device file that covers a room or feature and follow its pattern. Verify entity IDs and integration options against the live instance or current HA docs before relying on them - this config spans many HA versions and some older patterns here are deprecated upstream.

## Repository Overview

This is a **Home Assistant configuration repository** (27MB, 221 YAML files) for a comprehensive smart home deployment. It is **NOT a software development project** - it's a declarative configuration repository for Home Assistant deployed via Docker Compose.

**Key Facts:**
- **Primary Language:** YAML configuration files (Home Assistant & ESPHome)
- **Deployment:** Docker Compose (see https://github.com/kylegordon/ha-stack)
- **Architecture:** Package-based configuration with 44+ packages, 70+ ESPHome devices, 25+ automations
- **No Build Process:** This is a configuration repository - validation only, no compilation
- **CI/CD:** Validates against Home Assistant stable/beta/rc/dev versions and ESPHome stable/beta

## Critical: Validation Requirements

### ALWAYS Run These Validation Steps Before Completing Tasks

1. **YAMLlint** (required for all YAML changes):
   ```bash
   yamllint -c .github/yamllint-config.yml .
   ```
   - Must pass without errors
   - Configuration at `.github/yamllint-config.yml`
   - Ignores: `custom_components/`, `www/lovelace-auto-entities/`, `esphome/common/colours.yaml`
   - Disabled rules: line-length, comments-indentation, document-start, indentation

2. **Remark lint** (required for Markdown file changes):
   ```bash
   remark --no-stdout --color --frail --use preset-lint-recommended .
   ```
   - Validates all `.md` files
   - Uses `.remarkignore` to exclude certain directories

3. **Home Assistant Config Check** (if you modify HA config files):
   - Requires Docker with Home Assistant image
   - **Prerequisites (MUST be done first):**
     ```bash
     cp travis_secrets.yaml secrets.yaml
     touch fullchain.pem privkey.pem
     ```
   - **Validation command:**
     ```bash
     docker run --rm -v $(pwd):/config homeassistant/home-assistant:stable \
       python -m homeassistant --config /config --script check_config --info all
     ```
   - Tests against 4 versions: stable, beta, rc, dev (CI does this automatically)

4. **ESPHome Validation** (if you modify files in `esphome/` directory):
   - **Prerequisites (MUST be done first):**
     ```bash
     cp esphome/travis_secrets.yaml.txt esphome/common/secrets.yaml
     cp esphome/travis_secrets.yaml.txt esphome/secrets.yaml
     ```
   - **Validation per device (example):**
     ```bash
     docker run --rm -v $(pwd):/config esphome/esphome:stable config esphome/kitchen_switch.yaml
     ```
   - CI validates ALL 70+ devices in parallel using matrix strategy

## Repository Structure

### Root Configuration Files
- **`configuration.yaml`** - Main HA config with extensive includes
- **`secrets.yaml`** - **NEVER COMMIT THIS** (in .gitignore, use `travis_secrets.yaml` as template)
- **`travis_secrets.yaml`** - Template for secrets (commit-safe with dummy values)
- Individual entity files: `sensors.yaml`, `lights.yaml`, `switches.yaml`, `climate.yaml`, etc.

### Directory Layout
```
.
├── automation/              # Individual automation files (!include_dir_list)
├── packages/               # Grouped config packages (!include_dir_named)
│   ├── adaptive_lighting.yaml
│   ├── climate.yaml, heatpump.yaml
│   ├── kitchen.yaml, hallway.yaml, living_room_lights.yaml
│   ├── valetudo.yaml, givenergy.yaml, stove.yaml
│   └── [44 total package files for room-based & feature grouping]
├── esphome/                # ESPHome device configurations (70+ devices)
│   ├── common/            # Shared ESPHome packages & includes
│   │   ├── secrets.yaml   # ESPHome-specific secrets (NOT committed)
│   │   ├── common.yaml    # Base device config
│   │   └── [device type packages: power_plug_common.yaml, etc.]
│   ├── *.yaml             # Individual device configs
│   └── travis_secrets.yaml.txt  # ESPHome secrets template
├── scripts/               # Reusable scripts (!include_dir_merge_named)
├── custom_components/     # Custom integrations (HACS, hwam_stove)
├── blueprints/            # Automation blueprints
├── input_select/          # Input select entities
├── input_boolean/         # Input boolean entities
├── .github/
│   ├── workflows/         # CI/CD workflows
│   └── yamllint-config.yml  # YAMLlint configuration
└── www/                   # Frontend resources
```

### Package Architecture
The configuration uses Home Assistant's **package system** for logical grouping:
- Each package file in `packages/` contains related entities, automations, sensors, scripts
- Examples: `packages/kitchen.yaml` groups all kitchen-related config
- Loaded via `packages: !include_dir_named packages` in `configuration.yaml`

### ESPHome Devices
70+ devices including:
- **TX-Ultimate-Easy switches** (study_switch.yaml, kitchen_switch.yaml, etc.) - Touch switches with RGB feedback
- **Sensors:** Motion (PIR), temperature, humidity, lux meters, BLE trackers
- **Everything Presence Lite:** mmWave radar sensors (kitchen, living room, tin hut)
- **Konnected panels:** Wired security sensor integration
- **Cameras:** ESP32-CAM devices
- **Power monitoring:** Smart plugs with energy tracking
- **Custom doors:** Somfy RTS garage door controls (tin-hut-door-*.yaml)

## Common Pitfalls & Important Notes

### Secrets Management
- **NEVER** create or edit `secrets.yaml` or `esphome/common/secrets.yaml` directly
- **ALWAYS** use templates: `travis_secrets.yaml` and `esphome/travis_secrets.yaml.txt`
- For validation, copy templates to actual secrets files (see validation steps above)

### SSL Certificate Stubs
- **ALWAYS** create stub files before HA validation: `touch fullchain.pem privkey.pem`
- These are referenced in configuration but not used in validation

### ESPHome Common Packages
- Devices use `!include common/*.yaml` for shared configuration
- Common packages are in `esphome/common/`: `common.yaml`, `power_plug_common.yaml`, etc.
- **colours.yaml** is excluded from yamllint due to complex color definitions

### YAML Include Patterns
Understand the different include directives:
- `!include file.yaml` - Single file include
- `!include_dir_list automation` - List of automations (array)
- `!include_dir_named packages` - Named dictionary of packages
- `!include_dir_merge_named scripts/` - Merged named dictionaries

### Custom Components
- **HACS** (Home Assistant Community Store) - manages other custom components
- **hwam_stove** - HWAM smart stove integration (requires `pystove==0.3a1`)
- **adaptive_lighting** - Circadian lighting (installed via HACS)
- Located in `custom_components/` (excluded from linting)

## CI/CD Workflows

### Main Workflow (.github/workflows/main.yaml)
Runs on: push, pull_request, daily at 12:00 UTC

**Job sequence:**
1. **yamllint** - YAML syntax validation
2. **remarklint** - Markdown validation  
3. **home_assistant_stable** - HA config check (stable)
4. **home_assistant_beta** - HA config check (beta)
5. **home_assistant_rc** - HA config check (rc)
6. **home_assistant_dev** - HA config check (dev)

Jobs 3-6 run in parallel after jobs 1-2 complete.

### ESPHome Workflows

**esphome-parallel.yaml** - Runs when esphome/ files change:
1. **files** job - Discovers all `esphome/*.yaml` files
2. **loop-stable** - Matrix validation of all devices (stable)
3. **loop-beta** - Matrix validation of all devices (beta)
4. **final** - Completion marker for branch protection

**esphome-dummy.yaml** - Runs when esphome/ files DON'T change:
- Provides passing "final" job for branch protection when no ESPHome changes exist

### Branch Protection
The "final" job name in ESPHome workflows is used by GitHub branch protection rules.

## Making Changes

### For Home Assistant Config Changes
1. Edit YAML files in root, `packages/`, `automation/`, etc.
2. Run `yamllint -c .github/yamllint-config.yml .`
3. Create stub files and secrets: `cp travis_secrets.yaml secrets.yaml && touch fullchain.pem privkey.pem`
4. Validate with Docker (see validation steps above)
5. **DO NOT** commit `secrets.yaml`, `fullchain.pem`, `privkey.pem` (they're in .gitignore)

### For ESPHome Changes
1. Edit device configs in `esphome/*.yaml` or common packages in `esphome/common/`
2. Run `yamllint -c .github/yamllint-config.yml .`
3. Create ESPHome secrets: `cp esphome/travis_secrets.yaml.txt esphome/common/secrets.yaml && cp esphome/travis_secrets.yaml.txt esphome/secrets.yaml`
4. Validate specific device config with ESPHome Docker image
5. **DO NOT** commit `esphome/secrets.yaml` or `esphome/common/secrets.yaml`

### For Documentation Changes
1. Edit `.md` files
2. Run `remark --no-stdout --color --frail --use preset-lint-recommended .`
3. Check `.remarkignore` for excluded directories

## Configuration Patterns

### Entity Customization
Extensive customization in `configuration.yaml` under `homeassistant: customize:`:
- Custom icons (e.g., `sensor.next_bin: icon: mdi:delete-empty`)
- Friendly names
- `assumed_state` settings for lights
- Entity pictures (Gravatar URLs for persons)

### Utility Meters
Energy tracking with multiple cycles:
- `quarter_hourly_energy`, `hourly_energy`, `daily_energy`, `monthly_energy`
- Source: `sensor.energy_spent`
- Separate meters for TV energy consumption

### Motion Detection: Trigger on Events, Not Binary Sensors

Where a motion source exposes discrete detections as well as a level, trigger on the detections. A `binary_sensor` meaning "something is present right now" is a **level**: while it is already `on`, a further detection produces no state change, and a tracker that momentarily loses its subject produces a spurious `off`. Frigate's `binary_sensor.<camera>_<object>_occupancy` sensors flicker badly for this reason - several on/off cycles for a single visit.

- **Frigate** - trigger on MQTT topic `frigate/events` and filter on `trigger.payload_json`: `type` (`new` / `update` / `end`), `after.label`, `after.camera`. See `packages/outside_lights.yaml` and `automation/camera_snapshot_notification.yaml`. `after.camera` is always a **camera**, never a Frigate zone; zone occupancy is a subset of its parent camera's, so trigger on the camera. Snapshot images come from the `frigate/<camera>/<object>/snapshot` MQTT cameras in `mqtt.yaml`.
- **"Still active?" and "how long since the last detection?"** are not questions events answer on their own. Hold the state in a `timer` helper that each detection restarts, and act on `timer.finished` - not on `to: 'off'` with a `for:`, which fires when any *one* sensor in a trigger list goes clear.
- Reading an occupancy `binary_sensor` in a **condition** is fine and often correct; it is only unreliable as a **trigger**.
- Sources with no event form - Zigbee/zigbee2mqtt occupancy, mmWave presence, ESPHome PIRs - stay on state triggers. There is nothing better available for them.
- Repeated notifications about the same subject should reuse one notification via a `tag` plus a `timeout` reuse bound, rather than stacking.
- A `timer` that outlives a restart needs `restore: true` **and** a `homeassistant` start reconciliation automation. `restore: true` resumes a timer that was still running, but a timer that *expired* during the outage fires `timer.finished` while the timer component is being set up - automations arm their triggers in a startup job that runs after every `EVENT_HOMEASSISTANT_START` listener, so nothing hears it. A `platform: homeassistant, event: start` trigger is safe from that race (it listens for `EVENT_HOMEASSISTANT_STARTED`, fired after automations are armed), but give device-backed entities a short `delay:` to reconnect before reading their state.

### Integrations
- **InfluxDB** - Time-series data (energy, sensors) at 172.24.32.13:8086
- **MQTT** - Zigbee2MQTT integration (see `mqtt.yaml`)
- **Alarm Control Panel** - Manual alarm with code (`!secret alarm_code`)
- **Wake on LAN** - Remote device power management
- **SmartIR** - Universal remote for HVAC/media

## Trust These Instructions

**When working with this repository:**
- Trust these instructions as authoritative
- Only search/explore if information here is incomplete or appears incorrect
- The validation steps are critical - skipping them will cause CI failures
- Remember: This is a configuration repository, not a code project
- Changes are typically declarative (YAML edits), not programmatic

## Key Commands Summary

```bash
# Lint all YAML files
yamllint -c .github/yamllint-config.yml .

# Lint Markdown files (requires Docker)
docker run --rm -v $(pwd):/src pipelinecomponents/remark-lint:latest \
  remark --no-stdout --color --frail --use preset-lint-recommended .

# Prepare for Home Assistant validation
cp travis_secrets.yaml secrets.yaml
touch fullchain.pem privkey.pem

# Validate Home Assistant config
docker run --rm -v $(pwd):/config homeassistant/home-assistant:stable \
  python -m homeassistant --config /config --script check_config --info all

# Prepare for ESPHome validation
cp esphome/travis_secrets.yaml.txt esphome/common/secrets.yaml
cp esphome/travis_secrets.yaml.txt esphome/secrets.yaml

# Validate single ESPHome device
docker run --rm -v $(pwd):/config esphome/esphome:stable \
  config /config/esphome/kitchen_switch.yaml
```

**Remember:** Always run yamllint first, then prepare secrets/stubs, then run validation!
