"""The select platform for hass_better_display integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SOURCE_LIST, DOMAIN
from .device import MonitorDevice

from homeassistant.helpers import entity_registry as er
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Monitor Display select."""
    _LOGGER.info(f"select 初始化")
    device = hass.data[DOMAIN][config_entry.entry_id]
    await device.coordinator.async_config_entry_first_refresh()
    select_entity = MonitorSelect(device, config_entry)

    #将 select_entity 添加到 hass.data[DOMAIN]["entities"] 中
    if hass.data[DOMAIN].get("entities") is None:
        hass.data[DOMAIN]["entities"] = {}
    hass.data[DOMAIN]["entities"][select_entity._attr_unique_id] = select_entity

    async_add_entities([select_entity])

    # 监听配置变更
    async def config_update(hass, entry):
        # 获取旧的select_entity
        old_select_entity = hass.data[DOMAIN]["entities"][select_entity._attr_unique_id]
        await old_select_entity.update_config(entry)
        
    # 注册更新监听器
    config_entry.async_on_unload(
        config_entry.add_update_listener(config_update)
    )

    

class MonitorSelect(SelectEntity):
    """Representation of a Monitor Display select."""

    def __init__(self, device: MonitorDevice, config_entry: ConfigEntry) -> None:
        """Initialize the select."""
        self._device = device
        self._source_list = config_entry.data.get(CONF_SOURCE_LIST, {})
        self._attr_unique_id = f"{device.unique_id}_input_source_select"
        self._attr_name = f"{device.name} Input Source"
        # 从配置用户配置的输入源列表中获取选项
        # 给每个key添加一个前缀 切换到 xx
        self._attr_options = [f"切换到 {key}" for key in self._source_list.keys()]
        
        self._attr_device_info = device.device_info

    @property
    def current_option(self) -> str | None:
        """返回当前选中的选项。"""
        # 可以直接从设备获取当前输入源
        source_value = self._device.source
        source_mapping = {
           value : f"切换到 {key}" for key, value in self._source_list.items()
        }
        # _LOGGER.info(f"source_value: {source_value}")
        # _LOGGER.info(f"source_mapping: {source_mapping}")
        # _LOGGER.info(f"current_option: {source_mapping.get(source_value)}")
        return source_mapping.get(source_value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # 将选项映射到对应的输入源值
        source_mapping = {
            f"切换到 {key}": value for key, value in self._source_list.items()
        }
        # _LOGGER.info(f"async_select_option: {option}")
        if option in source_mapping:
            await self._device.switch_source(source_mapping.get(option))

    async def update_config(self, config_entry: ConfigEntry) -> None:
        """Update the config."""
        self._source_list = config_entry.data.get(CONF_SOURCE_LIST, {})
        self._attr_options = [f"切换到 {key}" for key in self._source_list.keys()]
        
        self.async_write_ha_state()