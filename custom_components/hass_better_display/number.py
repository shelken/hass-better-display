"""Platform for Monitor Control integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .device import MonitorDevice

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Monitor Control number entities."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    
    # 启动协调器
    await device.coordinator.async_config_entry_first_refresh()

    entities = [
        MonitorBrightnessNumber(device),
        MonitorVolumeNumber(device),
    ]
    
    async_add_entities(entities)

class MonitorBrightnessNumber(CoordinatorEntity, NumberEntity):
    """Representation of a monitor brightness control."""

    def __init__(self, device: MonitorDevice) -> None:
        """Initialize the number entity."""
        super().__init__(device.coordinator)
        self._device = device
        self._attr_unique_id = f"{device.name}_brightness"
        self._attr_name = f"{device.name} Brightness"
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 1.0
        self._attr_native_step = 1/16
        self._attr_device_class = "brightness"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_has_entity_name = True
        self._attr_translation_key = "brightness"
        self._attr_device_info = device.device_info
        self._attr_icon = "mdi:brightness-6"  # 亮度图标

    @property
    def native_value(self) -> float:
        """Return the current brightness."""
        return self._device.brightness

    async def async_set_native_value(self, value: float) -> None:
        """Set new brightness value."""
        await self._device.async_set_brightness(value)

class MonitorVolumeNumber(CoordinatorEntity, NumberEntity):
    """Representation of a monitor volume control."""

    def __init__(self, device: MonitorDevice) -> None:
        """Initialize the number entity."""
        super().__init__(device.coordinator)
        self._device = device
        self._attr_unique_id = f"{device.name}_volume"
        self._attr_name = f"{device.name} Volume"
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 1.0
        self._attr_native_step = 1/16
        self._attr_device_class = "volume"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_has_entity_name = True
        self._attr_translation_key = "volume"
        self._attr_device_info = device.device_info
        self._attr_icon = "mdi:volume-high"  # 音量图标

    @property
    def native_value(self) -> float:
        """Return the current volume."""
        return self._device.volume

    async def async_set_native_value(self, value: float) -> None:
        """Set new volume value."""
        await self._device.async_set_volume(value) 