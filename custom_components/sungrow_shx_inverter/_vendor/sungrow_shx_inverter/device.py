"""Typed residential hybrid inverter over an injected Modbus unit."""

import logging
from asyncio import Lock, sleep
from collections.abc import Iterable

from modbus_connection import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
    ModbusUnit,
)

from .active_limitation import ActiveLimitation
from .apl import Apl
from .backup import Backup
from .battery import Battery
from .battery_firmware import BatteryFirmware
from .battery_health import BatteryHealth
from .battery_info import BatteryInfo
from .battery_limits import BatteryLimits
from .battery_settings import BatterySettings
from .battery_status import BatteryStatus
from .combined_energy import CombinedEnergy
from .communication_firmware import CommunicationFirmware
from .derived import DerivedReadings
from .energy import Energy
from .enums import InverterCommand
from .export_bounds import ExportBounds
from .export_settings import ExportSettings
from .grid import Grid
from .grid_flow import GridFlow
from .grid_output import GridOutput
from .identity import Identity
from .inverter_firmware import InverterFirmware
from .inverter_temperature import InverterTemperature
from .legacy_firmware import LegacyFirmware
from .load_settings import LoadSettings
from .meter_power import MeterPower
from .model import SungrowComponent, UpdateReport, bounded
from .pv import Pv
from .software import Software
from .state import State
from .variants import Model, UnsupportedDeviceError, identify

_LOGGER = logging.getLogger(__name__)


