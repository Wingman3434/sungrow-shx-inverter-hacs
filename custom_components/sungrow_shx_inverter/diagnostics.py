"""Redacted device diagnostics and replayable register snapshots."""

from typing import Any

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusError

from .coordinator import SungrowConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
) -> dict[str, Any]:
    """Never include host, serial, unique ID or raw identity words."""
    error: str | None
    coordinator = entry.runtime_data
    try:
        raw, unreadable = await coordinator.device.async_read_raw()
    except ModbusError as err:
        # Error strings can contain endpoints, so serialize only the error type.
        raw = {}
        unreadable = {}
        error = type(err).__name__
    else:
        error = None
    for address in range(4989, 4999):
        raw.get("input", {}).pop(address, None)
    return {
        "model": coordinator.device.model,
        "components": sorted(coordinator.device.components),
        "absent": sorted(coordinator.device.absent),
        "updated": sorted(coordinator.data.updated),
        "failed": {
            key: type(err).__name__ for key, err in coordinator.data.failed.items()
        },
        "unreadable": unreadable,
        "raw": raw,
        "read_error": error,
    }
