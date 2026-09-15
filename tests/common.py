"""Sungrow SHx Inverter common checks."""

from homeassistant.helpers import entity_registry as er

from . import SERIAL


def entity_id(registry: er.EntityRegistry, platform: str, key: str) -> str:
    """Entity id."""
    result = registry.async_get_entity_id(
        platform, "sungrow_shx_inverter", f"{SERIAL}_{key}"
    )
    assert result is not None
    return result
