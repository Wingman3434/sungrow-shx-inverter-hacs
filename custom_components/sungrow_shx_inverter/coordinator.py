"""Polling cohorts with per-component availability and automatic recovery."""

from datetime import timedelta
import logging
from time import monotonic
from typing import override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError

from ._vendor.sungrow_shx_inverter import (
    SungrowSHxInverter,
    UnsupportedDeviceError,
    UpdateReport,
)
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SungrowCoordinator(DataUpdateCoordinator[UpdateReport]):
    """Schedule the source's 5/10/60/600-second cohorts on a single coordinator."""

    def __init__(
        self, hass: HomeAssistant, entry: SungrowConfigEntry, device: SungrowSHxInverter
    ) -> None:
        """Initialize the entity or coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.device = device
        self._entry = entry
        self._next: dict[str, float] = {}
        self._fresh: set[str] = set()
        self._failed: dict[str, ModbusError] = {}

    @property
    def device_info(self) -> DeviceInfo:
        """Describe the physical inverter using its serial number."""
        serial = self.device.serial_number
        assert serial is not None
        return DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="Sungrow",
            model=self.device.model,
            name=f"Sungrow SHx Inverter {self.device.model}",
            serial_number=serial,
            sw_version=self.device.inverter_firmware.inverter_firmware_version or None,
        )

    @override
    async def _async_update_data(self) -> UpdateReport:
        """Async update data."""
        try:
            await self.device.async_identify()
            if self.device.serial_number != self._entry.unique_id:
                raise ConfigEntryError(
                    translation_domain=DOMAIN, translation_key="device_changed"
                )
            now = monotonic()
            due = [n for n in self.device.components if now >= self._next.get(n, 0)]
            if not due:
                return UpdateReport(set(self._fresh), dict(self._failed))
            report = await self.device.async_update_components(due)
        except UnsupportedDeviceError as err:
            raise ConfigEntryError(
                translation_domain=DOMAIN, translation_key="unsupported_device"
            ) from err
        except ModbusError as err:
            # Retry all cohorts on recovery; retained slow readings aren't fresh.
            self._next.clear()
            self._fresh.clear()
            raise UpdateFailed(
                translation_domain=DOMAIN, translation_key="modbus_error"
            ) from err
        if not report.updated and not (self._fresh - set(due)):
            raise UpdateFailed(
                translation_domain=DOMAIN, translation_key="no_component_answered"
            )
        for name in report.failed.keys() - self._failed.keys():
            _LOGGER.warning(
                "Sungrow %s is unavailable: %s",
                name,
                type(report.failed[name]).__name__,
            )
        for name in report.updated:
            if name in self._failed:
                _LOGGER.info("Sungrow %s is available again", name)
            self._failed.pop(name, None)
        self._fresh.difference_update(report.failed)
        self._fresh.update(report.updated)
        self._failed.update(report.failed)
        # A subsystem the device dropped mid-poll is neither fresh nor failing.
        served = self.device.components.keys()
        self._fresh = {name for name in self._fresh if name in served}
        self._failed = {
            name: err for name, err in self._failed.items() if name in served
        }
        finished = monotonic()
        for name in due:
            interval = self.device.intervals.get(name)
            if interval is None:
                self._next.pop(name, None)
                continue
            self._next[name] = finished + interval
        return UpdateReport(set(self._fresh), dict(self._failed))

    async def async_refresh_components(self, *names: str) -> None:
        """Read back a changed component and status immediately after a command."""
        for name in names:
            self._next.pop(name, None)
        await self.async_request_refresh()


type SungrowConfigEntry = ConfigEntry[SungrowCoordinator]
