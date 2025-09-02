# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-01-21

### Added
- **Enhanced 2-Step Configuration Flow**: New intuitive configuration process for better UX
- **Entity-First Selection**: Select your devices first, then assign actions
- **Multi-Select Entity Picker**: Choose multiple entities at once in step 1
- **Clear Action Assignment**: Dropdown menus for each entity in step 2

### Changed
- **Replaced Single-Form Configuration**: New 2-step process replaces complex single form
- **Improved Button Mapping UX**: More logical flow for entity-to-action assignment
- **Better Configuration Organization**: See all mappings clearly in step 2

### Fixed
- **Configuration Persistence**: Settings now save and load properly
- **Entity Selection UX**: Eliminated configuration friction and confusion
- **Action Assignment Clarity**: Each entity gets clear action selection

## [1.0.3] - 2025-09-03

### Fixed
- **Entity Dropdown Restored**: Brought back entity selector dropdowns for easier configuration
- **Optional Field Handling**: Properly handle None values when entity fields are left blank
- **Configuration UX**: Improved user experience with familiar dropdown selectors

### Improved
- **Entity Selection**: Users can now select entities from dropdown menus instead of manual typing
- **Validation**: Enhanced validation to handle optional entity mapping fields correctly
- **Documentation**: Updated guides to reflect entity dropdown configuration

### Technical
- Replaced TextSelector with properly configured EntitySelector
- Updated coordinator to handle None values from empty EntitySelector fields
- Enhanced translation strings for better user guidance

## [1.0.2] - 2025-09-03

### Fixed
- **Entity Configuration Issue**: Fixed "Entity is neither a valid entity ID nor a valid UUID" error
- **Button Mapping Configuration**: Replaced EntitySelector with TextSelector for better flexibility
- **Optional Entity Fields**: Users can now leave entity mapping fields blank without validation errors
- **Empty String Handling**: Improved filtering of empty entity mappings in coordinator
- **Translation File**: Fixed empty translation file that caused config flow loading errors

### Improved
- **Configuration UI**: Enhanced entity mapping form with clearer instructions
- **Error Messages**: Better validation and error handling for entity configuration
- **Documentation**: Updated usage guide with entity ID examples and troubleshooting
- **User Experience**: More intuitive setup process for button mapping

### Technical
- Updated config flow to use TextSelector instead of EntitySelector
- Enhanced entity state listener setup with proper empty value filtering
- Improved translation strings with detailed instructions
- Added comprehensive release automation and HACS update process

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
