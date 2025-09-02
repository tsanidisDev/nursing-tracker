# Button Mapping Examples

This document provides examples of how to map physical buttons and smart devices to baby care actions.

## Zigbee Button Examples

### 4-Button Remote (e.g., IKEA TRADFRI Shortcut Button)
```yaml
# Entity mapping configuration:
# Button 1 (single press): Start breastfeeding left
# Button 2 (single press): Start breastfeeding right  
# Button 3 (single press): Stop breastfeeding
# Button 4 (single press): Toggle sleep/wake

# Configuration in Baby Care Tracker integration:
feeding_start_left_entity: button.tradfri_button_1
feeding_start_right_entity: button.tradfri_button_2
feeding_stop_entity: button.tradfri_button_3
sleep_start_entity: button.tradfri_button_4
wake_up_entity: button.tradfri_button_4  # Same button toggles
```

### Smart Switch for Diaper Tracking
```yaml
# Use a 3-gang smart switch for quick diaper logging
diaper_pee_entity: switch.nursery_switch_1
diaper_poo_entity: switch.nursery_switch_2
diaper_both_entity: switch.nursery_switch_3
```

## Smart Home Integration Examples

### Philips Hue Dimmer Switch
```yaml
# Map Hue dimmer buttons to baby care actions
# On button: Start feeding left
# Brightness up: Start feeding right
# Brightness down: Stop feeding
# Off button: Log sleep/wake

feeding_start_left_entity: button.hue_dimmer_on
feeding_start_right_entity: button.hue_dimmer_brightness_up
feeding_stop_entity: button.hue_dimmer_brightness_down
sleep_start_entity: button.hue_dimmer_off
```

### ESP32 Custom Button Board
```yaml
# Custom ESP32 with 6 buttons for comprehensive baby care
feeding_start_left_entity: button.esp32_button_1
feeding_start_right_entity: button.esp32_button_2
feeding_stop_entity: button.esp32_button_3
sleep_start_entity: button.esp32_button_4
wake_up_entity: button.esp32_button_5
diaper_both_entity: button.esp32_button_6
```

### Stream Deck Integration
```yaml
# Use Stream Deck buttons (via HA integration)
feeding_start_left_entity: button.streamdeck_key_1
feeding_start_right_entity: button.streamdeck_key_2
feeding_stop_entity: button.streamdeck_key_3
sleep_start_entity: button.streamdeck_key_4
wake_up_entity: button.streamdeck_key_5
diaper_pee_entity: button.streamdeck_key_6
diaper_poo_entity: button.streamdeck_key_7
diaper_both_entity: button.streamdeck_key_8
```

## Advanced Button Configurations

### Multi-Click Support with Node-RED
If you want more sophisticated button handling (double-click, long-press), you can use Node-RED:

```json
[
    {
        "id": "button_handler",
        "type": "server-state-changed",
        "name": "Button Press",
        "server": "home_assistant",
        "version": 1,
        "entityidfilter": "button.nursery_button",
        "entityidfiltertype": "exact",
        "outputinitially": false,
        "state_type": "str",
        "haltifstate": "",
        "halt_if_type": "str",
        "halt_if_compare": "is",
        "outputs": 1,
        "output_only_on_state_change": true,
        "for": 0,
        "forType": "num",
        "forUnits": "minutes",
        "ignorePrevStateNull": false,
        "ignorePrevStateUnknown": false,
        "ignorePrevStateUnavailable": false,
        "ignoreCurrentStateUnknown": false,
        "ignoreCurrentStateUnavailable": false,
        "x": 130,
        "y": 100,
        "wires": [["click_detector"]]
    },
    {
        "id": "click_detector",
        "type": "function",
        "name": "Detect Click Type",
        "func": "// Detect single, double, or long press\nconst now = Date.now();\nconst lastClick = context.get('lastClick') || 0;\nconst clickCount = context.get('clickCount') || 0;\n\nif (now - lastClick < 500) {\n    // Double click\n    context.set('clickCount', clickCount + 1);\n    if (clickCount === 1) {\n        msg.payload = { action: 'double_click' };\n        context.set('clickCount', 0);\n        return msg;\n    }\n} else {\n    // Single click (after delay to check for double)\n    context.set('clickCount', 1);\n    context.set('lastClick', now);\n    \n    setTimeout(() => {\n        if (context.get('clickCount') === 1) {\n            node.send({ payload: { action: 'single_click' } });\n            context.set('clickCount', 0);\n        }\n    }, 500);\n}\n\nreturn null;",
        "outputs": 1,
        "x": 340,
        "y": 100,
        "wires": [["action_router"]]
    }
]
```

### Binary Sensor for Toggle Actions
```yaml
# Use binary sensors for sleep/wake toggle
automation:
  - alias: "Sleep Toggle from Button"
    trigger:
      - platform: state
        entity_id: binary_sensor.bedside_button
        to: 'on'
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: binary_sensor.baby_currently_sleeping
                state: 'off'
            sequence:
              - service: baby_care_tracker.log_sleep_start
        default:
          - service: baby_care_tracker.log_wake_up
```

## Voice Control Integration

### Alexa/Google Assistant
```yaml
# Create scripts for voice commands
script:
  start_feeding_left_voice:
    alias: "Start Feeding Left"
    sequence:
      - service: baby_care_tracker.start_feeding
        data:
          side: left
      - service: tts.speak
        data:
          entity_id: media_player.nursery_speaker
          message: "Started feeding on left breast"

  stop_feeding_voice:
    alias: "Stop Feeding"
    sequence:
      - service: baby_care_tracker.stop_feeding
      - service: tts.speak
        data:
          entity_id: media_player.nursery_speaker
          message: "Feeding session stopped"
```

## Wearable Integration

### Smartwatch Button Mapping
```yaml
# Use smartwatch apps that can trigger HA buttons
# Example with Wear OS HA companion app
feeding_start_left_entity: button.watch_tile_1
feeding_start_right_entity: button.watch_tile_2
feeding_stop_entity: button.watch_tile_3
```

### Fitness Tracker Integration
```yaml
# Some fitness trackers can send webhooks
# Use webhook automation to trigger actions
automation:
  - alias: "Fitness Tracker Button"
    trigger:
      - platform: webhook
        webhook_id: baby_care_button
    action:
      - service: baby_care_tracker.start_feeding
        data:
          side: "{{ trigger.json.side }}"
```

## Mobile App Integration

### Home Assistant Companion App Shortcuts
```yaml
# Create mobile app actionable notifications
automation:
  - alias: "Quick Baby Care Actions"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'feed_left' }}"
            sequence:
              - service: baby_care_tracker.start_feeding
                data:
                  side: left
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'feed_right' }}"
            sequence:
              - service: baby_care_tracker.start_feeding
                data:
                  side: right
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'stop_feeding' }}"
            sequence:
              - service: baby_care_tracker.stop_feeding
```

## Tips for Button Mapping

1. **Consistent Placement**: Keep buttons in the same location for muscle memory
2. **Visual Indicators**: Use colored buttons or labels for different actions
3. **Backup Methods**: Always have manual dashboard options as backup
4. **Night Mode**: Consider illuminated buttons for nighttime use
5. **Battery Monitoring**: Set up alerts for low battery on wireless buttons
6. **Testing**: Test all button mappings regularly to ensure they work
7. **Family Training**: Make sure all caregivers know the button mappings
