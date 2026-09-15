"""Power-flow bit flags."""

from dataclasses import dataclass
from typing import cast, override

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SungrowConfigEntry
from .entity import SungrowDescription, SungrowEntity, is_supported


@dataclass(frozen=True, kw_only=True)
class SungrowBinaryDescription(BinarySensorEntityDescription, SungrowDescription):
    """A platform-specific typed entity description."""


PARALLEL_UPDATES = 0
BINARY_SENSORS = (
    SungrowBinaryDescription(
        key="pv_generating",
        translation_key="pv_generating",
        component="derived",
        field="pv_generating",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="battery_charging",
        translation_key="battery_charging",
        component="derived",
        field="battery_charging",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="battery_discharging",
        translation_key="battery_discharging",
        component="derived",
        field="battery_discharging",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="positive_load_power",
        translation_key="positive_load_power",
        component="derived",
        field="positive_load_power",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="exporting_power",
        translation_key="exporting_power",
        component="derived",
        field="exporting_power",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="importing_power",
        translation_key="importing_power",
        component="derived",
        field="importing_power",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
    SungrowBinaryDescription(
        key="negative_load_power",
        translation_key="negative_load_power",
        component="derived",
        field="negative_load_power",
        dependencies=("state",),
        source_fields=(("state", "power_flow_status"),),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the seven defined status bits, excluding reserved bit 6."""
    async_add_entities(
        SungrowBinarySensor(entry.runtime_data, description)
        for description in BINARY_SENSORS
        if is_supported(entry.runtime_data, description)
    )


class SungrowBinarySensor(SungrowEntity, BinarySensorEntity):
    """A device-reported power-flow flag."""

    entity_description: SungrowBinaryDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return the bit state, or None when the source is absent."""
        return cast(bool | None, self._value())