class SungrowSHxInverter:
    """Own device state and protocol rules, never the connection lifecycle."""

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        message_wait: float = 0.1,
        battery_max_power: float | None = None,
    ) -> None:
        self._unit = unit
        self._lock = Lock()
        self.profile: Model | None = None
        self.absent: set[str] = set()
        self._battery_max_power = (
            None if battery_max_power is None else bounded(10, 65535)(battery_max_power)
        )
        # Capability-detect requirements added after the 4.10/4.11 releases.
        # Released shared units only allow per-unit message spacing.
        if callable(require_timeout := getattr(unit, "require_timeout", None)):
            require_timeout(30)
        if callable(require_delay := getattr(unit, "require_connect_delay", None)):
            require_delay(15)
        unit.set_message_spacing(message_wait)
        self.legacy_firmware = LegacyFirmware(unit)
        self.software = Software(unit)
        self.identity = Identity(unit)
        self.combined_energy = CombinedEnergy(unit)
        self.inverter_temperature = InverterTemperature(unit)
        self.pv = Pv(unit)
        self.grid = Grid(unit)
        self.battery = Battery(unit)
        self.meter_power = MeterPower(unit)
        self.export_bounds = ExportBounds(unit)
        self.battery_info = BatteryInfo(unit)
        self.backup = Backup(unit)
        self.state = State(unit)
        self.energy = Energy(unit)
        self.grid_flow = GridFlow(unit)
        self.battery_status = BatteryStatus(unit)
        self.battery_health = BatteryHealth(unit)
        self.grid_output = GridOutput(unit)
        self.load_settings = LoadSettings(unit)
        self.battery_settings = BatterySettings(unit)
        self.export_settings = ExportSettings(unit)
        self.active_limitation = ActiveLimitation(unit)
        self.inverter_firmware = InverterFirmware(unit)
        self.communication_firmware = CommunicationFirmware(unit)
        self.battery_firmware = BatteryFirmware(unit)
        self.apl = Apl(unit)
        self.battery_limits = BatteryLimits(unit)
        self.derived = DerivedReadings(self)
        self.components: dict[str, SungrowComponent] = {
            "legacy_firmware": self.legacy_firmware,
            "software": self.software,
            "identity": self.identity,
            "combined_energy": self.combined_energy,
            "inverter_temperature": self.inverter_temperature,
            "pv": self.pv,
            "grid": self.grid,
            "battery": self.battery,
            "meter_power": self.meter_power,
            "export_bounds": self.export_bounds,
            "battery_info": self.battery_info,
            "backup": self.backup,
            "state": self.state,
            "energy": self.energy,
            "grid_flow": self.grid_flow,
            "battery_status": self.battery_status,
            "battery_health": self.battery_health,
            "grid_output": self.grid_output,
            "load_settings": self.load_settings,
            "battery_settings": self.battery_settings,
            "export_settings": self.export_settings,
            "active_limitation": self.active_limitation,
            "inverter_firmware": self.inverter_firmware,
            "communication_firmware": self.communication_firmware,
            "battery_firmware": self.battery_firmware,
            "apl": self.apl,
            "battery_limits": self.battery_limits,
        }
        self.intervals: dict[str, int] = {
            "legacy_firmware": 600,
            "software": 600,
            "identity": 600,
            "combined_energy": 600,
            "inverter_temperature": 60,
            "pv": 10,
            "grid": 10,
            "battery": 10,
            "meter_power": 10,
            "export_bounds": 600,
            "battery_info": 600,
            "backup": 10,
            "state": 5,
            "energy": 600,
            "grid_flow": 10,
            "battery_status": 60,
            "battery_health": 600,
            "grid_output": 10,
            "load_settings": 10,
            "battery_settings": 10,
            "export_settings": 10,
            "active_limitation": 10,
            "inverter_firmware": 600,
            "communication_firmware": 600,
            "battery_firmware": 600,
            "apl": 10,
            "battery_limits": 10,
        }

    @property
    def serial_number(self) -> str | None:
        """Serial number read from the inverter."""
        return self.identity.inverter_serial

    @property
    def model(self) -> str | None:
        """Detected product model."""
        return self.profile.name if self.profile else None

    @property
    def battery_max_power(self) -> float | None:
        """Configured battery limit, capped by the battery and inverter ratings."""
        values = [
            float(v)
            for v in (
                self._battery_max_power,
                self.battery_info.bdc_rated_power,
                self.identity.inverter_rated_output,
            )
            if v is not None and 0 < v < 655350
        ]
        return min(values) if values else None

    async def async_identify(self) -> None:
        """Read identity and constrain optional fields once; performs no writes."""
        async with self._lock:
            if self.profile is not None:
                return
            await self.identity.async_update()
            serial = self.serial_number
            if (
                not serial
                or not serial.isascii()
                or not all(ch.isalnum() or ch in "-_" for ch in serial)
            ):
                raise UnsupportedDeviceError("Missing or invalid inverter serial")
            profile = identify(self.identity.device_type_code)
            for component_name, component in tuple(self.components.items()):
                keep = set(component.resolved_fields)
                if profile.phases == 1:
                    keep = {
                        k for k in keep if "phase_b" not in k and "phase_c" not in k
                    }
                keep = {
                    k
                    for k in keep
                    if not (k.startswith("mppt3") and profile.mppts < 3)
                    and not (k.startswith("mppt4") and profile.mppts < 4)
                }
                if (
                    (
                        component_name.endswith("_firmware")
                        and component_name != "legacy_firmware"
                        and not profile.extended_firmware
                    )
                    or (
                        component_name == "active_limitation"
                        and not profile.active_limitation
                    )
                ):
                    keep = set()
                component.restrict_fields(keep)
                if not keep:
                    self.components.pop(component_name)
                    self.intervals.pop(component_name)
            self.profile = profile

    async def async_update_components(self, names: Iterable[str]) -> UpdateReport:
        """Refresh selected subsystems, retaining failed values without notifying.

        A subsystem the device answers with an illegal-data-address exception is
        not polled again: the block is absent from this device rather than
        failing, so retrying it would only repeat the same refusal.
        """
        names = tuple(names)  # Snapshot before identification restricts the map.
        await self.async_identify()
        updated: set[str] = set()
        failed: dict[str, ModbusError] = {}
        absent: list[str] = []
        async with self._lock:
            for name in dict.fromkeys(names):
                if name not in self.components:
                    continue
                try:
                    await self.components[name].async_update(notify=False)
                except ModbusConnectionError:
                    raise
                except IllegalDataAddressError:
                    absent.append(name)
                    continue
                except ModbusTimeoutError as err:
                    if not updated:
                        raise
                    failed[name] = err
                except ModbusError as err:
                    failed[name] = err
                else:
                    updated.add(name)
            for name in absent:
                self._forget_absent(name)
            for name in updated:
                self.components[name].notify()
        return UpdateReport(updated, failed)

    def _forget_absent(self, name: str) -> None:
        """Stop serving a subsystem the device says it does not implement."""
        self.components.pop(name, None)
        self.intervals.pop(name, None)
        self.absent.add(name)
        _LOGGER.info(
            "Sungrow %s is not implemented by this device; it will not be polled",
            name,
        )

    async def async_update(self) -> UpdateReport:
        """Refresh every served subsystem."""
        await self.async_identify()
        return await self.async_update_components(self.components)

    async def async_update_readings(self) -> UpdateReport:
        """Refresh all measured values, leaving configuration unchanged."""
        return await self.async_update_components(
            n for n, c in self.components.items() if c.register_space == "input"
        )

    async def async_update_settings(self) -> UpdateReport:
        """Refresh settings after writes or on their own polling schedule."""
        return await self.async_update_components(
            n for n, c in self.components.items() if c.register_space == "holding"
        )

    async def async_write(self, component: str, field: str, value: int | float) -> None:
        """Validate, write once, delay for application, and verify by reading back."""
        await self.async_identify()
        target = self.components.get(component)
        if target is None or field not in target.resolved_fields:
            raise ValueError("This field is not supported by the detected model")
        if field in (
            "battery_forced_charge_discharge_power",
            "battery_max_charge_power",
            "battery_max_discharge_power",
        ):
            maximum = self.battery_max_power
            if maximum is None:
                raise ValueError("Battery power rating has not been read")
            if value > maximum:
                raise ValueError(f"Battery power exceeds {maximum} W")
        if field == "export_power_limit":
            low, high = (
                self.export_bounds.export_power_limit_min,
                self.export_bounds.export_power_limit_max,
            )
            if low is None or high is None or not low <= value <= high:
                raise ValueError("Export power is outside the reported bounds")
        async with self._lock:
            await target.write(field, value)
            await sleep(1)
            await target.async_update()
            if getattr(target, field) != value:
                raise ModbusError("The device did not confirm the requested value")

    async def async_command(self, command: InverterCommand) -> None:
        """Send a start/stop command to HOLDING 12999, not the input status word."""
        command = InverterCommand(command)
        await self.async_identify()
        async with self._lock:
            await self._unit.write_register(12999, int(command))

    async def async_read_raw(
        self,
    ) -> tuple[dict[str, dict[int, int | bool]], dict[str, str]]:
        """Read the served map for diagnostics; never read a command-only register.

        Returns the raw words plus the subsystems this device refused, keyed to
        the exception type name, so one absent block cannot empty the snapshot.
        """
        await self.async_identify()
        raw: dict[str, dict[int, int | bool]] = {}
        unreadable: dict[str, str] = {}
        async with self._lock:
            for name, component in self.components.items():
                try:
                    blocks = await component.async_read_raw(notify=False)
                except ModbusConnectionError:
                    raise
                except ModbusError as err:
                    unreadable[name] = type(err).__name__
                    continue
                for space, words in blocks.items():
                    raw.setdefault(space, {}).update(words)
        return raw, unreadable
