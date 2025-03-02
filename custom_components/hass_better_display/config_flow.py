"""Config flow for Monitor Control integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_BASE_URL, CONF_DEVICE_NAME, CONF_SOURCE_LIST, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

class MonitorControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monitor Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # 验证输入源列表格式
            try:
                source_list = {}
                for item in user_input[CONF_SOURCE_LIST].split(','):
                    key, value = item.strip().split(':')
                    source_list[key.strip()] = value.strip()
                
                return self.async_create_entry(
                    title=user_input[CONF_DEVICE_NAME],
                    data={
                        CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                        CONF_BASE_URL: user_input[CONF_BASE_URL],
                        CONF_SOURCE_LIST: source_list,
                    },
                )
            except ValueError:
                errors["base"] = "invalid_source_list"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_BASE_URL): str,  # 例如: http://192.168.6.248:55777
                    vol.Optional(
                        CONF_SOURCE_LIST, 
                        default="hdmi1:15,hdmi2:16,dp:17"
                    ): str,  # 格式: "key1:value1,key2:value2"
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """创建选项流."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """处理选项流."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """初始化选项流."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """处理选项."""
        errors = {}

        if user_input is not None:
            try:
                _LOGGER.info(f"user_input: {user_input}")
                source_list = {}
                for item in user_input[CONF_SOURCE_LIST].split(','):
                    key, value = item.strip().split(':')
                    source_list[key.strip()] = value.strip()

                # 更新配置条目的数据
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data={
                        CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                        CONF_BASE_URL: user_input[CONF_BASE_URL],
                        CONF_SOURCE_LIST: source_list,
                    }
                )

                return self.async_create_entry(title="", data={})
            except ValueError:
                errors["base"] = "invalid_source_list"

        _LOGGER.info(f"self._config_entry.data: {self._config_entry.data}")
        # 使用当前配置值作为默认值
        current_source_list = self._config_entry.options.get(
            CONF_SOURCE_LIST,
            self._config_entry.data.get(CONF_SOURCE_LIST, {})
        )
        default_source_list = ",".join([f"{k}:{v}" for k, v in current_source_list.items()])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE_NAME,
                        default=self._config_entry.data.get(CONF_DEVICE_NAME, DEFAULT_NAME)
                    ): str,
                    vol.Required(
                        CONF_BASE_URL,
                        default=self._config_entry.data.get(CONF_BASE_URL, "")
                    ): str,
                    vol.Optional(
                        CONF_SOURCE_LIST,
                        default=default_source_list
                    ): str,
                }
            ),
            errors=errors,
        ) 