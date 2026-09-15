For the full HACS/follow-up build only; the sensor-first Core build has no control or binary-sensor platforms.

# Optional UI helpers

The common mode presets are **built into the integration** as the `Operating
preset` selector (and the `sungrow_shx_inverter.set_preset` service), so you do
not need helpers or scripts for them. Use this generator only for the extra
dashboard niceties: delayed flags, the consumed-energy filter and the timed
visibility toggle. Its seven preset scripts are redundant with the built-in
selector.

These are not device-library fields and are never installed automatically.
Generate a separate package for one inverter:

    python scripts/generate_helpers.py --entity-prefix sungrow_shx_inverter_sh10rt --output sungrow_helpers.yaml

Check actual entity IDs in Developer Tools first. If any differ, supply
--entity-map mapping.json, a JSON object mapping a logical key such as
number.battery_max_discharge_power to the actual entity ID. Each inverter
needs a distinct prefix. The output is JSON-form YAML, valid as a Home Assistant
package. Review it and include it through your normal packages configuration.

It supplies seven 60-second delayed flags, the five-minute consumed-energy
filter, a dashboard-only input_boolean that resets after one minute, and seven
mode-preset scripts. Scripts read the current entity maximum for export and
battery power instead of needing the old secrets. Scripts issue device writes
only when invoked. The input_boolean is presentation state, not a device write
interlock; use explicit entity enablement and your own dashboard controls.

Dashboard references to the old danger-mode switch must change to the generated
input_boolean. Preset scenes are now scripts; update scene buttons accordingly.
No old entities, history, scenes or automations are deleted by the generator.
