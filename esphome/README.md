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
