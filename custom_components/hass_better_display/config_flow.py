"""Config flow for Monitor Control integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_BASE_URL, CONF_DEVICE_NAME, DEFAULT_NAME

class MonitorControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Monitor Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_BASE_URL): str,  # 例如: http://192.168.6.248:55777
                }
            ),
            errors=errors,
        ) 