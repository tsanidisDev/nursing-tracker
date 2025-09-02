# Quick Start Guide - Baby Care Tracker

## 🚀 How to Use Baby Care Tracker

### Option 1: Local Development/Testing

Since you have the integration files ready, you can test it locally:

#### Step 1: Copy to Home Assistant
```bash
# Copy the integration to your Home Assistant custom_components directory
cp -r /home/tsanidisdev/Projects/nursing-tracker/custom_components/baby_care_tracker /path/to/homeassistant/config/custom_components/

# For example, if HA is in ~/homeassistant:
cp -r custom_components/baby_care_tracker ~/homeassistant/config/custom_components/
```

#### Step 2: Restart Home Assistant
- Restart your Home Assistant instance
- Wait for it to fully load

#### Step 3: Add the Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Baby Care Tracker"**
4. Click on it and follow the setup wizard

### Option 2: Publish to GitHub and Use HACS

#### Step 1: Publish Your Repository
```bash
# Initialize git and push to GitHub
git add .
git commit -m "Initial release of Baby Care Tracker v1.0.0"
git branch -M main
git remote add origin https://github.com/tsanidisDev/nursing-tracker.git
git push -u origin main

# Create a release tag
git tag v1.0.0
git push origin v1.0.0
```

#### Step 2: Install via HACS
1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **three dots menu** → **Custom repositories**
4. Add: `https://github.com/tsanidisDev/nursing-tracker`
5. Category: **Integration**
6. Click **Add**
7. Find **"Baby Care Tracker"** and install it
8. Restart Home Assistant
9. Add the integration via **Settings** → **Devices & Services**

## 📱 Using the Integration

### Initial Setup
1. **Enter Baby's Name**: e.g., "Emma", "Oliver"
2. **Optional Birth Date**: For age tracking
3. **Configure Button Mapping** (optional but powerful!)

### Button Mapping Examples

Map physical buttons to baby actions:

```yaml
# Example: 4-button remote control
Button 1: Start Left Breast Feeding
Button 2: Start Right Breast Feeding  
Button 3: Stop Feeding
Button 4: Sleep/Wake Toggle

# Example: Smart switches for diaper tracking
Switch 1: Log Pee Diaper
Switch 2: Log Poo Diaper
Switch 3: Log Both Types
```

### Dashboard Usage

Add this card to your Lovelace dashboard:

```yaml
type: vertical-stack
cards:
  - type: glance
    title: Baby Care Status
    entities:
      - entity: sensor.baby_current_activity
        name: Current Activity
      - entity: binary_sensor.baby_currently_feeding
        name: Feeding
      - entity: binary_sensor.baby_currently_sleeping
        name: Sleeping

  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.start_feeding
          service_data:
            side: left
        name: Start Left
        icon: mdi:baby-bottle
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.start_feeding
          service_data:
            side: right
        name: Start Right
        icon: mdi:baby-bottle
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.stop_feeding
        name: Stop
        icon: mdi:stop

  - type: entities
    title: Today's Summary
    entities:
      - sensor.baby_daily_feedings
      - sensor.baby_daily_diapers
      - sensor.baby_last_feeding_time
```

### Service Usage

Call services directly:

```yaml
# Start feeding
service: baby_care_tracker.start_feeding
data:
  side: left
  notes: "Baby was fussy"

# Log diaper change
service: baby_care_tracker.log_diaper
data:
  type: both
  notes: "Big one!"

# Log sleep start
service: baby_care_tracker.log_sleep_start
data:
  notes: "Put down at 8 PM"
```

## 🔧 Troubleshooting

### Integration Not Loading
```bash
# Check Home Assistant logs
tail -f /path/to/homeassistant/config/home-assistant.log | grep baby_care_tracker
```

### Fixed Translation Error
✅ The empty translation file has been fixed. The integration should now load properly.

### Common Issues

1. **"Integration not found"**
   - Ensure files are copied to the right directory
   - Restart Home Assistant completely

2. **"Button mapping not working"**
   - Verify entity IDs exist in Home Assistant
   - Check entity states in Developer Tools

3. **"Services not available"**
   - Integration may not be loaded properly
   - Check logs for errors

## 🎯 Real-World Usage Examples

### Scenario 1: Night Feeding
1. Keep a bedside button next to your bed
2. Map it to "Start Left Feeding" 
3. When baby wakes at 3 AM, just press the button
4. No need to fumble with phone or dashboard

### Scenario 2: Nursery Setup
1. Install 3 smart switches near changing table
2. Map them to: Pee, Poo, Both
3. After diaper change, flip the appropriate switch
4. Hands-free logging while baby is squirmy

### Scenario 3: Partner Coordination
1. Both parents see real-time status on dashboards
2. Get notifications: "Baby hasn't eaten in 3 hours"
3. Track daily patterns and share with pediatrician

## 📊 Data You'll Get

- **Real-time status**: Currently feeding/sleeping
- **Daily summaries**: Number of feedings, diapers today  
- **Duration tracking**: How long each feeding/sleep session
- **History**: Complete log of all activities with timestamps
- **Automation triggers**: Use data for smart home automations

The integration is designed to be **hands-free** and **mother-friendly** - perfect for those busy parenting moments when you can't reach for your phone! 🍼👶
