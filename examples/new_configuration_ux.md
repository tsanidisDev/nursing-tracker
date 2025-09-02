# New Configuration UX - 2-Step Process

## Overview

The Baby Care Tracker now features an **enhanced 2-step configuration process** for better user experience when setting up button mapping.

## Step-by-Step Guide

### Step 1: Select Your Entities
1. Go to **Integration Settings** → **Configure**
2. You'll see a **multi-select entity picker**
3. **Select all entities** you want to use from the dropdown:
   - Buttons (`button.*`)
   - Switches (`switch.*`) 
   - Input Buttons (`input_button.*`)
   - Binary Sensors (`binary_sensor.*`)
4. Click **Submit**

### Step 2: Assign Actions
1. For each selected entity, you'll see a **dropdown menu**
2. **Choose what action** each entity should trigger:
   - Start Left Breast Feeding
   - Start Right Breast Feeding
   - Stop Feeding
   - Start Sleep
   - Wake Up
   - Log Pee Diaper
   - Log Poo Diaper
   - Log Both (Pee & Poo)
   - No Action (leave unmapped)
3. Click **Submit** to save your configuration

## Example Workflow

### Step 1 Selection
```
Selected Entities:
☑️ button.nursery_button_1
☑️ button.nursery_button_2  
☑️ switch.diaper_switch_1
☑️ switch.diaper_switch_2
☑️ input_button.sleep_button
```

### Step 2 Assignment
```
Entity Action Assignments:
button.nursery_button_1 → Start Left Breast Feeding
button.nursery_button_2 → Start Right Breast Feeding
switch.diaper_switch_1 → Log Pee Diaper
switch.diaper_switch_2 → Log Poo Diaper
input_button.sleep_button → Start Sleep
```

## Benefits of New UX

### ✅ **Entity-First Approach**
- See all your available devices first
- Choose what you want to use before assigning actions
- Multi-select for faster selection

### ✅ **Clear Action Assignment** 
- One dropdown per entity
- No confusion about which field is for what
- Easy to see all your mappings

### ✅ **Flexible Configuration**
- One entity = one action (or none)
- Can leave entities unmapped by selecting "No Action"
- Easy to reconfigure later

### ✅ **Better Organization**
- Step 1: "What devices do I have?"
- Step 2: "What should each device do?"
- Logical progression from selection to assignment

## Common Configurations

### **Minimal Setup (2 buttons)**
```
Step 1: Select
☑️ button.feeding_button_1
☑️ button.feeding_button_2

Step 2: Assign
button.feeding_button_1 → Start Left Breast Feeding
button.feeding_button_2 → Stop Feeding
```

### **Full Bedside Setup (8 controls)**
```
Step 1: Select
☑️ button.bedside_left_feeding
☑️ button.bedside_right_feeding  
☑️ button.bedside_stop_feeding
☑️ button.bedside_start_sleep
☑️ button.bedside_wake_up
☑️ switch.bedside_pee_diaper
☑️ switch.bedside_poo_diaper
☑️ switch.bedside_both_diaper

Step 2: Assign
button.bedside_left_feeding → Start Left Breast Feeding
button.bedside_right_feeding → Start Right Breast Feeding
button.bedside_stop_feeding → Stop Feeding
button.bedside_start_sleep → Start Sleep
button.bedside_wake_up → Wake Up
switch.bedside_pee_diaper → Log Pee Diaper
switch.bedside_poo_diaper → Log Poo Diaper
switch.bedside_both_diaper → Log Both (Pee & Poo)
```

## Tips for Success

1. **Use descriptive entity names** in Home Assistant for easier selection
2. **Start with essential actions** (feeding, sleep) then add diaper tracking
3. **Group related entities** by room or function in your entity naming
4. **Test each button** after configuration to verify correct actions
5. **Reconfigure anytime** by going back to Integration → Configure

## Previous vs New UX

### Before (Single Complex Form)
- ❌ Long form with many fields
- ❌ Hard to see what entities are available  
- ❌ Confusing which field maps to what
- ❌ Configuration sometimes didn't save

### After (2-Step Process)
- ✅ Clear entity selection first
- ✅ Simple action assignment second
- ✅ Better visual organization
- ✅ Reliable configuration saving
