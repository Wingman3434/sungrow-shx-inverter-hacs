"""Sungrow SHx Inverter translation file contract checks.

Home Assistant validates these files with hassfest, not with the integration's
own code, so a broken translation file can ship past a green unit suite.
"""

import json
from pathlib import Path
from typing import Any

from . import DOMAIN

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / DOMAIN
STRINGS = INTEGRATION / "strings.json"
EN_TRANSLATIONS = INTEGRATION / "translations" / "en.json"


def load(path: Path) -> dict[str, Any]:
    """Load a translation file as JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def mapping(value: Any, path: str) -> dict[str, Any]:
    """Return a value Home Assistant's schema requires to be a mapping."""
    assert isinstance(value, dict), (
        f"{path} must be a mapping, got {type(value).__name__}"
    )
    return value


def string_mapping(value: Any, path: str) -> dict[str, Any]:
    """Return a flat section Home Assistant requires to hold strings."""
    result = mapping(value, path)
    for key, item in result.items():
        assert isinstance(item, str) and item.strip(), (
            f"{path}.{key} must be a non-empty string, got {item!r}"
        )
    return result


def test_exceptions_are_message_mappings() -> None:
    """Every exception is a mapping with the non-empty message HA renders."""
    exceptions = mapping(load(STRINGS).get("exceptions"), "exceptions")
    assert exceptions, "exceptions must not be empty"
    for key, value in exceptions.items():
        entry = mapping(value, f"exceptions.{key}")
        message = entry.get("message")
        assert isinstance(message, str) and message.strip(), (
            f"exceptions.{key}.message must be a non-empty string, got {message!r}"
        )


def test_nested_sections_stay_mappings() -> None:
    """Sections HA consumes as nested mappings keep their shape."""
    strings = load(STRINGS)

    for section in ("config", "options"):
        flow = mapping(strings.get(section), section)
        steps = mapping(flow.get("step"), f"{section}.step")
        assert steps, f"{section}.step must not be empty"
        for step_id, step in steps.items():
            step = mapping(step, f"{section}.step.{step_id}")
            for field in ("data", "data_description"):
                if field in step:
                    string_mapping(step[field], f"{section}.step.{step_id}.{field}")
            # hassfest rejects a description for a field without a data entry.
            unknown = set(step.get("data_description", ())) - set(step.get("data", ()))
            assert not unknown, (
                f"{section}.step.{step_id}.data_description has keys without data: "
                f"{sorted(unknown)}"
            )
        for field in ("error", "abort"):
            if field in flow:
                string_mapping(flow[field], f"{section}.{field}")

    entity = mapping(strings.get("entity"), "entity")
    for platform, entries in entity.items():
        for key, entry in mapping(entries, f"entity.{platform}").items():
            entry = mapping(entry, f"entity.{platform}.{key}")
            if "state" in entry:
                string_mapping(entry["state"], f"entity.{platform}.{key}.state")

    services = mapping(strings.get("services"), "services")
    for service, definition in services.items():
        definition = mapping(definition, f"services.{service}")
        for field in ("name", "description"):
            value = definition.get(field)
            assert isinstance(value, str) and value.strip(), (
                f"services.{service}.{field} must be a non-empty string, got {value!r}"
            )
        fields = mapping(definition.get("fields", {}), f"services.{service}.fields")
        for field, spec in fields.items():
            name = mapping(spec, f"services.{service}.fields.{field}").get("name")
            assert isinstance(name, str) and name.strip(), (
                f"services.{service}.fields.{field}.name must be a non-empty string, "
                f"got {name!r}"
            )


def test_translations_en_matches_strings() -> None:
    """The shipped English translation is byte-identical to strings.json."""
    assert EN_TRANSLATIONS.read_bytes() == STRINGS.read_bytes(), (
        "translations/en.json has drifted from strings.json "
        f"({EN_TRANSLATIONS.stat().st_size} vs {STRINGS.stat().st_size} bytes)"
    )
