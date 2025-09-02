# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-03

### Added
- Initial release of Baby Care Tracker integration
- **Core Tracking Features:**
  - Breastfeeding tracking with left/right breast support
  - Sleep/wake time tracking with duration calculation
  - Diaper change logging (pee, poo, both)
  - Bottle feeding tracking with volume
  - Growth measurement logging (weight, height)

- **Smart Button Integration:**
  - Entity mapping for physical buttons and smart switches
  - Support for button, switch, binary_sensor, and input_button entities
  - Automatic action triggering on entity state changes
  - Configurable button-to-action mapping via UI

- **Home Assistant Integration:**
  - 10 sensor entities for tracking various metrics
  - 2 binary sensors for current activity status
  - 7 services for manual and automated logging
  - Configuration flow with options for button mapping
  - HACS compatibility

- **Sensors:**
  - Current activity status
  - Last feeding time and side
  - Last sleep duration
  - Daily feeding and diaper counts
  - Current feeding/sleep durations
  - Sleep status (awake/sleeping)
  - Last diaper change time
  - Current feeding side

- **Services:**
  - `start_feeding` - Begin breastfeeding session
  - `stop_feeding` - End current feeding session
  - `log_diaper` - Record diaper change
  - `log_sleep_start` - Record sleep beginning
  - `log_wake_up` - Record wake up
  - `log_bottle_feeding` - Record bottle feeding
  - `log_growth` - Record growth measurements

- **Documentation:**
  - Comprehensive README with feature overview
  - Installation guide with HACS and manual setup
  - Dashboard examples with Lovelace cards
  - Button mapping examples for various devices
  - Automation examples for notifications and smart home integration

- **Data Management:**
  - JSON storage in Home Assistant storage directory
  - Persistent data across restarts
  - Activity history with timestamps and notes
  - State management for ongoing activities

### Technical Details
- Built for Home Assistant 2023.1.0+
- Uses DataUpdateCoordinator for efficient updates
- Entity state change listeners for button integration
- Configurable via integration options flow
- Full translation support (English included)
- HACS manifest for community store distribution

### Example Use Cases
- Map Zigbee buttons to feeding start/stop actions
- Use smart switches for quick diaper logging
- Voice control integration via scripts
- Mobile app actionable notifications
- Automated lighting based on sleep state
- Feeding and diaper change reminders

## [Unreleased]

### Planned Features
- Multi-baby support in single integration
- Data export functionality
- Weekly/monthly statistics
- Growth charts and percentiles
- Medication tracking
- Temperature logging
- Feeding goals and reminders
- Integration with baby monitor devices
- Mobile companion app
- Cloud sync capabilities
