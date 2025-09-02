"""Config flow for Baby Care Tracker integration."""
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
    CONF_FEEDING_START_LEFT,
    CONF_FEEDING_START_RIGHT,
    CONF_FEEDING_STOP,
    CONF_SLEEP_START,
    CONF_WAKE_UP,
    CONF_DIAPER_PEE,
    CONF_DIAPER_POO,
    CONF_DIAPER_BOTH,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)


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
    """Handle options flow for Baby Care Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_entity_mapping()

    async def async_step_entity_mapping(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure entity mapping for button controls."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current options
        current_options = self.config_entry.options

        return self.async_show_form(
            step_id="entity_mapping",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_FEEDING_START_LEFT): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_FEEDING_START_RIGHT): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_FEEDING_STOP): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_SLEEP_START): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_WAKE_UP): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_DIAPER_PEE): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_DIAPER_POO): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(CONF_DIAPER_BOTH): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["switch", "button", "input_button", "binary_sensor"],
                            multiple=False,
                        )
                    ),
                }
            ),
            description_placeholders={
                "entity_mapping_help": (
                    "Map your physical buttons, switches, or other entities to baby care actions. "
                    "Select entities from the dropdown or leave blank to disable automatic triggering for that action. "
                    "When these entities change state, the corresponding baby care action will be triggered."
                )
            },
        )
