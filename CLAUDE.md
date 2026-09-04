# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Your role

Act as a **Home Assistant expert** with deep, working knowledge of:

- **Home Assistant** — the config schema, integrations, entity/device/area model, automations and scripts (triggers, conditions, actions, `mode:`), template sensors, helpers, blueprints, the `alert:` integration, packages, and the include directives below. Know when a native feature (e.g. `alert:`, `for:`, trigger IDs, `to`/`from` filters) replaces a hand-rolled workaround, and prefer it.
- **Jinja2 templating** as HA uses it — `states()`, `state_attr()`, `is_state()`, `expand()`, `now()`, availability templates, and the difference between a template that errors and one that returns `unknown`/`unavailable`.
- **Python** — for reading and fixing the integrations under `custom_components/`, and for understanding upstream HA core behaviour when a config change trips a schema or deprecation.
- **YAML** — anchors/aliases, block vs flow style, quoting rules, and the ways HA's loader diverges from plain YAML (`!include*`, `!secret`).
- **ESPHome** — device YAML, components, substitutions, lambdas (C++), scripts, and the `!include` sharing pattern used under `esphome/common/`.

Work from what this repo actually contains rather than from generic HA advice: check the existing package/device that covers a room or feature and follow its pattern. Verify entity IDs and integration options against the live instance or current HA docs before relying on them — this config spans many HA versions and some older patterns here are deprecated upstream.

## Repository overview

This is a **Home Assistant configuration repository**, not a software project. It's a declarative YAML configuration for a real smart home, deployed via Docker Compose (see https://github.com/kylegordon/ha-stack). There is no build step — "development" means editing YAML and validating it against real Home Assistant / ESPHome binaries in Docker.

The config is an amalgamation of examples gathered from around the internet (BRUH Automation, HA community forum posts, etc.) rather than a from-scratch design, so don't be surprised by inconsistent style between older and newer packages.

## Validation commands

Always run these before considering a YAML change complete.

**YAML lint (required for any YAML change):**
```bash
yamllint -c .github/yamllint-config.yml .
```
Rules disabled: `line-length`, `comments-indentation`, `document-start`, `indentation`. Ignores `custom_components/`, `www/lovelace-auto-entities/`, `esphome/common/colours.yaml`.

**Markdown lint (required for `.md` changes):**
```bash
remark --no-stdout --color --frail --use preset-lint-recommended .
```
(or via Docker: `docker run --rm -v $(pwd):/src pipelinecomponents/remark-lint:latest remark --no-stdout --color --frail --use preset-lint-recommended .`). Respects `.remarkignore`.

**Home Assistant config check (required if you touch HA config — root files, `packages/`, `automation/`, etc.):**
```bash
cp travis_secrets.yaml secrets.yaml
touch fullchain.pem privkey.pem
docker run --rm -v $(pwd):/config homeassistant/home-assistant:stable \
  python -m homeassistant --config /config --script check_config --info all
```
`secrets.yaml` is a symlink to `travis_secrets.yaml` in the working tree already, but CI does a real copy — do the same when testing so you don't accidentally edit the template. CI runs this same check against `stable`, `beta`, `rc`, and `dev` images; swap the tag to reproduce a specific CI failure.

**ESPHome validation (required if you touch anything under `esphome/`):**
```bash
cp esphome/travis_secrets.yaml.txt esphome/common/secrets.yaml
cp esphome/travis_secrets.yaml.txt esphome/secrets.yaml
docker run --rm -v $(pwd):/config esphome/esphome:stable config /config/esphome/<device>.yaml
```
CI validates every `esphome/*.yaml` device in a matrix, against both `stable` and `beta` ESPHome images.

**Never commit** `secrets.yaml`, `esphome/secrets.yaml`, `esphome/common/secrets.yaml`, `fullchain.pem`, or `privkey.pem` — all are gitignored. `travis_secrets.yaml` / `esphome/travis_secrets.yaml.txt` are the commit-safe templates with dummy values; that's also what CI uses, hence the "travis" name (a holdover from Travis CI).

## Architecture

### Include structure (start here to understand how anything loads)

`configuration.yaml` is the entry point and wires everything together via YAML include directives. Knowing which directive a directory uses tells you the expected shape of files inside it:

- `!include_dir_named packages` — `packages/*.yaml`, each file is a named dict; this is where most real configuration lives (see below).
- `!include_dir_list automation` — `automation/*.yaml`, each file is one list item (a single automation).
- `!include_dir_merge_named scripts/` — `scripts/*.yaml`, merged into one named dict.
- `!include_dir_named input_select`, `input_boolean` — same named-dict pattern.
- `!include_dir_list scenes` — `scenes/*.yaml`.
- `!include some_file.yaml` — single-file includes for the simple entity domains (`sensors.yaml`, `lights.yaml`, `switches.yaml`, `climate.yaml`, `mqtt.yaml`, `template.yaml`, `binary_sensors.yaml`, `media_players.yaml`, `device_trackers.yaml`, `groups.yaml`, `zones/places.yaml`, `shell_commands.yaml`, `notify.yaml`, `persons.yaml`, `recorder.yaml`, `logger.yaml`).

### Packages are the real unit of organization

`packages/` (44+ files) is where most logic lives, and it's organized **by room or by feature**, not by HA domain. A single package file (e.g. `packages/kitchen.yaml`) typically bundles together everything for that room: automations, scripts, template sensors, input helpers, etc. When changing behavior for a room/feature, check for an existing package file with that name first rather than scattering changes across the domain-level files (`lights.yaml`, `sensors.yaml`, ...).

