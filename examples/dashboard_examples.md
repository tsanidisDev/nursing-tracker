# Baby Care Tracker Dashboard Examples

## Lovelace Dashboard Configuration

Add these cards to your Lovelace dashboard for easy baby care tracking:

### Main Baby Care Card
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
    show_name: true
    show_state: true

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
        name: Stop Feeding
        icon: mdi:stop

  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.log_sleep_start
        name: Sleep Start
        icon: mdi:sleep
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.log_wake_up
        name: Wake Up
        icon: mdi:weather-sunny

  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.log_diaper
          service_data:
            type: pee
        name: Pee
        icon: mdi:water
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.log_diaper
          service_data:
            type: poo
        name: Poo
        icon: mdi:emoticon-poop
      - type: button
        tap_action:
          action: call-service
          service: baby_care_tracker.log_diaper
          service_data:
            type: both
        name: Both
        icon: mdi:baby-carriage
```

### Daily Summary Card
```yaml
type: entities
title: Daily Summary
entities:
  - entity: sensor.baby_daily_feedings
    name: Feedings Today
    icon: mdi:baby-bottle
  - entity: sensor.baby_daily_diapers
    name: Diapers Today
    icon: mdi:baby-carriage
  - entity: sensor.baby_last_feeding_time
    name: Last Feeding
  - entity: sensor.baby_last_diaper_time
    name: Last Diaper
  - entity: sensor.baby_last_sleep_duration
    name: Last Sleep Duration
```

### Current Activity Details Card
```yaml
type: conditional
conditions:
  - entity: binary_sensor.baby_currently_feeding
    state: "on"
card:
  type: entities
  title: Current Feeding Session
  entities:
    - entity: sensor.baby_feeding_side
      name: Feeding Side
    - entity: sensor.baby_current_feeding_duration
      name: Duration
```

### Sleep Tracking Card
```yaml
type: conditional
conditions:
  - entity: binary_sensor.baby_currently_sleeping
    state: "on"
card:
  type: entities
  title: Current Sleep Session
  entities:
    - entity: sensor.baby_current_sleep_duration
      name: Sleep Duration
    - entity: sensor.baby_sleep_status
      name: Status
```

## Automation Examples

### 1. Feeding Reminder
```yaml
alias: "Baby Feeding Reminder"
description: "Remind when baby hasn't eaten in 3 hours"
trigger:
  - platform: template
    value_template: >
      {% set last_feeding = states('sensor.baby_last_feeding_time') %}
      {% if last_feeding not in ['unknown', 'unavailable'] %}
        {{ (now() - as_datetime(last_feeding)).total_seconds() > 10800 }}
      {% else %}
        false
      {% endif %}
condition: []
action:
  - service: notify.mobile_app_your_device
    data:
      title: "Baby Care Reminder"
      message: "{{ states('sensor.baby_name') }} hasn't eaten in over 3 hours"
      data:
        actions:
          - action: start_feeding_left
            title: "Start Left"
          - action: start_feeding_right
            title: "Start Right"
mode: single
```

### 2. Sleep Mode Automation
```yaml
alias: "Baby Sleep Mode"
description: "Dim lights and set sleep mode when baby starts sleeping"
trigger:
  - platform: state
    entity_id: binary_sensor.baby_currently_sleeping
    to: "on"
condition: []
action:
  - service: light.turn_on
    target:
      entity_id: light.nursery
    data:
      brightness: 10
      color_name: red
  - service: notify.mobile_app_your_device
    data:
      message: "{{ states('sensor.baby_name') }} is now sleeping"
mode: single
```

### 3. Wake Up Automation
```yaml
alias: "Baby Wake Up"
description: "Restore normal lighting when baby wakes up"
trigger:
  - platform: state
    entity_id: binary_sensor.baby_currently_sleeping
    to: "off"
condition: []
action:
  - service: light.turn_on
    target:
      entity_id: light.nursery
    data:
      brightness: 255
      color_temp: 370
  - service: notify.mobile_app_your_device
    data:
      message: >
        {{ states('sensor.baby_name') }} is awake! 
        Last sleep was {{ states('sensor.baby_last_sleep_duration') }} hours
mode: single
```

### 4. Diaper Change Reminder
```yaml
alias: "Diaper Change Reminder"
description: "Remind to check diaper if no change in 3 hours"
trigger:
  - platform: template
    value_template: >
      {% set last_diaper = states('sensor.baby_last_diaper_time') %}
      {% if last_diaper not in ['unknown', 'unavailable'] %}
        {{ (now() - as_datetime(last_diaper)).total_seconds() > 10800 }}
      {% else %}
        false
      {% endif %}
condition: []
action:
  - service: notify.mobile_app_your_device
    data:
      title: "Baby Care Reminder"
      message: "Time to check {{ states('sensor.baby_name') }}'s diaper"
      data:
        actions:
          - action: log_diaper_pee
            title: "Pee"
          - action: log_diaper_poo
            title: "Poo"
          - action: log_diaper_both
            title: "Both"
mode: single
```

### 5. Daily Summary Notification
```yaml
alias: "Baby Care Daily Summary"
description: "Send daily summary at bedtime"
trigger:
  - platform: time
    at: "20:00:00"
condition: []
action:
  - service: notify.mobile_app_your_device
    data:
      title: "{{ states('sensor.baby_name') }} Daily Summary"
      message: >
        Today's stats:
        🍼 Feedings: {{ states('sensor.baby_daily_feedings') }}
        👶 Diapers: {{ states('sensor.baby_daily_diapers') }}
        💤 Last sleep: {{ states('sensor.baby_last_sleep_duration') }} hours
mode: single
```

## Script Examples for Mobile App Actions

### Notification Action Scripts
```yaml
start_feeding_left:
  alias: "Start Feeding Left"
  sequence:
    - service: baby_care_tracker.start_feeding
      data:
        side: left

start_feeding_right:
  alias: "Start Feeding Right"
  sequence:
    - service: baby_care_tracker.start_feeding
      data:
        side: right

log_diaper_pee:
  alias: "Log Pee Diaper"
  sequence:
    - service: baby_care_tracker.log_diaper
      data:
        type: pee

log_diaper_poo:
  alias: "Log Poo Diaper"
  sequence:
    - service: baby_care_tracker.log_diaper
      data:
        type: poo

log_diaper_both:
  alias: "Log Both Diaper"
  sequence:
    - service: baby_care_tracker.log_diaper
      data:
        type: both
```
