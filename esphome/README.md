# ESPHome devices configuration directory

The local control aspect of the switches has been lifted from https://community.home-assistant.io/t/make-esphome-node-fallback-when-not-connected-to-ha-api/116615/16


## ESPHome Garage Cover Single Control

Graciously copied from @juaigl at https://github.com/juaigl/esphome-garage-cover-single-control
This mainly relates to tin-hut-door-left.yaml and tni-hut-door-right.yaml
It controls a Somfy Rolixo RTS system, which has a couple of pins that can be shorted like a push button to trigger control of the door.
# This project uses:

Esp board compatible with ESPHome
Relay to activate the cover control
Two reed switches to detect end positions of the door.

# Cover description
Cover is controlled with a single control using a relay. Each time the control is activated, it performs an action according following state machine:

Sequence: open -> stop -> close -> stop -> open
When cover reach the end (open or close) it counts as a stop action

# Features
Position reporting based on time (no position control for now)
Calculate the number of times the control need to be activated to perform the action requested
Actuate the door many times as needed to perform requested action. For example if position in memory is wrong or unknow because a external control stops the door at middle.
Detect and update position when the cover is externally commanded. Only if door is full open or closed when commanded or reachs end stop sensors.
Configuration options for GPIOs, debounce time, open/close durations. time between control actuation...

# Code
The door logic is placed in common/tin-hut-doors.yaml

## TX-Ultimate-Easy Smart Switches

This project uses TX-Ultimate-Easy smart switches for wall-mounted light control throughout the home. These are ESPHome-based touch switches with RGB LED feedback and multi-gang support.

### Configuration Files

The following TX-Ultimate-Easy switch devices are configured in this directory:

- `study_switch.yaml` - Single gang switch in the study
- `kitchen_switch.yaml` - Dual gang switch in the kitchen
- `hall_single_switch.yaml` - Single gang switch in the hallway
- `hall_dual_switch.yaml` - Dual gang switch in the hallway
- `front_hall_dual_switch.yaml` - Dual gang switch in the front hallway
- `ensuite_switch.yaml` - Single gang switch in the ensuite bathroom
- `masterbedroom_switch.yaml` - Single gang switch in the master bedroom
- `guestbedroom_switch.yaml` - Single gang switch in the guest bedroom
- `living_room_switch.yaml` - Switch in the living room
- `craftroom_switch.yaml` - Switch in the craft room

All switches use the TX-Ultimate-Easy package from https://github.com/edwardtfn/TX-Ultimate-Easy (ref: v9999.99.9)

### Features

- **Touch Control**: Responsive touch interface with visual feedback
- **RGB LED Feedback**: Rainbow effects show when button presses are registered
- **Multi-gang Support**: Single or dual gang configurations
- **Bluetooth Proxy**: All switches include Bluetooth proxy functionality
- **API Failsafe Mode**: Switches are configured to operate in "API Failsafe only" mode, allowing them to function as normal switches when WiFi or Home Assistant is offline. The physical relay is activated on every button press regardless of connectivity status.
- **Event-based**: Switches fire events that trigger automations

### Integration with Home Assistant

The switches fire `esphome.tx_ultimate_easy` events that are consumed by automations defined in the `../packages/` directory. Each automation responds to specific event data:

**Event Structure:**
```yaml
event_type: esphome.tx_ultimate_easy
event_data:
  device_name: <switch_name>  # e.g., "study_switch", "kitchen_switch"
  action: <action_type>        # e.g., "click", "double_click"
  button_id: <button_number>   # Optional, for multi-gang switches (e.g., "1", "2")
```

**Action Types:**
- `click` - Single button press
- `double_click` - Double button press (used for secondary functions)

### Automation Examples

The switches are integrated with automations in the parent directory's `packages/` folder:

- **`packages/study_lights.yaml`**: Study light toggle on click, decorative lights on double-click
- **`packages/kitchen.yaml`**: Kitchen ceiling lights (button 1) and worktop lights (button 2)
- **`packages/hallway.yaml`**: Hallway lights with motion detection integration
- **`packages/ensuite.yaml`**: Ensuite lights with time-based behavior
- **`packages/master_bedroom_lights.yaml`**: Master bedroom lighting control
- **`packages/guest_bedroom.yaml`**: Guest bedroom lighting control
- **`packages/living_room_lights.yaml`**: Living room lighting with multiple zones
- **`packages/craft_room.yaml`**: Craft room lighting control
- **`packages/master_bathroom.yaml`**: Master bathroom lighting

**Typical Automation Pattern:**
```yaml
automation:
  - alias: Room light toggle
    trigger:
      - platform: event
        event_type: esphome.tx_ultimate_easy
        event_data:
          device_name: room_switch
          action: click
    action:
      - service: light.turn_on
        data:
          entity_id: light.room_switch_lights_all
          effect: "Rainbow - Fast"
      - service: switch.turn_on
        entity_id: switch.room_switch_relay_1
      - service: light.toggle
        entity_id: light.room_lights
      - delay: "00:00:05"
      - service: light.turn_off
        entity_id: light.room_switch_lights_all
```

