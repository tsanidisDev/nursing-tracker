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
            
            # Preserve existing mappings for selected entities
            for entity in self.current_entities:
                # Find if this entity is already mapped
                for action_key, entity_id in current_options.items():
                    if entity_id == entity:
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

        # Get currently configured entities
        current_options = self.config_entry.options
        currently_mapped = [entity_id for entity_id in current_options.values() if entity_id]

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
            # Build the final configuration mapping
            final_config = {}
            
            for entity in self.current_entities:
                action = user_input.get(f"action_{entity}")
                if action and action != "none":
                    # Map action back to config key
                    action_to_config = {
                        "feeding_start_left": "feeding_start_left_entity",
                        "feeding_start_right": "feeding_start_right_entity",
                        "feeding_stop": "feeding_stop_entity",
                        "sleep_start": "sleep_start_entity", 
                        "wake_up": "wake_up_entity",
                        "diaper_pee": "diaper_pee_entity",
                        "diaper_poo": "diaper_poo_entity",
                        "diaper_both": "diaper_both_entity",
                    }
                    config_key = action_to_config.get(action)
                    if config_key:
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
                # Convert config key back to action key
                config_to_action = {
                    "feeding_start_left_entity": "feeding_start_left",
                    "feeding_start_right_entity": "feeding_start_right",
                    "feeding_stop_entity": "feeding_stop",
                    "sleep_start_entity": "sleep_start",
                    "wake_up_entity": "wake_up", 
                    "diaper_pee_entity": "diaper_pee",
                    "diaper_poo_entity": "diaper_poo",
                    "diaper_both_entity": "diaper_both",
                }
                current_action = config_to_action.get(current_action, "none")
            else:
                current_action = "none"

            # Create action choices
            action_choices = [{"value": "none", "label": "No Action"}]
            for action_key, action_label in BABY_ACTIONS.items():
                action_choices.append({"value": action_key, "label": action_label})

            schema_dict[vol.Optional(f"action_{entity}", default=current_action)] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=action_choices,
                        mode=selector.SelectSelectorMode.DROPDOWN,
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
                    "Select 'No Action' to leave an entity unmapped."
                )
            },
        )
