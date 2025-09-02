"""Sensor platform for Baby Care Tracker."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_BABY_NAME, ACTIVITY_FEEDING, ACTIVITY_SLEEPING, ACTIVITY_DIAPER
from .coordinator import BabyCareCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Baby Care Tracker sensors."""
    coordinator: BabyCareCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    baby_name = config_entry.data.get(CONF_BABY_NAME, "Baby")

    entities = [
        BabyCurrentActivitySensor(coordinator, baby_name),
        BabyLastFeedingTimeSensor(coordinator, baby_name),
        BabyLastSleepDurationSensor(coordinator, baby_name),
        BabyDailyFeedingsSensor(coordinator, baby_name),
        BabyDailyDiapersSensor(coordinator, baby_name),
        BabySleepStatusSensor(coordinator, baby_name),
        BabyCurrentFeedingDurationSensor(coordinator, baby_name),
        BabyCurrentSleepDurationSensor(coordinator, baby_name),
        BabyLastDiaperTimeSensor(coordinator, baby_name),
        BabyFeedingSideSensor(coordinator, baby_name),
    ]

    async_add_entities(entities)


class BabyCareSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for baby care sensors."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str, sensor_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._baby_name = baby_name
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{baby_name}_{sensor_type}".lower().replace(" ", "_")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, baby_name)},
            "name": f"Baby Care - {baby_name}",
            "manufacturer": "Baby Care Tracker",
            "model": "Baby Monitor",
        }


class BabyCurrentActivitySensor(BabyCareSensorBase):
    """Sensor for current baby activity."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "current_activity")
        self._attr_name = f"{baby_name} Current Activity"
        self._attr_icon = "mdi:baby"

    @property
    def native_value(self) -> str:
        """Return the current activity."""
        if self.coordinator.is_currently_feeding:
            feeding_info = self.coordinator.current_feeding_info
            side = feeding_info.get("side", "")
            return f"Feeding ({side})"
        elif self.coordinator.is_currently_sleeping:
            return "Sleeping"
        else:
            return "Awake"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        if self.coordinator.is_currently_feeding:
            feeding_info = self.coordinator.current_feeding_info
            start_time = datetime.fromisoformat(feeding_info["start_time"])
            duration = (datetime.now() - start_time).total_seconds()
            attrs.update({
                "feeding_side": feeding_info.get("side"),
                "feeding_start_time": feeding_info.get("start_time"),
                "feeding_duration_minutes": round(duration / 60, 1),
            })
        
        if self.coordinator.is_currently_sleeping:
            sleep_info = self.coordinator.current_sleep_info
            start_time = datetime.fromisoformat(sleep_info["start_time"])
            duration = (datetime.now() - start_time).total_seconds()
            attrs.update({
                "sleep_start_time": sleep_info.get("start_time"),
                "sleep_duration_hours": round(duration / 3600, 1),
            })
        
        return attrs


class BabyLastFeedingTimeSensor(BabyCareSensorBase):
    """Sensor for last feeding time."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "last_feeding_time")
        self._attr_name = f"{baby_name} Last Feeding Time"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:baby-bottle"

    @property
    def native_value(self) -> Optional[datetime]:
        """Return the last feeding time."""
        last_feeding = self.coordinator.get_last_activity(ACTIVITY_FEEDING)
        if last_feeding:
            return datetime.fromisoformat(last_feeding["timestamp"])
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        last_feeding = self.coordinator.get_last_activity(ACTIVITY_FEEDING)
        if not last_feeding:
            return {}
        
        return {
            "side": last_feeding.get("side"),
            "duration_minutes": round(last_feeding.get("duration_seconds", 0) / 60, 1),
            "notes": last_feeding.get("notes", ""),
        }


class BabyLastSleepDurationSensor(BabyCareSensorBase):
    """Sensor for last sleep duration."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "last_sleep_duration")
        self._attr_name = f"{baby_name} Last Sleep Duration"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:sleep"

    @property
    def native_value(self) -> Optional[float]:
        """Return the last sleep duration in hours."""
        last_sleep = self.coordinator.get_last_activity(ACTIVITY_SLEEPING)
        if last_sleep and "duration_seconds" in last_sleep:
            return round(last_sleep["duration_seconds"] / 3600, 1)
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        last_sleep = self.coordinator.get_last_activity(ACTIVITY_SLEEPING)
        if not last_sleep:
            return {}
        
        return {
            "start_time": last_sleep.get("start_time"),
            "end_time": last_sleep.get("end_time"),
            "notes": last_sleep.get("notes", ""),
        }


class BabyDailyFeedingsSensor(BabyCareSensorBase):
    """Sensor for daily feeding count."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "daily_feedings")
        self._attr_name = f"{baby_name} Daily Feedings"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:counter"

    @property
    def native_value(self) -> int:
        """Return the number of feedings today."""
        daily_feedings = self.coordinator.get_daily_activities(ACTIVITY_FEEDING)
        return len(daily_feedings)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        daily_feedings = self.coordinator.get_daily_activities(ACTIVITY_FEEDING)
        
        # Calculate total feeding time today
        total_duration = sum(
            feeding.get("duration_seconds", 0)
            for feeding in daily_feedings
            if "duration_seconds" in feeding
        )
        
        # Count by side
        left_count = sum(1 for f in daily_feedings if f.get("side") == "left")
        right_count = sum(1 for f in daily_feedings if f.get("side") == "right")
        
        return {
            "total_duration_minutes": round(total_duration / 60, 1),
            "left_breast_count": left_count,
            "right_breast_count": right_count,
        }