### Visual Feedback

When a button is pressed, the switch:
1. Shows a "Rainbow - Fast" LED effect
2. Activates the relay (ensuring the physical switch operates even if HA goes offline)
3. Performs the associated action (toggle lights, etc.)
4. Fades the LED effect after 5 seconds

This provides immediate visual confirmation that the button press was registered and processed.

### API Failsafe Mode

The switches are configured to operate in **API Failsafe only** mode. This means:

- **Offline Operation**: If WiFi or Home Assistant becomes unavailable, the switches continue to function as normal physical switches
- **Relay Activation**: When connected to Home Assistant, the automation activates the physical relay during button press events (step 2 above), ensuring the connected lights can be controlled by Home Assistant if they have been locally turned off during an outage.
- **Service Resume**: When Home Assistant service resumes, the relay state is synchronized, keeping the switch and light states consistent
- **No Dependency**: Physical switch operation does not depend on API connectivity

This setup ensures reliable local control of lighting while integrating seamlessly with Home Assistant for enhanced automation and feedback.

## Reed Switch Door Sensors

This project includes configurations for magnetic reed switch sensors used for door/window monitoring. These sensors provide binary states (open/closed) to Home Assistant for use in automations and monitoring.

### Hardware

- **Wemos D1 Mini** (ESP8266)
- **Magnetic reed switch** (Normally Closed type - NC)
- Connects reed switch between GPIO pin and GND
- Uses internal pull-up resistor

### Important: Normally Closed (NC) Reed Switches

**CRITICAL NOTE:** This configuration is designed for **Normally Closed (NC)** reed switches, meaning:
- The switch **conducts** (closed circuit) when the magnet is **away**
- The switch **opens** (open circuit) when the magnet is **present**

**Important:** Alarm/security reed switches are typically **Normally Open (NO)**, which is the opposite behavior. NO switches keep the alarm circuit conductive when doors are shut and allow detection of cut wires. NC switches like this one are NOT suitable for alarm applications but work fine for non-critical door monitoring.

The configuration accounts for NC behavior by using `inverted: true` so that Home Assistant reports logical door states correctly:
- **Door Open** (magnet away, switch closed/conducting) → Sensor reports "OPEN"
- **Door Closed** (magnet near, switch open) → Sensor reports "CLOSED"

### Pin Recommendations

**Recommended Pin: D2 (GPIO4)**
- Supports internal pull-up resistor
- Safe during ESP8266 boot sequence
- Not used by other critical functions

**Alternative Pins:** D1 (GPIO5), D5 (GPIO14), D6 (GPIO12), D7 (GPIO13)

**Avoid:** D3 (GPIO0), D4 (GPIO2), D8 (GPIO15) - these can cause boot issues if pulled incorrectly

### Wiring

Simple 2-wire connection:
1. Connect one wire from reed switch to the GPIO pin (e.g., D2)
2. Connect other wire from reed switch to GND
3. Internal pull-up resistor enabled in software (no external resistor needed)

### Configuration Files

- **`common/wemos_reed_switch_common.yaml`** - Common package for all reed switch sensors
  - Provides base ESP8266 configuration
  - Binary sensor with debouncing
  - Status LED indicators for WiFi/API connectivity
  - Includes common monitoring sensors (WiFi signal, uptime, etc.)

- **`tin_hut_door_sensor.yaml`** - Tin Hut pedestrian door sensor configuration
  - Monitors pedestrian door state for tin hut
  - Used for lighting automations in the tin hut and outside lights
  - Pin: D2 (GPIO4)
  - Debounce: 50ms

### Creating New Reed Switch Sensors

To add a new reed switch sensor, create a new YAML file with:

```yaml
---
substitutions:
  device_name: my-door-sensor
  device_description: My Door Reed Switch Sensor
  friendly_name: My Door Sensor
  reed_switch_pin: D2
  debounce_time: 50ms

<<: !include common/wemos_reed_switch_common.yaml
```

### Home Assistant Integration

The sensor will automatically appear in Home Assistant as:
- **Binary Sensor:** `binary_sensor.<device_name>_door` with device class `door`
- **Status Sensors:** WiFi signal strength, uptime, connection status
- **Controls:** Restart button, status LED

Use in automations for:
- Triggering lights when door opens
- Security monitoring
- Notifications
- Climate control (e.g., turn off heating when door open)

### Testing

The configuration includes visual feedback via the built-in blue LED:
- **Single blink (5s interval):** Not connected to WiFi
- **Double blink (5s interval):** Not connected to Home Assistant API
- **LED off:** Connected and operational
