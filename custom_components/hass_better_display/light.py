"""Platform for Monitor Control integration."""
from __future__ import annotations

from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS,
    ColorMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import MonitorDevice

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Monitor brightness control."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    await device.coordinator.async_config_entry_first_refresh()
    async_add_entities([MonitorBrightnessLight(device)])

class MonitorBrightnessLight(CoordinatorEntity, LightEntity):
    """Representation of Monitor brightness control."""

    def __init__(self, device: MonitorDevice) -> None:
        super().__init__(device.coordinator)
        self._device = device
        self._attr_unique_id = f"{device.name}_brightness"
        self._attr_name = f"{device.name} Brightness"
        self._attr_device_info = device.device_info
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_icon = "mdi:brightness-6"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.brightness > 0

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return int(self._device.brightness * 255)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = round(kwargs[ATTR_BRIGHTNESS] / 255, 2)
            await self._device.async_set_brightness(brightness)
        else:
            await self._device.async_set_brightness(1.0)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        await self._device.async_set_brightness(0.0) 