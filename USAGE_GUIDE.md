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

### Button Mapping - Enhanced UX with Specific Actions

The integration now features a **2-step configuration process** with support for **specific button actions**:

#### **Step 1: Select Your Entities**
1. Go to **Integration Settings** → **Configure**
2. **Select entities** you want to use from the multi-select dropdown
3. Choose from: buttons, switches, input_buttons, binary_sensors

#### **Step 2: Assign Actions**
1. For each selected entity, choose what action it should trigger:
   - **Start Left Breast Feeding**
   - **Start Right Breast Feeding** 
   - **Stop Feeding**
   - **Start Sleep**
   - **Wake Up**
   - **Log Pee Diaper**
   - **Log Poo Diaper**
   - **Log Both (Pee & Poo)**
   - **No Action** (to leave unmapped)

2. **For button entities**, you can also specify **specific button actions**:
   - Enter specific action names like `arrow_left_hold`, `arrow_right_click`
   - This allows mapping individual button actions instead of any button press

#### **Button Action Examples:**
```
Entity: button.ikea_tradfri_shortcut_button
Action: Start Left Breast Feeding  
Specific Action: arrow_left_hold

Entity: button.ikea_tradfri_shortcut_button
Action: Start Right Breast Feeding
Specific Action: arrow_right_hold

Entity: button.ikea_tradfri_shortcut_button  
Action: Stop Feeding
Specific Action: arrow_left_click
```

#### **Benefits of New UX:**
- ✅ **Entity-First Approach**: Select your available devices first
- ✅ **Clear Action Assignment**: Easy dropdown for each entity
- ✅ **Flexible Mapping**: One entity, one action (or none)
- ✅ **Saved Configuration**: Settings are properly preserved
- ✅ **Better Organization**: See all your mappings at once
- ✅ **Specific Button Actions**: Map individual button actions like `arrow_left_hold`

#### **Supported Button Actions:**
For IKEA TRÅDFRI Shortcut Button (E2001/E2002):
- `arrow_left_click` - Arrow left push
- `arrow_left_hold` - Arrow left hold  
- `arrow_left_release` - Arrow left release
- `arrow_right_click` - Arrow right push
- `arrow_right_hold` - Arrow right hold
- `arrow_right_release` - Arrow right release
- `on` - Top button push
- `brightness_move_up` - Top button hold
- `brightness_stop` - Top button release
- `off` - Bottom button push  
- `brightness_move_down` - Bottom button hold

#### **Example Workflow:**
```
Step 1: Select Entities
☑️ button.ikea_tradfri_shortcut_button
☑️ switch.diaper_switch_1
☑️ switch.diaper_switch_2

Step 2: Assign Actions
button.ikea_tradfri_shortcut_button → Start Left Breast Feeding
  └── Specific Action: arrow_left_hold
button.ikea_tradfri_shortcut_button → Start Right Breast Feeding  
  └── Specific Action: arrow_right_hold
switch.diaper_switch_1 → Log Pee Diaper
switch.diaper_switch_2 → Log Poo Diaper
```

**Note**: You can map the same button entity multiple times with different specific actions!

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

2. **"Entity selector validation fixed"**
   - ✅ **FIXED**: Entity dropdowns now work properly with optional fields
   - Select entities from dropdown or leave blank
   - No more validation errors for empty fields

3. **"Button mapping not working"**
   - Verify entity IDs exist in Home Assistant
   - Check entity states in Developer Tools
   - Ensure entities are available (not unavailable/unknown)
   - Test entity state changes manually first

4. **"Services not available"**
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
