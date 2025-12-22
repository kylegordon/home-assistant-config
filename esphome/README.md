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
- **Relay Activation**: The automation activates the physical relay during button press events (step 2 above), ensuring the connected lights can be controlled locally
- **Service Resume**: When Home Assistant service resumes, the relay state is synchronized, keeping the switch and light states consistent
- **No Dependency**: Physical switch operation does not depend on API connectivity

This failsafe approach is based on the configuration from [Home Assistant Community](https://community.home-assistant.io/t/make-esphome-node-fallback-when-not-connected-to-ha-api/116615/16), ensuring reliable operation even during network outages.
