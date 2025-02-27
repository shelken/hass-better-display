"""The Monitor Control integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BASE_URL, CONF_DEVICE_NAME
from .device import MonitorDevice

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.FAN]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Monitor Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    device = MonitorDevice(
        hass,
        entry.data[CONF_DEVICE_NAME],
        entry.data[CONF_BASE_URL],
    )
    
    hass.data[DOMAIN][entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok 