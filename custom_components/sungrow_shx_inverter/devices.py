"""Sub-device grouping: the inverter itself and its logical sub-assemblies.

Home Assistant renders one entity list per device, so the entities are split across
the parent inverter device and the sub-assemblies a user thinks of separately. The
parent keeps the inverter's own controls, status, system information, diagnostics,
grid connection and output; PV, battery, meter, energy statistics and backup output
each get their own device page. Entity names stay data-point-only, so the device name
supplies the context ("Battery power" rather than "Battery battery power").
"""

from .const import DOMAIN

#: The parent device, which already exists for every entry.
PARENT_DEVICE = "inverter"

#: Sub-device key to the label appended to the inverter model in its device name.
SUB_DEVICE_LABELS: dict[str, str] = {
    "pv": "PV",
    "battery": "Battery",
    "meter": "Meter",
    "energy": "Energy",
    "backup": "Backup",
}


def identifier(group: str, serial: str) -> set[tuple[str, str]]:
    """Return the device-registry identifier for a group."""
    if group == PARENT_DEVICE:
        return {(DOMAIN, serial)}
    return {(DOMAIN, f"{serial}_{group}")}
