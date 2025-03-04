"""Platform for Monitor Control integration."""
from __future__ import annotations

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
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
    """Set up the Monitor volume control."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    await device.coordinator.async_config_entry_first_refresh()
    async_add_entities([MonitorVolumeFan(device)])

class MonitorVolumeFan(CoordinatorEntity, FanEntity):
    """Representation of Monitor volume control."""

    def __init__(self, device: MonitorDevice) -> None:
        super().__init__(device.coordinator)
        self._device = device
        self._attr_unique_id = f"{device.name}_volume"
        self._attr_name = f"{device.name} Volume"
        self._attr_device_info = device.device_info
        self._attr_supported_features = FanEntityFeature.SET_SPEED | \
                                        FanEntityFeature.TURN_ON | \
                                        FanEntityFeature.TURN_OFF
        self._attr_icon = "mdi:volume-high"

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self._device.mute_state == 'off'

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return int(self._device.volume * 100)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        if percentage == 0:
            await self._device.async_set_volume(0)
        else:
            volume = round(percentage / 100, 2)
            await self._device.async_set_volume(volume)

    async def async_turn_on(self, p, pm, **kwargs) -> None:
        """Turn on the fan."""
        await self._device.async_mute_volume("off")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        await self._device.async_mute_volume("on")