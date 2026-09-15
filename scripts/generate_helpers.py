#!/usr/bin/env python3
"""Generate an optional YAML-compatible helper package for one inverter."""

import argparse
import json
from pathlib import Path
import re


def build(prefix: str, overrides: dict[str, str]) -> dict:
    """Build helpers using explicit entity IDs, without accessing a live system."""

    def entity(platform: str, key: str) -> str:
        return overrides.get(f"{platform}.{key}", f"{platform}.{prefix}_{key}")

    def action(platform: str, service: str, key: str, **data) -> dict:
        result = {
            "action": f"{platform}.{service}",
            "target": {"entity_id": entity(platform, key)},
        }
        if data:
            result["data"] = data
        return result

    def mode(ems: str, forced: str) -> list[dict]:
        return [
            action("select", "select_option", "ems_mode", option=ems),
            action(
                "select",
                "select_option",
                "battery_forced_charge_discharge",
                option=forced,
            ),
        ]

    delayed = []
    for name in (
        "pv_generating",
        "battery_charging",
        "battery_discharging",
        "positive_load_power",
        "exporting_power",
        "importing_power",
        "negative_load_power",
    ):
        source = entity("binary_sensor", name)
        delayed.append(
            {
                "name": f"{prefix} {name.replace('_', ' ')} delayed",
                "unique_id": f"{prefix}_{name}_delayed",
                "availability": "{{ has_value('" + source + "') }}",
                "state": "{{ is_state('" + source + "', 'on') }}",
                "delay_on": {"seconds": 60},
            }
        )
    scripts = {
        "self_consumption_max_battery_discharge": [
            *mode("self_consumption_mode", "stop"),
            action(
                "number",
                "set_value",
                "battery_max_discharge_power",
                value="{{ state_attr('"
                + entity("number", "battery_max_discharge_power")
                + "', 'max') }}",
            ),
        ],
        "self_consumption_no_battery_discharge": [
            *mode("self_consumption_mode", "stop"),
            action("number", "set_value", "battery_max_discharge_power", value=10),
        ],
        "zero_export_power": [
            action("switch", "turn_on", "export_power_limit"),
            action("number", "set_value", "export_power_limit", value=0),
        ],
        "max_export_power": [
            action("switch", "turn_on", "export_power_limit"),
            action(
                "number",
                "set_value",
                "export_power_limit",
                value="{{ state_attr('"
                + entity("number", "export_power_limit")
                + "', 'max') }}",
            ),
        ],
        "battery_bypass": mode("forced_mode", "stop"),
        "battery_forced_discharge": mode("forced_mode", "forced_discharge"),
        "battery_forced_charge": mode("forced_mode", "forced_charge"),
    }
    danger_key = f"{prefix}_dashboard_enable_danger_mode"
    return {
        "template": [{"binary_sensor": delayed}],
        "sensor": [
            {
                "platform": "filter",
                "name": f"{prefix} daily consumed energy filtered",
                "unique_id": f"{prefix}_daily_consumed_energy_filtered",
                "entity_id": entity("sensor", "daily_consumed_energy"),
                "filters": [
                    {
                        "filter": "time_simple_moving_average",
                        "window_size": "00:05:00",
                        "precision": 2,
                    }
                ],
            }
        ],
        "input_boolean": {
            danger_key: {
                "name": f"{prefix} dashboard enable danger mode",
                "initial": False,
            },
        },
        "automation": [
            {
                "id": f"{prefix}_reset_dashboard_danger_mode",
                "alias": f"{prefix} reset dashboard danger mode",
                "triggers": [
                    {
                        "trigger": "state",
                        "entity_id": f"input_boolean.{danger_key}",
                        "to": "on",
                    }
                ],
                "actions": [
                    {"delay": "00:01:00"},
                    {
                        "action": "input_boolean.turn_off",
                        "target": {
                            "entity_id": f"input_boolean.{danger_key}",
                        },
                    },
                ],
                "mode": "restart",
            }
        ],
        "script": {
            f"{prefix}_{key}": {
                "alias": f"{prefix} {key.replace('_', ' ')}",
                "sequence": steps,
                "mode": "single",
            }
            for key, steps in scripts.items()
        },
    }


def main() -> None:
    """Write JSON, which is also valid YAML, to an explicitly selected file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entity-prefix", required=True, help="For example sungrow_sh10rt"
    )
    parser.add_argument(
        "--entity-map",
        type=Path,
        help="Optional JSON map: sensor.daily_consumed_energy -> actual entity ID",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9_]+", args.entity_prefix):
        parser.error(
            "Entity prefix must contain lowercase letters, numbers and underscores"
        )
    overrides = json.loads(args.entity_map.read_text()) if args.entity_map else {}
    if not isinstance(overrides, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in overrides.items()
    ):
        parser.error("Entity map must be a JSON object of string entity IDs")
    if args.output.exists():
        parser.error("Output already exists; choose another path")
    args.output.write_text(
        "# Optional helper package; verify all entity IDs before enabling.\n"
        "# Preset scripts issue writes only when explicitly invoked.\n"
        + json.dumps(build(args.entity_prefix, overrides), indent=2)
        + "\n"
    )
    print(f"Created {args.output}; no live configuration was changed")


if __name__ == "__main__":
    main()
