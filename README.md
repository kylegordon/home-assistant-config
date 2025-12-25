# Home Assistant Configuration

![Home-Assistant](https://github.com/kylegordon/home-assistant-config/actions/workflows/main.yaml/badge.svg)  
![ESPHome](https://github.com/kylegordon/home-assistant-config/actions/workflows/esphome-parallel.yaml/badge.svg)

A comprehensive Home Assistant configuration for a smart home, featuring extensive automation, ESPHome device integration, and climate control. This configuration is an amalgamation of various examples and sources from around the internet, customized for real-world home automation scenarios.

## Overview

This repository contains the complete configuration for a Home Assistant installation deployed via docker-compose. The setup includes:

- **40+ automation packages** covering lighting, climate, security, and notifications
- **70+ ESPHome devices** including sensors, switches, cameras, and presence detection
- **Custom integrations** for HWAM stove control, Valetudo vacuum, and GivEnergy battery system
- **Adaptive lighting** throughout the home
- **Energy monitoring** with InfluxDB integration
- **Continuous integration** testing against Home Assistant stable, beta, RC, and dev releases

## Deployment

This configuration is deployed through docker-compose using the service description available at:
- **Deployment Stack**: <https://github.com/kylegordon/ha-stack>

## Repository Structure

```text
.
├── automation/              # Individual automation files (25 automations)
├── packages/               # Grouped configuration packages (44 packages)
│   ├── adaptive_lighting.yaml
│   ├── climate.yaml
│   ├── valetudo.yaml
│   └── ...
├── esphome/               # ESPHome device configurations (70+ devices)
│   ├── sensors/           # Motion, temperature, humidity sensors
│   ├── switches/          # Light switches and power plugs
│   ├── cameras/           # ESP32 cameras
│   └── presence/          # Everything Presence Lite devices
├── custom_components/     # Custom integrations
│   ├── hacs/             # Home Assistant Community Store
│   └── hwam_stove/       # HWAM stove integration
├── scripts/              # Reusable scripts
├── blueprints/           # Automation blueprints
├── input_select/         # Input select entities
├── input_boolean/        # Input boolean entities
└── configuration.yaml    # Main configuration file
```

## Key Features

### Automation & Packages

The configuration uses a **package-based architecture** for logical grouping of related entities and automations:

- **Climate Control**: Adaptive heating with Better Thermostat, heat pump management
- **Lighting**: Room-based automation with adaptive lighting, presence detection
- **Security**: Alarm system, camera integration, device alerts
- **Energy Management**: GivEnergy battery monitoring, utility meters, InfluxDB logging
- **Presence Detection**: Person tracking, proximity zones, status management
- **Notifications**: Bin reminders, printer status, device alerts, overflight notifications
- **Media**: Automated radio stations, TV control, media player management
- **Appliances**: HWAM stove control, Valetudo vacuum automation

### ESPHome Devices

Extensive ESPHome integration with 70+ devices:

- **Sensors**: Motion (PIR), temperature, humidity, lux meters, BLE trackers
- **Switches**: Zigbee switches, power monitoring plugs, relay controls
- **Cameras**: ESP32-CAM devices for indoor monitoring
- **Presence Detection**: Everything Presence Lite sensors with mmWave radar
- **Displays**: Bandwidth monitoring displays, traffic lights, glow orbs
- **Lighting**: Room switches, outdoor floodlights, shelf lighting
- **Konnected Panels**: Wired security sensors integration

### Integrations

- **MQTT**: Zigbee2MQTT for device control
- **InfluxDB**: Time-series data storage for energy and sensor metrics
- **Adaptive Lighting**: Circadian rhythm lighting for hallways, bedrooms, and living spaces
- **SmartIR**: Universal remote control for HVAC and media devices
- **Wake on LAN**: Remote device power management
- **Alarm Control Panel**: Manual alarm system with code protection
- **HWAM Stove**: Custom integration for wood stove monitoring and control
- **Valetudo**: Self-hosted vacuum robot control
- **GivEnergy**: Battery and solar system integration

### Climate & Energy

- **Heat Pump Control**: Automated climate management
- **Better Thermostat**: Advanced thermostat automation with away/night modes
- **Utility Meters**: Tracking energy consumption at 15-minute, hourly, daily, and monthly intervals
- **Energy Monitoring**: Per-device power consumption tracking
- **Battery Management**: GivEnergy battery system monitoring

### Presence & Security

- **Person Tracking**: Kyle and Charlotte status tracking
- **Zones**: Home, work, and location-based automations
- **Device Trackers**: Multiple tracking methods for presence detection
- **Alarm System**: Manual alarm control panel
- **Guest Mode**: Special automation mode for visitors
- **Away Detection**: Extended away automations for energy savings

## Installation & Setup

### Prerequisites

- Docker and docker-compose installed
- Home Assistant compatible host system
- Network access to ESPHome devices
- (Optional) MQTT broker for Zigbee2MQTT integration

### Initial Setup

1. Clone this repository
2. Copy `travis_secrets.yaml` to `secrets.yaml` and update with your values
3. Deploy using docker-compose from <https://github.com/kylegordon/ha-stack>
4. Configure ESPHome devices to connect to Home Assistant
5. Set up integrations requiring authentication (InfluxDB, MQTT, etc.)

### Configuration Files

The main configuration file (`configuration.yaml`) uses extensive includes:

- **Packages**: `!include_dir_named packages` - Grouped configurations
- **Automations**: `!include_dir_list automation` - Individual automation files
- **Scripts**: `!include_dir_merge_named scripts/` - Reusable scripts
- **Entity Files**: Individual YAML files for sensors, lights, switches, etc.

## Continuous Integration

The repository includes comprehensive CI/CD pipelines:

### Home Assistant Validation

Tests configuration against multiple Home Assistant versions:

- **Stable**: Latest stable release
- **Beta**: Pre-release testing
- **RC**: Release candidate
- **Dev**: Development branch

### Code Quality Checks

- **YAMLlint**: YAML syntax and style validation
- **Remark lint**: Markdown file linting
- **ESPHome**: Parallel validation of all ESPHome device configs

CI runs automatically on:

- Every push
- Every pull request
- Daily at 12:00 UTC (scheduled maintenance check)

## HWAM Stove Integration

The configuration includes integration with a HWAM smart wood stove:

- **Custom Component**: Uses <https://github.com/mvn23/hwam_stove>
- **Alternative Approach**: Basic REST and template sensors documented at <https://github.com/peterczarlarsen-ha/hwam/blob/main/configure.yaml>
- **Features**: Temperature monitoring, burn rate control, status tracking

## Notable Automations

- **Adaptive Lighting**: Circadian rhythm lighting that adjusts color temperature and brightness throughout the day
- **Room-Aware Automation**: Lights and climate adjust based on presence and time of day
- **Bin Reminders**: TTS notifications for collection days
- **Night Mode**: Automatic dimming and temperature adjustments at bedtime
- **Away Mode**: Energy-saving automations when nobody is home
- **Device Alerts**: Proactive notifications for device issues
- **Overflights**: Notifications for aircraft passing overhead (enthusiast feature)

## Customization

This configuration is tailored to a specific home but can be adapted:

1. Review `configuration.yaml` for location-specific settings (latitude, longitude, timezone)
2. Update `secrets.yaml` with your credentials
3. Modify packages to match your devices and rooms
4. Adjust ESPHome configurations for your hardware
5. Remove or disable automations that don't apply to your setup

## Contributing

While this is a personal configuration, contributions are welcome:

- Bug fixes for configuration issues
- Improvements to automation logic
- Documentation updates
- ESPHome device examples

Please test changes locally before submitting PRs.

## Resources & Acknowledgments

This configuration draws inspiration from many sources:

- **BRUH Automation**: <https://github.com/bruhautomation/BRUH2-Home-Assistant-Configuration>
- **Home Assistant Community**: Countless forum posts and shared configurations
- **ESPHome Documentation**: Device configuration examples
- **Custom Integrations**: HWAM Stove, Valetudo, and HACS community

## License

This configuration is shared for educational and inspirational purposes. Use at your own risk and adapt to your specific needs.

## Support

For issues specific to this configuration, please open an issue on GitHub. For general Home Assistant support, refer to the official documentation and community forums.