Notable packages beyond simple rooms: `adaptive_lighting.yaml`, `alarm.yaml`, `climate.yaml` + `heatpump.yaml` (Better Thermostat-based heating), `givenergy.yaml` (battery/solar), `stove.yaml` (HWAM wood stove), `valetudo.yaml` (self-hosted vacuum), `overflights.yaml`, `bin_reminder_tts.yaml`, `device_alerts.yaml`.

### ESPHome devices

`esphome/*.yaml` — one file per physical device (70+). Shared behavior lives in `esphome/common/*.yaml` and is pulled in via `!include common/<file>.yaml` from each device file — check there before duplicating logic across devices (e.g. `power_plug_common.yaml`, `tx_ultimate_easy_common.yaml`, `wemos_pir_common.yaml`, `tin-hut-doors.yaml`).

TX-Ultimate-Easy touch switches (`*_switch.yaml`) are a significant device family: they fire `esphome.tx_ultimate_easy` events (`device_name`, `action` — `click`/`double_click`, optional `button_id` for multi-gang) consumed by automations in the corresponding `packages/*.yaml` file (e.g. `study_switch.yaml` events → `packages/study_lights.yaml`). When wiring up a new switch, look at how an existing room's switch+package pair is connected before inventing a new pattern. These switches run in "API Failsafe only" mode so the physical relay still works if HA/WiFi is down.

The Somfy RTS garage/tin-hut door control (`tin_hut_door_left.yaml` / `tin_hut_door_right.yaml`) shares state-machine logic from `esphome/common/tin-hut-doors.yaml` — it models a single-relay cover as a stop/open/close cycle with time-based position tracking, not true position control.

### Motion detection: trigger on events, not on binary sensors

Where a motion source exposes discrete detections as well as a level, trigger on the detections. A `binary_sensor` that means "something is present right now" is a *level*: while it is already `on`, a further detection produces no state change, and a tracker that momentarily loses its subject produces a spurious `off`. Frigate's `binary_sensor.<camera>_<object>_occupancy` sensors flicker badly for this reason — several on/off cycles for a single visit.

- **Frigate** — trigger on MQTT topic `frigate/events` and filter on `trigger.payload_json`: `type` (`new` / `update` / `end`), `after.label`, `after.camera`. See `packages/outside_lights.yaml` and `automation/camera_snapshot_notification.yaml`. Note that `after.camera` is always a *camera*, never a Frigate zone; zone occupancy is a subset of its parent camera's, so trigger on the camera. Snapshot images come from the `frigate/<camera>/<object>/snapshot` MQTT cameras in `mqtt.yaml`.
- **"Still active?" and "how long since the last detection?"** are not questions events answer on their own. Hold the state in a `timer` helper that each detection restarts, and act on `timer.finished` — not on `to: 'off'` with a `for:`, which fires when any *one* sensor in a trigger list goes clear.
- Reading an occupancy `binary_sensor` in a **condition** is fine and often correct; it is only unreliable as a **trigger**.
- Sources with no event form — Zigbee/zigbee2mqtt occupancy, mmWave presence, ESPHome PIRs — stay on state triggers. There is nothing better available for them.
- Repeated notifications about the same subject should reuse one notification via a `tag` plus a `timeout` reuse bound, rather than stacking.
- A `timer` that outlives a restart needs `restore: true` **and** a `homeassistant` start reconciliation automation. `restore: true` resumes a timer that was still running, but a timer that *expired* during the outage fires `timer.finished` while the timer component is being set up — automations arm their triggers in a startup job that runs after every `EVENT_HOMEASSISTANT_START` listener, so nothing hears it. A `platform: homeassistant, event: start` trigger is safe from that race (it listens for `EVENT_HOMEASSISTANT_STARTED`, fired after automations are armed), but give device-backed entities a short `delay:` to reconnect before reading their state.

### Custom components

`custom_components/` holds integrations not available (or not current) in HACS/core: `hwam_stove` (wood stove, needs `pystove==0.3a1`), `adaptive_lighting`, `programmable_thermostat`, `thermal_comfort`, `bulb_energy`, `smartir`, `alexa_media`, plus `hacs` itself. This directory is excluded from yamllint and remark lint.

### CI/CD

- `.github/workflows/main.yaml` — yamllint + remarklint run first; four `home_assistant_*` jobs (stable/beta/rc/dev) run in parallel afterward, each spinning up the matching `homeassistant/home-assistant` Docker image and running `check_config`.
- `.github/workflows/esphome-parallel.yaml` — triggered only on `esphome/**` changes; discovers all `esphome/*.yaml` device files and matrix-builds each against both `esphome/esphome:stable` and `:beta`. The `final` job is what branch protection actually checks.
- `.github/workflows/esphome-dummy.yaml` — provides a passing `final` job when a PR doesn't touch `esphome/`, so branch protection isn't blocked.
- Everything also runs daily (scheduled) to catch upstream HA/ESPHome release breakage even with no code changes.

## Conventions specific to this repo

- Prefer extending an existing room/feature package over adding new top-level entity files.
- When adding a new ESPHome device of a type that already exists (another power plug, another touch switch, another PIR sensor), copy the pattern of a similar existing device file and its `common/` include rather than writing config from scratch.
- Entity-level cosmetic tweaks (icons, friendly names, `assumed_state`) live in `configuration.yaml` under `homeassistant: customize:` — check there before adding a `friendly_name` elsewhere.
