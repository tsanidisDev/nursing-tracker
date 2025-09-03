"""Enhanced config flow for Baby Care Tracker with better UX."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_BABY_NAME,
    CONF_BIRTH_DATE,
    DEFAULT_NAME,
    CONF_FEEDING_START_LEFT,
    CONF_FEEDING_START_RIGHT,
    CONF_FEEDING_STOP,
    CONF_SLEEP_START,
    CONF_WAKE_UP,
    CONF_DIAPER_PEE,
    CONF_DIAPER_POO,
    CONF_DIAPER_BOTH,
)

_LOGGER = logging.getLogger(__name__)

# Action mapping for better UX
BABY_ACTIONS = {
    "feeding_start_left": "Start Left Breast Feeding",
    "feeding_start_right": "Start Right Breast Feeding", 
    "feeding_stop": "Stop Feeding",
    "sleep_start": "Start Sleep",
    "wake_up": "Wake Up",
    "diaper_pee": "Log Pee Diaper",
    "diaper_poo": "Log Poo Diaper",
    "diaper_both": "Log Both (Pee & Poo)",
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Baby Care Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_BABY_NAME])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Baby Care - {user_input[CONF_BABY_NAME]}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BABY_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_BIRTH_DATE): selector.DateSelector(),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Baby Care Tracker with enhanced UX."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.entity_mappings = {}
        self.current_entities = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_select_entities()

    async def async_step_select_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Select entities to configure."""
        if user_input is not None:
            self.current_entities = user_input.get("entities", [])
            if not self.current_entities:
                # No entities selected, save empty configuration
                return self.async_create_entry(title="", data={})
            
            # Initialize mappings with current options
            current_options = self.config_entry.options
            self.entity_mappings = {}
            self.entity_button_actions = {}
            
            # Preserve existing mappings for selected entities - map back from config keys to entities
            config_to_entity = {
                CONF_FEEDING_START_LEFT: "feeding_start_left",
                CONF_FEEDING_START_RIGHT: "feeding_start_right", 
                CONF_FEEDING_STOP: "feeding_stop",
                CONF_SLEEP_START: "sleep_start",
                CONF_WAKE_UP: "wake_up",
                CONF_DIAPER_PEE: "diaper_pee",
                CONF_DIAPER_POO: "diaper_poo",
                CONF_DIAPER_BOTH: "diaper_both",
            }
            
            for entity in self.current_entities:
                # Find if this entity is already mapped
                for config_key, action_key in config_to_entity.items():
                    entity_config = current_options.get(config_key)
                    if entity_config:
                        # Handle entity:action format
                        if ":" in str(entity_config):
                            entity_id, button_action = entity_config.split(":", 1)
                            if entity_id == entity:
                                self.entity_mappings[entity] = action_key
                                self.entity_button_actions[entity] = button_action
                                break
                        elif entity_config == entity:
                            self.entity_mappings[entity] = action_key
                            break
                else:
                    # Entity not mapped yet
                    self.entity_mappings[entity] = None
            
            return await self.async_step_assign_actions()

        # Get all available button/switch entities
        entities = []
        for domain in ["button", "switch", "input_button", "binary_sensor"]:
            domain_entities = self.hass.states.async_entity_ids(domain)
            entities.extend(domain_entities)

        if not entities:
            return self.async_show_form(
                step_id="select_entities",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "message": "No button or switch entities found. Create some buttons or switches first, then configure the integration."
                },
            )

        # Get currently configured entities from options
        current_options = self.config_entry.options
        currently_mapped = []
        current_button_actions = {}
        
        # Extract entities from current configuration, handling button actions
        for config_key in [CONF_FEEDING_START_LEFT, CONF_FEEDING_START_RIGHT, CONF_FEEDING_STOP,
                          CONF_SLEEP_START, CONF_WAKE_UP, CONF_DIAPER_PEE, CONF_DIAPER_POO, CONF_DIAPER_BOTH]:
            entity_config = current_options.get(config_key)
            if entity_config:
                # Check if this includes a button action
                if ":" in str(entity_config):
                    entity_id, button_action = entity_config.split(":", 1)
                    currently_mapped.append(entity_id)
                    current_button_actions[entity_id] = button_action
                else:
                    currently_mapped.append(entity_config)

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema({
                vol.Optional(
                    "entities",
                    default=currently_mapped
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["button", "switch", "input_button", "binary_sensor"],
                        multiple=True,
                    )
                ),
            }),
            description_placeholders={
                "help_text": (
                    "Select the buttons, switches, or other entities you want to use for baby care actions. "
                    "In the next step, you'll assign specific actions to each entity."
                )
            },
        )

    async def async_step_assign_actions(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Assign actions to selected entities."""
        if user_input is not None:
            # Build the final configuration mapping using the correct const keys
            final_config = {}
            
            for entity in self.current_entities:
                action = user_input.get(f"action_{entity}")
                button_action = user_input.get(f"button_action_{entity}", "").strip()
                
                if action and action != "none":
                    # Map action back to config key using constants
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
                    config_key = action_to_config.get(action)
                    if config_key:
                        # Store entity with optional button action
                        if button_action:
                            final_config[config_key] = f"{entity}:{button_action}"
                        else:
                            final_config[config_key] = entity

            return self.async_create_entry(title="", data=final_config)

        # Build form for action assignment
        schema_dict = {}
        
        for entity in self.current_entities:
            # Get entity name for display
            entity_state = self.hass.states.get(entity)
            entity_name = entity_state.attributes.get("friendly_name", entity) if entity_state else entity
            
            # Get current action for this entity (if any)
            current_action = self.entity_mappings.get(entity)
            if current_action:
                # current_action is already the action key
                pass
            else:
                current_action = "none"

            # Create action choices with support for specific button actions
            action_choices = [{"value": "none", "label": "No Action"}]
            for action_key, action_label in BABY_ACTIONS.items():
                action_choices.append({"value": action_key, "label": action_label})

            # Add field with entity name as label for clarity
            field_label = f"{entity_name} ({entity})"
            schema_dict[vol.Optional(f"action_{entity}", default=current_action, description=field_label)] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=action_choices,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            )
            
            # If this is a button entity, add option for specific action selection
            if entity.startswith("button."):
                # Get existing button action if any
                existing_button_action = getattr(self, 'entity_button_actions', {}).get(entity, "")
                
                # Add an optional field for specific button action
                schema_dict[vol.Optional(f"button_action_{entity}", default=existing_button_action, description=f"Specific Action for {entity_name}")] = (
                    selector.TextSelector(
                        selector.TextSelectorConfig(
                            placeholder="e.g., arrow_left_hold, arrow_right_click (optional)"
                        )
                    )
                )

        return self.async_show_form(
            step_id="assign_actions",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "help_text": (
                    "Assign baby care actions to your selected entities. "
                    "Each entity can trigger one action when its state changes. "
                    "For buttons with specific actions (like arrow_left_hold), enter the action name below the dropdown. "
                    "Select 'No Action' to leave an entity unmapped."
                )
            },
        )
