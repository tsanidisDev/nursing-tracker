# Baby Care Tracker - Home Assistant Integration

A comprehensive Home Assistant integration for tracking baby care activities with smart button support.

## Features

### 📱 Core Tracking
- **Breastfeeding**: Track duration, breast side (left/right), notes
- **Sleep/Wake**: Monitor sleep patterns and duration
- **Diaper Changes**: Log pee, poo, or both with timestamps
- **Feeding**: Track bottle feeding and solid foods
- **Growth**: Record weight and height measurements

### 🔘 Smart Button Integration
- **Entity Mapping**: Map any Home Assistant entity (buttons, switches, etc.) to baby care actions
- **Flexible Controls**: 
  - Single press, double press, long press actions
  - Start/stop timers for ongoing activities
  - Quick-log buttons for instant recording
- **State Management**: Automatic handling of ongoing activities

### 🏠 Home Assistant Integration
- **Sensors**: Current activity status, daily summaries, last activity times
- **Services**: Manual logging and automation integration
- **Dashboard**: Ready-to-use Lovelace cards
- **Automations**: Trigger notifications and other automations based on baby activities

## Installation

### HACS (Recommended)
1. Add this repository to HACS custom repositories
2. Install "Baby Care Tracker" from HACS
3. Restart Home Assistant
4. Add integration via Configuration → Integrations

### Manual Installation
1. Copy the `custom_components/baby_care_tracker` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add integration via Configuration → Integrations

## Configuration

### Initial Setup
1. Go to Configuration → Integrations
2. Click "Add Integration" and search for "Baby Care Tracker"
3. Enter baby's name and configure basic settings

### Button Mapping
1. In the integration configuration, go to "Configure"
2. Map your physical buttons/switches to baby care actions:
   - **Breastfeeding Start Left**: Entity to start left breast feeding
   - **Breastfeeding Start Right**: Entity to start right breast feeding
   - **Breastfeeding Stop**: Entity to stop current feeding session
   - **Sleep Start**: Entity to log sleep beginning
   - **Wake Up**: Entity to log wake up
   - **Diaper Pee**: Entity to log pee diaper
   - **Diaper Poo**: Entity to log poo diaper
   - **Diaper Both**: Entity to log both pee and poo

### Example Button Setup
```yaml
# Example: Using Zigbee buttons
# Map a 4-button remote:
# Button 1: Start breastfeeding left
# Button 2: Start breastfeeding right  
# Button 3: Stop breastfeeding
# Button 4: Sleep/wake toggle
```

## Entities Created

### Sensors
- `sensor.baby_current_activity` - Current ongoing activity
- `sensor.baby_last_feeding_time` - Last breastfeeding session
- `sensor.baby_last_sleep_duration` - Duration of last sleep
- `sensor.baby_daily_feedings` - Number of feedings today
- `sensor.baby_daily_diapers` - Number of diaper changes today
- `sensor.baby_sleep_status` - Currently sleeping or awake

### Binary Sensors
- `binary_sensor.baby_currently_feeding` - Active feeding session
- `binary_sensor.baby_currently_sleeping` - Currently sleeping

### Services
- `baby_care_tracker.start_feeding` - Start breastfeeding session
- `baby_care_tracker.stop_feeding` - Stop current feeding
- `baby_care_tracker.log_diaper` - Log diaper change
- `baby_care_tracker.log_sleep_start` - Log sleep start
- `baby_care_tracker.log_wake_up` - Log wake up

## Automation Examples

```yaml
# Notify when baby hasn't eaten in 3 hours
- alias: "Baby Feeding Reminder"
  trigger:
    - platform: template
      value_template: >
        {{ (now() - states.sensor.baby_last_feeding_time.last_updated).total_seconds() > 10800 }}
  action:
    - service: notify.mobile_app
      data:
        message: "Baby hasn't eaten in over 3 hours"

# Dim lights when baby starts sleeping
- alias: "Baby Sleep Mode"
  trigger:
    - platform: state
      entity_id: binary_sensor.baby_currently_sleeping
      to: 'on'
  action:
    - service: light.turn_on
      target:
        entity_id: light.nursery
      data:
        brightness: 10
```

## Dashboard Cards

The integration includes example Lovelace dashboard cards for easy baby care tracking.

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

MIT License
