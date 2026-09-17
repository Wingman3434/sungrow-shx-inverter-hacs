"""Shared typed entity metadata, identity and subsystem availability."""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from modbus_connection import ModbusError

from .const import DOMAIN
from .coordinator import SungrowCoordinator
from .devices import PARENT_DEVICE


@dataclass(frozen=True, kw_only=True)
class SungrowDescription(EntityDescription):
    """A library attribute and the register fields it depends on."""

    component: str
    field: str
    dependencies: tuple[str, ...]
    source_fields: tuple[tuple[str, str], ...]
    device: str = PARENT_DEVICE


def is_supported(
    coordinator: SungrowCoordinator, description: SungrowDescription
) -> bool:
    """Filter entity creation by detected model capabilities, never by live zeros."""
    return all(
        component in coordinator.device.components
        and field in coordinator.device.components[component].resolved_fields
        for component, field in description.source_fields
    )


class SungrowEntity(CoordinatorEntity[SungrowCoordinator]):
    """Entity whose state is fresh only when all of its inputs are fresh."""

    _attr_has_entity_name = True
    entity_description: SungrowDescription

    def __init__(
        self, coordinator: SungrowCoordinator, description: SungrowDescription
    ) -> None:
        """Initialize the entity or coordinator."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device.serial_number}_{description.key}"
        self._attr_device_info = coordinator.device_info_for(description.device)

    @property
    @override
    def available(self) -> bool:
        """Whether all required subsystems have answered since the last failure."""
        return super().available and all(
            name in self.coordinator.data.updated
            for name in self.entity_description.dependencies
        )

    def _value(self) -> Any:
        """Value."""
        return getattr(
            getattr(self.coordinator.device, self.entity_description.component),
            self.entity_description.field,
        )

    async def _async_write(self, value: float) -> None:
        """Write once and map device failures to translated action errors."""
        try:
            await self.coordinator.device.async_write(
                self.entity_description.component, self.entity_description.field, value
            )
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_value"
            ) from err
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="write_failed"
            ) from err
        await self.coordinator.async_refresh_components(
            self.entity_description.component, "state"
        )
