"""Monitor control device class."""
import logging
import aiohttp
from datetime import timedelta
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class MonitorDevice:
    """Representation of a Monitor device."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        base_url: str,
    ) -> None:
        """Initialize the device."""
        self.hass = hass
        self.name = name
        self._base_url = base_url.rstrip('/')  # 移除末尾的斜杠
        self._brightness = 0.5
        self._volume = 0.5
        
        # 创建更新协调器
        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="monitor_values",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=30),  # 每30秒更新一次
        )

    async def _async_update_data(self):
        """获取最新的显示器数据."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    # 获取音量
                    volume_url = f"{self._base_url}/get?feature=volume&name={self.name}"
                    async with session.get(volume_url) as resp:
                        if resp.status == 200:
                            self._volume = float(await resp.text())
                    
                    # 获取亮度
                    brightness_url = f"{self._base_url}/get?feature=brightness&name={self.name}"
                    async with session.get(brightness_url) as resp:
                        if resp.status == 200:
                            self._brightness = float(await resp.text())
                    
                    return {
                        "brightness": self._brightness,
                        "volume": self._volume
                    }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}")

    async def async_set_brightness(self, brightness: float) -> None:
        """Set monitor brightness."""
        try:
            url = f"{self._base_url}/set?feature=brightness&name={self.name}&value={brightness}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        self._brightness = brightness
                        # 强制更新数据
                        await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting brightness: %s", err)

    async def async_set_volume(self, volume: float) -> None:
        """Set monitor volume."""
        try:
            url = f"{self._base_url}/set?feature=volume&name={self.name}&value={volume}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        self._volume = volume
                        # 强制更新数据
                        await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting volume: %s", err)

    @property
    def brightness(self) -> float:
        """Return the brightness of the monitor."""
        return self._brightness

    @property
    def volume(self) -> float:
        """Return the volume of the monitor."""
        return self._volume 