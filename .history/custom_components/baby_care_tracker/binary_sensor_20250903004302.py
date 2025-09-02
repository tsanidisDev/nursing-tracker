"""Binary sensor platform for Baby Care Tracker."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_BABY_NAME
from .coordinator import BabyCareCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Baby Care Tracker binary sensors."""
    coordinator: BabyCareCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    baby_name = config_entry.data.get(CONF_BABY_NAME, "Baby")

    entities = [
        BabyCurrentlyFeedingBinarySensor(coordinator, baby_name),
        BabyCurrentlySleepingBinarySensor(coordinator, baby_name),
    ]

    async_add_entities(entities)


class BabyCareBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for baby care binary sensors."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str, sensor_type: str) -> None:
        """Initialize the binary sensor."""
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


class BabyCurrentlyFeedingBinarySensor(BabyCareBinarySensorBase):
    """Binary sensor for currently feeding status."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, baby_name, "currently_feeding")
        self._attr_name = f"{baby_name} Currently Feeding"
        self._attr_icon = "mdi:baby-bottle"

    @property
    def is_on(self) -> bool:
        """Return true if currently feeding."""
        return self.coordinator.is_currently_feeding

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.is_currently_feeding:
            return {}
        
        feeding_info = self.coordinator.current_feeding_info
        start_time = datetime.fromisoformat(feeding_info["start_time"])
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "feeding_side": feeding_info.get("side"),
            "start_time": feeding_info.get("start_time"),
            "duration_minutes": round(duration / 60, 1),
            "notes": feeding_info.get("notes", ""),
        }


class BabyCurrentlySleepingBinarySensor(BabyCareBinarySensorBase):
    """Binary sensor for currently sleeping status."""

    def __init__(self, coordinator: BabyCareCoordinator, baby_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, baby_name, "currently_sleeping")
        self._attr_name = f"{baby_name} Currently Sleeping"
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY
        self._attr_icon = "mdi:sleep"

    @property
    def is_on(self) -> bool:
        """Return true if currently sleeping."""
        return self.coordinator.is_currently_sleeping

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.is_currently_sleeping:
            return {}
        
        sleep_info = self.coordinator.current_sleep_info
        start_time = datetime.fromisoformat(sleep_info["start_time"])
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "start_time": sleep_info.get("start_time"),
            "duration_hours": round(duration / 3600, 1),
            "notes": sleep_info.get("notes", ""),
        }
