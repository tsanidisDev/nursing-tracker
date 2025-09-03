"""Baby Care Tracker integration for Home Assistant."""
from __future__ import annotations

import logging
import os
from typing import Any

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN
from .coordinator import BabyCareCoordinator
from .panel import async_register_panel, async_unregister_panel

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


class BabyCareTrackerView(HomeAssistantView):
    """View to serve Baby Care Tracker panel files."""

    url = "/api/baby_care_tracker/{filename}"
    name = "api:baby_care_tracker"
    requires_auth = False

    async def get(self, request, filename):
        """Serve static files for the panel."""
        integration_dir = os.path.dirname(__file__)
        file_path = os.path.join(integration_dir, "www", filename)
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            if filename.endswith(".js"):
                return web.Response(text=content, content_type="application/javascript")
            elif filename.endswith(".css"):
                return web.Response(text=content, content_type="text/css")
            else:
                return web.Response(text=content, content_type="text/plain")
        else:
            return web.Response(status=404)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Baby Care Tracker component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register the HTTP view for serving panel files
    hass.http.register_view(BabyCareTrackerView())
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Baby Care Tracker from a config entry."""
    coordinator = BabyCareCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await coordinator.async_register_services()
    
    # Setup entity state listeners for button mapping
    await coordinator.async_setup_entity_listeners()
    
    # Register the dashboard panel
    await async_register_panel(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: BabyCareCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Unregister services
    await coordinator.async_unregister_services()
    
    # Remove entity listeners
    await coordinator.async_remove_entity_listeners()
    
    # Unregister the dashboard panel
    await async_unregister_panel(hass)
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
