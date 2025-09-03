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

### Button Mapping - New Dashboard Interface

The integration now features a **dedicated dashboard** for managing button mappings, similar to Home Assistant's automation builder:

#### **Accessing the Dashboard**
1. Go to **Home Assistant sidebar** → **Baby Care Tracker**
2. Or visit `/baby-care-tracker` in your Home Assistant URL

#### **Device-First Configuration (Like HA Automations)**
The new interface follows Home Assistant's familiar pattern:

**Step 1: Select Device**
- Choose from a dropdown of available devices
- See all devices with button/switch entities
- Displays device name and model

**Step 2: Configure Actions**
- For each entity on the device, see available triggers
- Select what baby care action each trigger should perform
- Add multiple mappings for the same device

#### **Available Device Triggers**
The dashboard automatically detects available triggers:

**For Buttons (like IKEA TRÅDFRI):**
- `Arrow Left Hold` → Start Left Breast Feeding
- `Arrow Right Hold` → Start Right Breast Feeding  
- `Arrow Left Click` → Stop Feeding
- `Button Press` → Any button action
- And more device-specific triggers...

**For Switches/Sensors:**
- `State Change` → On/off triggers

#### **Benefits of Dashboard Interface:**
- ✅ **Familiar UX**: Same pattern as HA automations
- ✅ **Device-Centric**: Select device first, then configure actions
- ✅ **Visual Management**: See all mappings in one place
- ✅ **Easy Removal**: Remove mappings with one click
- ✅ **Real-Time Updates**: Changes apply immediately
- ✅ **No Config Menus**: No need to dig into integration settings

#### **Example Workflow:**
```
1. Open Baby Care Tracker dashboard
2. Select "IKEA TRÅDFRI Shortcut Button"
3. Configure:
   - Arrow Left Hold → Start Left Breast Feeding
   - Arrow Right Hold → Start Right Breast Feeding
   - Top Button → Stop Feeding
4. Click "Add" for each mapping
5. See all mappings listed below
```

#### **Dashboard Features:**
- **Current Mappings List**: See all configured button mappings
- **Device Detection**: Automatically finds devices with button entities
- **Action Dropdown**: Choose from all baby care actions
- **Remove Mappings**: One-click removal of unwanted mappings
- **Live Updates**: Changes take effect immediately without restart

#### **Legacy Config Flow Still Available:**
You can still use the traditional config flow via:
**Integration Settings** → **Configure** (for advanced users)

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