class BabyDailyDiapersSensor(BabyCareSensorBase):
    """Sensor for daily diaper count."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "daily_diapers")
        self._attr_name = f"{baby_name} Daily Diapers"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:baby-carriage"

    @property
    def native_value(self) -> int:
        """Return the number of diaper changes today."""
        daily_diapers = self.coordinator.get_daily_activities(ACTIVITY_DIAPER)
        return len(daily_diapers)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        daily_diapers = self.coordinator.get_daily_activities(ACTIVITY_DIAPER)
        
        # Count by type
        pee_count = sum(1 for d in daily_diapers if d.get("diaper_type") in ["pee", "both"])
        poo_count = sum(1 for d in daily_diapers if d.get("diaper_type") in ["poo", "both"])
        
        return {
            "pee_count": pee_count,
            "poo_count": poo_count,
        }


class BabySleepStatusSensor(BabyCareSensorBase):
    """Sensor for current sleep status."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "sleep_status")
        self._attr_name = f"{baby_name} Sleep Status"
        self._attr_icon = "mdi:sleep"

    @property
    def native_value(self) -> str:
        """Return the current sleep status."""
        return "Sleeping" if self.coordinator.is_currently_sleeping else "Awake"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.is_currently_sleeping:
            sleep_info = self.coordinator.current_sleep_info
            start_time = datetime.fromisoformat(sleep_info["start_time"])
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "sleep_start_time": sleep_info.get("start_time"),
                "current_duration_hours": round(duration / 3600, 1),
            }
        return {}


class BabyCurrentFeedingDurationSensor(BabyCareSensorBase):
    """Sensor for current feeding duration."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "current_feeding_duration")
        self._attr_name = f"{baby_name} Current Feeding Duration"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:timer"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current feeding duration in minutes."""
        if not self.coordinator.is_currently_feeding:
            return None
        
        feeding_info = self.coordinator.current_feeding_info
        start_time = datetime.fromisoformat(feeding_info["start_time"])
        duration = (datetime.now() - start_time).total_seconds()
        return round(duration / 60, 1)


class BabyCurrentSleepDurationSensor(BabyCareSensorBase):
    """Sensor for current sleep duration."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "current_sleep_duration")
        self._attr_name = f"{baby_name} Current Sleep Duration"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:timer"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current sleep duration in hours."""
        if not self.coordinator.is_currently_sleeping:
            return None
        
        sleep_info = self.coordinator.current_sleep_info
        start_time = datetime.fromisoformat(sleep_info["start_time"])
        duration = (datetime.now() - start_time).total_seconds()
        return round(duration / 3600, 1)


class BabyLastDiaperTimeSensor(BabyCareSensorBase):
    """Sensor for last diaper change time."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "last_diaper_time")
        self._attr_name = f"{baby_name} Last Diaper Time"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:baby-carriage"

    @property
    def native_value(self) -> Optional[datetime]:
        """Return the last diaper change time."""
        last_diaper = self.coordinator.get_last_activity(ACTIVITY_DIAPER)
        if last_diaper:
            return datetime.fromisoformat(last_diaper["timestamp"])
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        last_diaper = self.coordinator.get_last_activity(ACTIVITY_DIAPER)
        if not last_diaper:
            return {}
        
        return {
            "diaper_type": last_diaper.get("diaper_type"),
            "notes": last_diaper.get("notes", ""),
        }


class BabyFeedingSideSensor(BabyCareSensorBase):
    """Sensor for current/last feeding side."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, baby_name, "feeding_side")
        self._attr_name = f"{baby_name} Feeding Side"
        self._attr_icon = "mdi:baby-bottle"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current or last feeding side."""
        if self.coordinator.is_currently_feeding:
            feeding_info = self.coordinator.current_feeding_info
            return feeding_info.get("side")
        
        last_feeding = self.coordinator.get_last_activity(ACTIVITY_FEEDING)
        if last_feeding:
            return last_feeding.get("side")
        
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.is_currently_feeding:
            return {"status": "Currently feeding"}
        
        last_feeding = self.coordinator.get_last_activity(ACTIVITY_FEEDING)
        if last_feeding:
            return {
                "status": "Last feeding",
                "timestamp": last_feeding.get("timestamp"),
            }
        
        return {"status": "No feeding recorded"}
