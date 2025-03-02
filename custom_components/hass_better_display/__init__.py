"""The Monitor Control integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BASE_URL, CONF_DEVICE_NAME
from .device import MonitorDevice


PLATFORMS: list[str] = [
    Platform.LIGHT,
    Platform.FAN,
    Platform.SELECT,
]

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

