"""Data coordinator for Baby Care Tracker."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_BABY_NAME,
    CONF_FEEDING_START_LEFT,
    CONF_FEEDING_START_RIGHT,
    CONF_FEEDING_STOP,
    CONF_SLEEP_START,
    CONF_WAKE_UP,
    CONF_DIAPER_PEE,
    CONF_DIAPER_POO,
    CONF_DIAPER_BOTH,
    ACTIVITY_FEEDING,
    ACTIVITY_SLEEPING,
    ACTIVITY_DIAPER,
    FEEDING_LEFT,
    FEEDING_RIGHT,
    DIAPER_PEE,
    DIAPER_POO,
    DIAPER_BOTH,
    SERVICE_START_FEEDING,
    SERVICE_STOP_FEEDING,
    SERVICE_LOG_DIAPER,
    SERVICE_LOG_SLEEP_START,
    SERVICE_LOG_WAKE_UP,
    SERVICE_LOG_BOTTLE_FEEDING,
    SERVICE_LOG_GROWTH,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class BabyCareCoordinator(DataUpdateCoordinator):
    """Coordinate baby care data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry
        self.baby_name = entry.data.get(CONF_BABY_NAME, "Baby")
        self._store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}")
        self._data: Dict[str, Any] = {}
        self._entity_listeners: List[Any] = []
        
        # Current activity tracking
        self._current_feeding: Optional[Dict[str, Any]] = None
        self._current_sleep: Optional[Dict[str, Any]] = None

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh."""
        await self._async_load_data()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data."""
        return self._data

    async def _async_load_data(self) -> None:
        """Load data from storage."""
        stored_data = await self._store.async_load()
        if stored_data is None:
            stored_data = {
                "activities": [],
                "current_feeding": None,
                "current_sleep": None,
            }
        
        self._data = stored_data
        self._current_feeding = stored_data.get("current_feeding")
        self._current_sleep = stored_data.get("current_sleep")

    async def _async_save_data(self) -> None:
        """Save data to storage."""
        self._data["current_feeding"] = self._current_feeding
        self._data["current_sleep"] = self._current_sleep
        await self._store.async_save(self._data)
        self.async_update_listeners()

    async def async_register_services(self) -> None:
        """Register services."""
        # Start feeding service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_START_FEEDING,
            self._handle_start_feeding,
            schema=vol.Schema({
                vol.Required("side"): vol.In([FEEDING_LEFT, FEEDING_RIGHT]),
                vol.Optional("notes"): cv.string,
            }),
        )

        # Stop feeding service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_STOP_FEEDING,
            self._handle_stop_feeding,
            schema=vol.Schema({
                vol.Optional("notes"): cv.string,
            }),
        )

        # Log diaper service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_DIAPER,
            self._handle_log_diaper,
            schema=vol.Schema({
                vol.Required("type"): vol.In([DIAPER_PEE, DIAPER_POO, DIAPER_BOTH]),
                vol.Optional("notes"): cv.string,
            }),
        )

        # Sleep start service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_SLEEP_START,
            self._handle_log_sleep_start,
            schema=vol.Schema({
                vol.Optional("notes"): cv.string,
            }),
        )

        # Wake up service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_WAKE_UP,
            self._handle_log_wake_up,
            schema=vol.Schema({
                vol.Optional("notes"): cv.string,
            }),
        )

        # Bottle feeding service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_BOTTLE_FEEDING,
            self._handle_log_bottle_feeding,
            schema=vol.Schema({
                vol.Required("amount_ml"): vol.Coerce(int),
                vol.Optional("notes"): cv.string,
            }),
        )

        # Growth tracking service
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_GROWTH,
            self._handle_log_growth,
            schema=vol.Schema({
                vol.Optional("weight_kg"): vol.Coerce(float),
                vol.Optional("height_cm"): vol.Coerce(float),
                vol.Optional("notes"): cv.string,
            }),
        )

        # Button mapping management services
        self.hass.services.async_register(
            DOMAIN,
            "update_button_mapping",
            self._handle_update_button_mapping,
            schema=vol.Schema({
                vol.Required("entity_id"): cv.string,
                vol.Optional("trigger_action"): cv.string,
                vol.Required("baby_care_action"): cv.string,
            }),
        )

        self.hass.services.async_register(
            DOMAIN,
            "remove_button_mapping",
            self._handle_remove_button_mapping,
            schema=vol.Schema({
                vol.Required("entity_id"): cv.string,
                vol.Optional("specific_action"): cv.string,
            }),
        )

    async def async_unregister_services(self) -> None:
        """Unregister services."""
        services = [
            SERVICE_START_FEEDING,
            SERVICE_STOP_FEEDING,
            SERVICE_LOG_DIAPER,
            SERVICE_LOG_SLEEP_START,
            SERVICE_LOG_WAKE_UP,
            SERVICE_LOG_BOTTLE_FEEDING,
            SERVICE_LOG_GROWTH,
            "update_button_mapping",
            "remove_button_mapping",
        ]
        
        for service in services:
            if self.hass.services.has_service(DOMAIN, service):
                self.hass.services.async_remove(DOMAIN, service)

    async def async_setup_entity_listeners(self) -> None:
        """Set up entity state change listeners and event listeners for button mapping."""
        options = self.entry.options
        
        # Parse entity configurations that may include specific button actions
        parsed_configs = {}
        button_event_configs = {}
        
        config_mappings = {
            CONF_FEEDING_START_LEFT: ("start_feeding", {"side": FEEDING_LEFT}),
            CONF_FEEDING_START_RIGHT: ("start_feeding", {"side": FEEDING_RIGHT}),
            CONF_FEEDING_STOP: ("stop_feeding", {}),
            CONF_SLEEP_START: ("sleep_start", {}),
            CONF_WAKE_UP: ("wake_up", {}),
            CONF_DIAPER_PEE: ("log_diaper", {"type": DIAPER_PEE}),
            CONF_DIAPER_POO: ("log_diaper", {"type": DIAPER_POO}),
            CONF_DIAPER_BOTH: ("log_diaper", {"type": DIAPER_BOTH}),
        }
        
        for config_key, (action, params) in config_mappings.items():
            entity_config = options.get(config_key)
            if not entity_config:
                continue
                
            # Check if entity has specific button action (format: entity_id:action)
            if ":" in str(entity_config):
                entity_id, button_action = entity_config.split(":", 1)
                button_event_configs[entity_id] = (action, params, button_action)
                _LOGGER.debug(f"Configured button event: {entity_id} action {button_action} -> {action}")
            else:
                # Regular state change listener
                parsed_configs[entity_config] = (action, params)
                _LOGGER.debug(f"Configured state change: {entity_config} -> {action}")

        # Set up state change listeners for regular entities
        if parsed_configs:
            listener = async_track_state_change_event(
                self.hass,
                list(parsed_configs.keys()),
                self._async_entity_state_changed,
            )
            self._entity_listeners.append(listener)
            self._entity_mappings = parsed_configs
            
        # Set up event listeners for button actions
        if button_event_configs:
            # Listen to all events that might be from our buttons
            listener = self.hass.bus.async_listen(
                "zha_event",  # Zigbee events
                self._async_button_event_received
            )
            self._entity_listeners.append(listener)
            
            # Also listen to deconz events for deCONZ users  
            listener = self.hass.bus.async_listen(
                "deconz_event",
                self._async_button_event_received
            )
            self._entity_listeners.append(listener)
            
            # Store button event mappings
            self._button_event_mappings = button_event_configs

    async def async_remove_entity_listeners(self) -> None:
        """Remove entity state change listeners."""
        for listener in self._entity_listeners:
            listener()
        self._entity_listeners.clear()

    @callback
    def _async_entity_state_changed(self, event: Event) -> None:
        """Handle entity state changes for button mapping."""
        entity_id = event.data.get("entity_id")
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if not entity_id or not new_state:
            return

        # Check if this entity is mapped to an action
        if entity_id not in getattr(self, '_entity_mappings', {}):
            return

        action, params = self._entity_mappings[entity_id]

        # Determine if we should trigger based on state change
        should_trigger = False

        # For buttons and input_buttons, trigger on any state change to 'on' or recent timestamp
        if new_state.domain in ["button", "input_button"]:
            should_trigger = True
        # For switches and binary_sensors, trigger on transition to 'on'
        elif new_state.domain in ["switch", "binary_sensor"]:
            if old_state and old_state.state != "on" and new_state.state == "on":
                should_trigger = True
        # For other entities, trigger on any state change
        else:
            if old_state and old_state.state != new_state.state:
                should_trigger = True

        if should_trigger:
            _LOGGER.info(f"Entity {entity_id} triggered action: {action} with params: {params}")
            # Schedule the action to run
            self.hass.async_create_task(self._async_trigger_action(action, params))

    async def _async_trigger_action(self, action: str, params: Dict[str, Any]) -> None:
        """Trigger a baby care action from entity state change."""
        try:
            if action == "start_feeding":
                await self._handle_start_feeding_internal(params.get("side"), "Button triggered")
            elif action == "stop_feeding":
                await self._handle_stop_feeding_internal("Button triggered")
            elif action == "log_diaper":
                await self._handle_log_diaper_internal(params.get("type"), "Button triggered")
            elif action == "sleep_start":
                await self._handle_log_sleep_start_internal("Button triggered")
            elif action == "wake_up":
                await self._handle_log_wake_up_internal("Button triggered")
        except Exception as e:
            _LOGGER.error(f"Error triggering action {action}: {e}")

    @callback
    def _async_button_event_received(self, event: Event) -> None:
        """Handle button events for specific button actions."""
        if not hasattr(self, '_button_event_mappings'):
            return
            
        event_data = event.data
        device_id = event_data.get("device_id")
        command = event_data.get("command")
        
        if not device_id or not command:
            return
            
        # Find entity_id from device_id
        entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
        device_registry = self.hass.helpers.device_registry.async_get(self.hass)
        
        # Get entities for this device
        entities = self.hass.helpers.entity_registry.async_entries_for_device(
            entity_registry, device_id
        )
        
        for entity_entry in entities:
            entity_id = entity_entry.entity_id
            if entity_id in self._button_event_mappings:
                action, params, button_action = self._button_event_mappings[entity_id]
                
                # Check if this is the specific button action we're looking for
                if command == button_action:
                    _LOGGER.info(f"Button event {entity_id} action {command} triggered: {action} with params: {params}")
                    # Schedule the action to run
                    self.hass.async_create_task(self._async_trigger_action(action, params))
                    break

    # Service handlers
    async def _handle_start_feeding(self, call: ServiceCall) -> None:
        """Handle start feeding service call."""
        side = call.data["side"]
        notes = call.data.get("notes", "")
        await self._handle_start_feeding_internal(side, notes)

    async def _handle_start_feeding_internal(self, side: str, notes: str = "") -> None:
        """Internal handler for starting feeding."""
        # Stop any current feeding
        if self._current_feeding:
            await self._handle_stop_feeding_internal("Switching sides")

        now = datetime.now()
        self._current_feeding = {
            "type": ACTIVITY_FEEDING,
            "side": side,
            "start_time": now.isoformat(),
            "notes": notes,
        }
        
        await self._async_save_data()
        _LOGGER.info(f"Started feeding on {side} side")

    async def _handle_stop_feeding(self, call: ServiceCall) -> None:
        """Handle stop feeding service call."""
        notes = call.data.get("notes", "")
        await self._handle_stop_feeding_internal(notes)

    async def _handle_stop_feeding_internal(self, notes: str = "") -> None:
        """Internal handler for stopping feeding."""
        if not self._current_feeding:
            _LOGGER.warning("No active feeding session to stop")
            return

        now = datetime.now()
        start_time = datetime.fromisoformat(self._current_feeding["start_time"])
        duration = (now - start_time).total_seconds()

        activity = {
            "type": ACTIVITY_FEEDING,
            "side": self._current_feeding["side"],
            "start_time": self._current_feeding["start_time"],
            "end_time": now.isoformat(),
            "duration_seconds": duration,
            "notes": f"{self._current_feeding.get('notes', '')} {notes}".strip(),
            "timestamp": now.isoformat(),
        }

        if "activities" not in self._data:
            self._data["activities"] = []
        
        self._data["activities"].append(activity)
        self._current_feeding = None
        
        await self._async_save_data()
        _LOGGER.info(f"Stopped feeding session, duration: {duration/60:.1f} minutes")

    async def _handle_log_diaper(self, call: ServiceCall) -> None:
        """Handle log diaper service call."""
        diaper_type = call.data["type"]
        notes = call.data.get("notes", "")
        await self._handle_log_diaper_internal(diaper_type, notes)

    async def _handle_log_diaper_internal(self, diaper_type: str, notes: str = "") -> None:
        """Internal handler for logging diaper change."""
        now = datetime.now()
        activity = {
            "type": ACTIVITY_DIAPER,
            "diaper_type": diaper_type,
            "timestamp": now.isoformat(),
            "notes": notes,
        }

        if "activities" not in self._data:
            self._data["activities"] = []
        
        self._data["activities"].append(activity)
        await self._async_save_data()
        _LOGGER.info(f"Logged diaper change: {diaper_type}")

    async def _handle_log_sleep_start(self, call: ServiceCall) -> None:
        """Handle log sleep start service call."""
        notes = call.data.get("notes", "")
        await self._handle_log_sleep_start_internal(notes)

    async def _handle_log_sleep_start_internal(self, notes: str = "") -> None:
        """Internal handler for logging sleep start."""
        # End any current sleep session
        if self._current_sleep:
            await self._handle_log_wake_up_internal("New sleep session started")

        now = datetime.now()
        self._current_sleep = {
            "type": ACTIVITY_SLEEPING,
            "start_time": now.isoformat(),
            "notes": notes,
        }
        
        await self._async_save_data()
        _LOGGER.info("Started sleep session")

    async def _handle_log_wake_up(self, call: ServiceCall) -> None:
        """Handle log wake up service call."""
        notes = call.data.get("notes", "")
        await self._handle_log_wake_up_internal(notes)

    async def _handle_log_wake_up_internal(self, notes: str = "") -> None:
        """Internal handler for logging wake up."""
        if not self._current_sleep:
            _LOGGER.warning("No active sleep session to end")
            return

        now = datetime.now()
        start_time = datetime.fromisoformat(self._current_sleep["start_time"])
        duration = (now - start_time).total_seconds()

        activity = {
            "type": ACTIVITY_SLEEPING,
            "start_time": self._current_sleep["start_time"],
            "end_time": now.isoformat(),
            "duration_seconds": duration,
            "notes": f"{self._current_sleep.get('notes', '')} {notes}".strip(),
            "timestamp": now.isoformat(),
        }

        if "activities" not in self._data:
            self._data["activities"] = []
        
        self._data["activities"].append(activity)
        self._current_sleep = None
        
        await self._async_save_data()
        _LOGGER.info(f"Ended sleep session, duration: {duration/3600:.1f} hours")

    async def _handle_log_bottle_feeding(self, call: ServiceCall) -> None:
        """Handle log bottle feeding service call."""
        amount_ml = call.data["amount_ml"]
        notes = call.data.get("notes", "")
        
        now = datetime.now()
        activity = {
            "type": "bottle_feeding",
            "amount_ml": amount_ml,
            "timestamp": now.isoformat(),
            "notes": notes,
        }

        if "activities" not in self._data:
            self._data["activities"] = []
        
        self._data["activities"].append(activity)
        await self._async_save_data()
        _LOGGER.info(f"Logged bottle feeding: {amount_ml}ml")

    async def _handle_log_growth(self, call: ServiceCall) -> None:
        """Handle log growth service call."""
        weight_kg = call.data.get("weight_kg")
        height_cm = call.data.get("height_cm")
        notes = call.data.get("notes", "")
        
        now = datetime.now()
        activity = {
            "type": "growth",
            "timestamp": now.isoformat(),
            "notes": notes,
        }
        
        if weight_kg is not None:
            activity["weight_kg"] = weight_kg
        if height_cm is not None:
            activity["height_cm"] = height_cm

        if "activities" not in self._data:
            self._data["activities"] = []
        
        self._data["activities"].append(activity)
        await self._async_save_data()
        _LOGGER.info(f"Logged growth measurement")

    async def _handle_update_button_mapping(self, call: ServiceCall) -> None:
        """Handle update button mapping service call."""
        entity_id = call.data["entity_id"]
        trigger_action = call.data.get("trigger_action")
        baby_care_action = call.data["baby_care_action"]
        
        # Map baby care action to config key
        action_to_config = {
            "feeding_start_left": CONF_FEEDING_START_LEFT,
            "feeding_start_right": CONF_FEEDING_START_RIGHT,
            "feeding_stop": CONF_FEEDING_STOP,
            "sleep_start": CONF_SLEEP_START,
            "wake_up": CONF_WAKE_UP,
            "diaper_pee": CONF_DIAPER_PEE,
            "diaper_poo": CONF_DIAPER_POO,
            "diaper_both": CONF_DIAPER_BOTH,
        }
        
        config_key = action_to_config.get(baby_care_action)
        if not config_key:
            _LOGGER.error(f"Invalid baby care action: {baby_care_action}")
            return
            
        # Update the config entry options
        new_options = dict(self.entry.options)
        
        # Remove any existing mapping for this config key
        new_options.pop(config_key, None)
        
        # Add new mapping
        if trigger_action:
            new_options[config_key] = f"{entity_id}:{trigger_action}"
        else:
            new_options[config_key] = entity_id
            
        # Update the config entry
        self.hass.config_entries.async_update_entry(
            self.entry, options=new_options
        )
        
        # Restart entity listeners
        await self.async_remove_entity_listeners()
        await self.async_setup_entity_listeners()
        
        _LOGGER.info(f"Updated button mapping: {entity_id} -> {baby_care_action}")

    async def _handle_remove_button_mapping(self, call: ServiceCall) -> None:
        """Handle remove button mapping service call."""
        entity_id = call.data["entity_id"]
        specific_action = call.data.get("specific_action")
        
        # Find and remove the mapping
        new_options = dict(self.entry.options)
        
        # Look for the entity in all config keys
        for config_key in [CONF_FEEDING_START_LEFT, CONF_FEEDING_START_RIGHT, CONF_FEEDING_STOP,
                          CONF_SLEEP_START, CONF_WAKE_UP, CONF_DIAPER_PEE, CONF_DIAPER_POO, CONF_DIAPER_BOTH]:
            entity_config = new_options.get(config_key)
            if entity_config:
                # Check if this matches our entity (with or without specific action)
                if ":" in str(entity_config):
                    config_entity, config_action = entity_config.split(":", 1)
                    if config_entity == entity_id and (not specific_action or config_action == specific_action):
                        new_options.pop(config_key, None)
                        break
                elif entity_config == entity_id and not specific_action:
                    new_options.pop(config_key, None)
                    break
        
        # Update the config entry
        self.hass.config_entries.async_update_entry(
            self.entry, options=new_options
        )
        
        # Restart entity listeners
        await self.async_remove_entity_listeners()
        await self.async_setup_entity_listeners()
        
        _LOGGER.info(f"Removed button mapping: {entity_id}")

    # Helper methods for sensors
    def get_daily_activities(self, activity_type: str) -> List[Dict[str, Any]]:
        """Get activities for today by type."""
        today = datetime.now().date()
        activities = self._data.get("activities", [])
        
        return [
            activity for activity in activities
            if activity.get("type") == activity_type
            and datetime.fromisoformat(activity["timestamp"]).date() == today
        ]

    def get_last_activity(self, activity_type: str) -> Optional[Dict[str, Any]]:
        """Get the most recent activity of a specific type."""
        activities = self._data.get("activities", [])
        
        type_activities = [
            activity for activity in activities
            if activity.get("type") == activity_type
        ]
        
        if not type_activities:
            return None
        
        return max(type_activities, key=lambda x: x["timestamp"])

    @property
    def is_currently_feeding(self) -> bool:
        """Check if currently feeding."""
        return self._current_feeding is not None

    @property
    def is_currently_sleeping(self) -> bool:
        """Check if currently sleeping."""
        return self._current_sleep is not None

    @property
    def current_feeding_info(self) -> Optional[Dict[str, Any]]:
        """Get current feeding information."""
        return self._current_feeding

    @property
    def current_sleep_info(self) -> Optional[Dict[str, Any]]:
        """Get current sleep information."""
        return self._current_sleep
