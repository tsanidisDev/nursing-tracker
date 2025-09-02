# Installation & Setup Guide

## Prerequisites

- Home Assistant 2023.1.0 or newer
- HACS (Home Assistant Community Store) installed

## Installation Methods

### Method 1: HACS (Recommended)

1. **Add Custom Repository:**
   - Open HACS in your Home Assistant
   - Go to "Integrations"
   - Click the three dots menu and select "Custom repositories"
   - Add this repository URL: `https://github.com/tsanidisDev/nursing-tracker`
   - Select category: "Integration"
   - Click "Add"

2. **Install Integration:**
   - Search for "Baby Care Tracker" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Add Integration:**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Baby Care Tracker"
   - Follow the setup wizard

### Method 2: Manual Installation

1. **Download Files:**
   ```bash
   cd /config/custom_components/
   git clone https://github.com/tsanidisDev/nursing-tracker.git
   mv nursing-tracker/custom_components/baby_care_tracker ./
   rm -rf nursing-tracker
   ```

2. **Restart Home Assistant:**
   - Go to Developer Tools → Services
   - Call service: `homeassistant.restart`

3. **Add Integration:**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Baby Care Tracker"

## Initial Setup

### Step 1: Basic Configuration

1. **Enter Baby Information:**
   - Baby's name (e.g., "Emma", "Oliver")
   - Birth date (optional, for age calculations)

### Step 2: Configure Button Mapping (Optional)

If you have physical buttons or smart switches you want to use:

1. Go to the integration settings
2. Click "Configure"
3. Map your entities to baby care actions:
   - **Start Left Feeding**: Button/switch to start left breast feeding
   - **Start Right Feeding**: Button/switch to start right breast feeding
   - **Stop Feeding**: Button/switch to stop feeding
   - **Sleep Start**: Button/switch to log sleep start
   - **Wake Up**: Button/switch to log wake up
   - **Diaper Pee**: Button/switch to log pee diaper
   - **Diaper Poo**: Button/switch to log poo diaper
   - **Diaper Both**: Button/switch to log both types

### Step 3: Add Dashboard Cards

Copy the dashboard examples from `examples/dashboard_examples.md` to create your baby care dashboard.

## Entities Created

After setup, you'll have these entities:

### Sensors
- `sensor.{baby_name}_current_activity`
- `sensor.{baby_name}_last_feeding_time`
- `sensor.{baby_name}_last_sleep_duration`
- `sensor.{baby_name}_daily_feedings`
- `sensor.{baby_name}_daily_diapers`
- `sensor.{baby_name}_sleep_status`
- `sensor.{baby_name}_current_feeding_duration`
- `sensor.{baby_name}_current_sleep_duration`
- `sensor.{baby_name}_last_diaper_time`
- `sensor.{baby_name}_feeding_side`

### Binary Sensors
- `binary_sensor.{baby_name}_currently_feeding`
- `binary_sensor.{baby_name}_currently_sleeping`

### Services
- `baby_care_tracker.start_feeding`
- `baby_care_tracker.stop_feeding`
- `baby_care_tracker.log_diaper`
- `baby_care_tracker.log_sleep_start`
- `baby_care_tracker.log_wake_up`
- `baby_care_tracker.log_bottle_feeding`
- `baby_care_tracker.log_growth`

## Quick Start Usage

### Using Dashboard Cards
1. Create dashboard cards using the examples
2. Tap buttons to log activities

### Using Services
Call services directly:
```yaml
service: baby_care_tracker.start_feeding
data:
  side: left
  notes: "Fussy today"
```

### Using Physical Buttons
1. Map your buttons in the integration configuration
2. Press mapped buttons to trigger actions automatically

## Data Storage

Data is stored in Home Assistant's storage directory:
- File: `.storage/baby_care_tracker_{entry_id}`
- Format: JSON
- Backup: Included in Home Assistant backups

## Troubleshooting

### Integration Not Found
- Ensure you've restarted Home Assistant after installation
- Check that files are in the correct directory: `/config/custom_components/baby_care_tracker/`

### Button Mapping Not Working
- Verify the entity IDs are correct
- Check that entities exist and are available
- Look in Home Assistant logs for error messages

### Data Not Saving
- Check Home Assistant logs for permission errors
- Ensure storage directory is writable

### Entities Not Updating
- Check if the coordinator is running (look for debug logs)
- Verify the integration is properly loaded

## Advanced Configuration

### Custom Automations
See `examples/dashboard_examples.md` for automation examples.

### Multiple Babies
Install the integration multiple times with different baby names.

### Data Export
Data can be accessed via Home Assistant's REST API or by reading the storage JSON file.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Feature Requests**: Submit enhancement requests on GitHub
- **Community**: Home Assistant Community Forum

## Updating

### HACS Updates
HACS will notify you of updates automatically.

### Manual Updates
```bash
cd /config/custom_components/baby_care_tracker/
git pull origin main
```
Then restart Home Assistant.

## Uninstalling

1. Remove the integration from Settings → Devices & Services
2. Delete the custom component folder:
   ```bash
   rm -rf /config/custom_components/baby_care_tracker/
   ```
3. Restart Home Assistant
