"""Monitor control device class."""
import logging
import aiohttp
from datetime import timedelta
import async_timeout

from custom_components.hass_better_display.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceInfo

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
        self._mute_state = 'off'
        self._source = "0"
        # 添加 unique_id 属性
        self.unique_id = f"{DOMAIN}_{name}"
        
        # 创建更新协调器
        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="monitor_values",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=30),  # 每30秒更新一次
        )

        # 添加设备信息
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name)},
            name=name,
            manufacturer="HASS Better Display",
            model="Display Controller",
            sw_version="1.0.0",
            # 添加以下属性来改善 HomeKit 集成
            suggested_area="Office",  # 建议的房间
            entry_type="service",     # 设备类型
            configuration_url=base_url,  # 配置 URL
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

                    # 获取静音状态
                    volume_url = f"{self._base_url}/get?feature=mute&name={self.name}"
                    async with session.get(volume_url) as resp:
                        if resp.status == 200:
                            self._mute_state = str(await resp.text()).strip()

                    # 获取亮度
                    brightness_url = f"{self._base_url}/get?feature=brightness&name={self.name}"
                    async with session.get(brightness_url) as resp:
                        if resp.status == 200:
                            self._brightness = float(await resp.text())
                    
                    # 获取输入源
                    source_url = f"{self._base_url}/get?feature=ddc&vcp=inputSelect&name={self.name}"
                    async with session.get(source_url) as resp:
                        if resp.status == 200:
                            self._source = str(await resp.text()).strip()
                        else:
                            self._source = "0"

                    return {
                        "brightness": self._brightness,
                        "volume": self._volume,
                        "source": self._source,
                        "mute_state": self._mute_state
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

    async def async_mute_volume(self, mute_value: str) -> None:
        """Set monitor volume."""
        try:
            url = f"{self._base_url}/set?feature=mute&name={self.name}&value={mute_value}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # 强制更新数据
                        self._mute_state = mute_value
                        await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting volume: %s", err)

    async def switch_source(self, source_value: str) -> None:
        """Switch input source."""
        try:
            url = f"{self._base_url}/set?vcp=inputSelect&name={self.name}&ddc={source_value}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        _LOGGER.info("Successfully switched to source: %s", source_value)
                        # 强制更新数据
                        self._source = source_value
                        await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to switch source: %s", err)

    @property
    def brightness(self) -> float:
        """Return the brightness of the monitor."""
        return self._brightness

    @property
    def volume(self) -> float:
        """Return the volume of the monitor."""
        return self._volume
    
    @property
    def source(self) -> str:
        """Return the source of the monitor."""
        return self._source
    
    @property
    def mute_state(self) -> str:
        return self._mute_state

    @property
    def device_info(self):
        """Return device info."""
        return self._attr_device_info 