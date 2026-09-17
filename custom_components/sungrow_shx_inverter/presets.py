"""Mode presets that reproduce the source YAML scenes as one user choice.

Each preset is the same sequence of register writes the upstream scenes performed,
but the export and battery maxima are read from the live inverter instead of a
secret, so no generated helpers or automations are required.
"""

from dataclasses import dataclass

from ._vendor.sungrow_shx_inverter import SungrowSHxInverter
from ._vendor.sungrow_shx_inverter.enums import EmsMode, Enable, ForcedChargeDischarge


@dataclass(frozen=True)
class PresetStep:
    """One validated register write inside a preset.

    A ``value`` of ``None`` marks a "maximum" step: the target is the inverter's
    own live maximum, resolved by :func:`resolve_value` from the field name.
    """

    component: str
    field: str
    value: int | float | None = None

    @property
    def is_maximum(self) -> bool:
        """Whether this step targets the inverter's own maximum."""
        return self.value is None


PRESETS: dict[str, tuple[PresetStep, ...]] = {
    "self_consumption_max_battery_discharge": (
        PresetStep(
            "battery_settings", "ems_mode_selection_raw", EmsMode.SELF_CONSUMPTION
        ),
        PresetStep(
            "battery_settings",
            "battery_forced_charge_discharge_cmd_raw",
            ForcedChargeDischarge.STOP,
        ),
        PresetStep("battery_limits", "battery_max_discharge_power"),
    ),
    "self_consumption_no_battery_discharge": (
        PresetStep(
            "battery_settings", "ems_mode_selection_raw", EmsMode.SELF_CONSUMPTION
        ),
        PresetStep(
            "battery_settings",
            "battery_forced_charge_discharge_cmd_raw",
            ForcedChargeDischarge.STOP,
        ),
        PresetStep("battery_limits", "battery_max_discharge_power", 10),
    ),
    "zero_export": (
        PresetStep("export_settings", "export_power_limit_mode_raw", Enable.ENABLED),
        PresetStep("export_settings", "export_power_limit", 0),
    ),
    "max_export": (
        PresetStep("export_settings", "export_power_limit_mode_raw", Enable.ENABLED),
        PresetStep("export_settings", "export_power_limit"),
    ),
    "battery_bypass": (
        PresetStep("battery_settings", "ems_mode_selection_raw", EmsMode.FORCED),
        PresetStep(
            "battery_settings",
            "battery_forced_charge_discharge_cmd_raw",
            ForcedChargeDischarge.STOP,
        ),
    ),
    "battery_forced_discharge": (
        PresetStep("battery_settings", "ems_mode_selection_raw", EmsMode.FORCED),
        PresetStep(
            "battery_settings",
            "battery_forced_charge_discharge_cmd_raw",
            ForcedChargeDischarge.DISCHARGE,
        ),
    ),
    "battery_forced_charge": (
        PresetStep("battery_settings", "ems_mode_selection_raw", EmsMode.FORCED),
        PresetStep(
            "battery_settings",
            "battery_forced_charge_discharge_cmd_raw",
            ForcedChargeDischarge.CHARGE,
        ),
    ),
}

PRESET_KEYS = tuple(PRESETS)


def fallback_maximum(
    device: SungrowSHxInverter, step: PresetStep
) -> int | float | None:
    """A lower, device-derived ceiling to retry when a maximum is still refused.

    ``battery_max_power`` now considers the inverter's rated output as well as the BDC
    rating, so the first write should already be accepted; this remains the safety net for
    a device that refuses the value for a reason of its own.
    """
    if step.field == "battery_max_discharge_power":
        return device.identity.inverter_rated_output
    return None


def resolve_value(device: SungrowSHxInverter, step: PresetStep) -> int | float:
    """Return the concrete write value, reading live maxima where the step asks."""
    if step.value is not None:
        return step.value
    if step.field == "battery_max_discharge_power":
        maximum = device.battery_max_power
        if maximum is None:
            raise ValueError("Battery power rating has not been read")
        return maximum
    if step.field == "export_power_limit":
        maximum = device.export_bounds.export_power_limit_max
        if maximum is None:
            raise ValueError("Export power limits have not been read")
        return maximum
    raise ValueError(f"{step.field} has no dynamic maximum")
