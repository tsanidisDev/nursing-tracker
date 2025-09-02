"""Constants for the Baby Care Tracker integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "baby_care_tracker"

# Configuration keys
CONF_BABY_NAME = "baby_name"
CONF_BIRTH_DATE = "birth_date"

# Entity mapping configuration keys
CONF_FEEDING_START_LEFT = "feeding_start_left_entity"
CONF_FEEDING_START_RIGHT = "feeding_start_right_entity"
CONF_FEEDING_STOP = "feeding_stop_entity"
CONF_SLEEP_START = "sleep_start_entity"
CONF_WAKE_UP = "wake_up_entity"
CONF_DIAPER_PEE = "diaper_pee_entity"
CONF_DIAPER_POO = "diaper_poo_entity"
CONF_DIAPER_BOTH = "diaper_both_entity"

# Activity types
ACTIVITY_FEEDING = "feeding"
ACTIVITY_SLEEPING = "sleeping"
ACTIVITY_DIAPER = "diaper"

# Feeding sides
FEEDING_LEFT = "left"
FEEDING_RIGHT = "right"

# Diaper types
DIAPER_PEE = "pee"
DIAPER_POO = "poo"
DIAPER_BOTH = "both"

# Services
SERVICE_START_FEEDING = "start_feeding"
SERVICE_STOP_FEEDING = "stop_feeding"
SERVICE_LOG_DIAPER = "log_diaper"
SERVICE_LOG_SLEEP_START = "log_sleep_start"
SERVICE_LOG_WAKE_UP = "log_wake_up"
SERVICE_LOG_BOTTLE_FEEDING = "log_bottle_feeding"
SERVICE_LOG_GROWTH = "log_growth"

# Data file
DATA_FILE = "baby_care_tracker_data.json"

# Default configuration
DEFAULT_NAME = "Baby"
