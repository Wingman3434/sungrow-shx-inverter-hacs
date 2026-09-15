"""Pure derived measurements; missing inputs never become fabricated zeros."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import RUNNING_STATES

if TYPE_CHECKING:
    from .device import SungrowSHxInverter


class DerivedReadings:
    """Computed readings over the inverter's latest decoded state."""

    def __init__(self, device: SungrowSHxInverter) -> None:
        self._device = device

    @property
    def mppt1_power(self) -> int | None:
        """Mppt1 power."""
        v0 = self._device.pv.mppt1_voltage
        v1 = self._device.pv.mppt1_current
        if v0 is None or v1 is None:
            return None
        return int(v0 * v1)

    @property
    def mppt2_power(self) -> int | None:
        """Mppt2 power."""
        v0 = self._device.pv.mppt2_voltage
        v1 = self._device.pv.mppt2_current
        if v0 is None or v1 is None:
            return None
        return int(v0 * v1)

    @property
    def mppt3_power(self) -> int | None:
        """Mppt3 power."""
        v0 = self._device.pv.mppt3_voltage
        v1 = self._device.pv.mppt3_current
        if v0 is None or v1 is None:
            return None
        return int(v0 * v1)

    @property
    def mppt4_power(self) -> int | None:
        """Mppt4 power."""
        v0 = self._device.pv.mppt4_voltage
        v1 = self._device.pv.mppt4_current
        if v0 is None or v1 is None:
            return None
        return int(v0 * v1)

    @property
    def phase_a_power(self) -> int | None:
        """Phase a power."""
        v0 = self._device.grid.phase_a_voltage
        v1 = self._device.grid_output.phase_a_current
        if v0 is None or v1 is None:
            return None
        return int(abs(v0 * v1))

    @property
    def phase_b_power(self) -> int | None:
        """Phase b power."""
        v0 = self._device.grid.phase_b_voltage
        v1 = self._device.grid_output.phase_b_current
        if v0 is None or v1 is None:
            return None
        return int(abs(v0 * v1))

    @property
    def phase_c_power(self) -> int | None:
        """Phase c power."""
        v0 = self._device.grid.phase_c_voltage
        v1 = self._device.grid_output.phase_c_current
        if v0 is None or v1 is None:
            return None
        return int(abs(v0 * v1))

    @property
    def inverter_state(self) -> str | None:
        """Inverter state."""
        v0 = self._device.state.running_state_raw
        if v0 is None:
            return None
        return RUNNING_STATES.get(v0, f"Unknown running state code: 0x{v0:04X}")

    @property
    def device_type(self) -> str | None:
        """Device type."""
        v0 = self._device.identity.device_type_code
        if v0 is None:
            return None
        return self._device.model

    @property
    def battery_charging_power_signed(self) -> int | None:
        """Battery charging power signed."""
        v0 = self._device.battery.battery_power
        if v0 is None:
            return None
        return -v0

    @property
    def battery_discharging_power_signed(self) -> int | None:
        """Battery discharging power signed."""
        v0 = self._device.battery.battery_power
        if v0 is None:
            return None
        return v0

    @property
    def battery_charging_power(self) -> int | None:
        """Battery charging power."""
        v0 = self._device.battery.battery_power
        if v0 is None:
            return None
        return max(-v0, 0)

    @property
    def battery_discharging_power(self) -> int | None:
        """Battery discharging power."""
        v0 = self._device.battery.battery_power
        if v0 is None:
            return None
        return max(v0, 0)

    @property
    def import_power(self) -> int | None:
        """Import power."""
        v0 = self._device.grid_flow.export_power_raw
        if v0 is None:
            return None
        return max(-v0, 0)

    @property
    def export_power(self) -> int | None:
        """Export power."""
        v0 = self._device.grid_flow.export_power_raw
        if v0 is None:
            return None
        return max(v0, 0)

    @property
    def battery_level_nominal(self) -> float | None:
        """Battery level nominal."""
        v0 = self._device.battery_settings.battery_min_soc
        v1 = self._device.battery_settings.battery_max_soc
        v2 = self._device.battery_status.battery_level
        if v0 is None or v1 is None or v2 is None:
            return None
        return round(v0 + (v1 - v0) * v2 / 100, 1)

    @property
    def battery_charge_nominal(self) -> float | None:
        """Battery charge nominal."""
        v0 = self._device.battery_info.battery_capacity_high_precision
        v1 = self._device.derived.battery_level_nominal
        if v0 is None or v1 is None:
            return None
        return round(v0 * v1 / 100, 1)

    @property
    def battery_charge(self) -> float | None:
        """Battery charge."""
        v0 = self._device.battery_info.battery_capacity_high_precision
        v1 = self._device.battery_settings.battery_max_soc
        v2 = self._device.battery_settings.battery_min_soc
        v3 = self._device.battery_status.battery_level
        if v0 is None or v1 is None or v2 is None or v3 is None:
            return None
        return round(v0 * (v1 - v2) / 100 * v3 / 100, 2)

    @property
    def battery_charge_health_rated(self) -> float | None:
        """Battery charge health rated."""
        v0 = self._device.derived.battery_charge
        v1 = self._device.battery_health.battery_state_of_health
        if v0 is None or v1 is None:
            return None
        return round(v0 * v1 / 100, 2)

    @property
    def daily_consumed_energy(self) -> float | None:
        """Daily consumed energy."""
        v0 = self._device.energy.daily_pv_generation
        v1 = self._device.energy.daily_exported_energy
        v2 = self._device.energy.daily_imported_energy
        v3 = self._device.energy.daily_battery_charge
        v4 = self._device.energy.daily_battery_discharge
        if v0 is None or v1 is None or v2 is None or v3 is None or v4 is None:
            return None
        return round(v0 - v1 + v2 - v3 + v4, 1)

    @property
    def total_consumed_energy(self) -> float | None:
        """Total consumed energy."""
        v0 = self._device.energy.total_pv_generation
        v1 = self._device.energy.total_exported_energy
        v2 = self._device.energy.total_imported_energy
        v3 = self._device.energy.total_battery_charge
        v4 = self._device.energy.total_battery_discharge
        if v0 is None or v1 is None or v2 is None or v3 is None or v4 is None:
            return None
        return round(v0 - v1 + v2 - v3 + v4, 1)

    @property
    def pv_generating(self) -> bool | None:
        """Pv generating."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 0))

    @property
    def battery_charging(self) -> bool | None:
        """Battery charging."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 1))

    @property
    def battery_discharging(self) -> bool | None:
        """Battery discharging."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 2))

    @property
    def positive_load_power(self) -> bool | None:
        """Positive load power."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 3))

    @property
    def exporting_power(self) -> bool | None:
        """Exporting power."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 4))

    @property
    def importing_power(self) -> bool | None:
        """Importing power."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 5))

    @property
    def negative_load_power(self) -> bool | None:
        """Negative load power."""
        v0 = self._device.state.power_flow_status
        if v0 is None:
            return None
        return bool(v0 & (1 << 7))
