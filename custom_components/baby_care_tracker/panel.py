"""Dashboard panel for Baby Care Tracker button mapping."""
from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.components import panel_custom
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the Baby Care Tracker panel."""
    
    # Register the panel
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path="baby-care-tracker",
        webcomponent_name="baby-care-tracker-panel",
        sidebar_title="Baby Care Tracker",
        sidebar_icon="mdi:baby-face",
        module_url="/api/baby_care_tracker/panel.js",
        embed_iframe=False,
        require_admin=False,
    )
    
    _LOGGER.info("Baby Care Tracker panel registered")

async def async_unregister_panel(hass: HomeAssistant) -> None:
    """Unregister the Baby Care Tracker panel."""
    hass.components.panel_custom.async_remove_panel("baby-care-tracker")
    _LOGGER.info("Baby Care Tracker panel unregistered")
