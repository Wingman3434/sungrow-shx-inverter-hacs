# Sungrow SHx Inverter

Local monitoring of solar PV generation, household load, grid import/export,
optional battery storage, backup output, inverter operating state and firmware.
The full community build also exposes the source-defined EMS, battery, export
and load-adjustment controls. This is a UI-configured implementation of Martin
Kaiser's register map, not the upstream YAML package itself.

## Connection and model scope

The register map contains 40 model codes across SH*K, SH*RS, SH*RT (including
-20/V112/V122), SH*T, and the related MG5RL/MG6RL models. A recognised code is
not proof that every register works on every firmware/interface. This new
implementation has **not yet been tested on physical hardware**. The upstream
author's SH10RT/Pylontech Force H1 experience is not testing of this new code.

A battery is optional; battery-dependent readings may be unavailable without one.
Some meter readings require a directly connected energy meter. Single-phase,
MPPT-count, firmware and documented RS/MG restrictions filter the entities.
Unknown model codes are rejected. iHomeManager has a different register map and
is not supported. Wallboxes and Logger1000 are also outside this package.

Prefer the inverter's internal Ethernet port where available. It may need
enabling through Sungrow's documented local commissioning process. WiNet-S LAN
and Wi-Fi may be slower and expose fewer registers. No iSolarCloud account,
installer password, cloud API or Internet connection is needed for Modbus reads.
Firmware updates and installer-only commissioning remain outside this integration.

## Install the community build

1. Use Home Assistant 2026.9.2 or later and take a backup.
2. Disable the old Sungrow YAML polling/control package and any previous test
   integration before enabling this one on that inverter. Preserve history.
3. Before publication, copy only
   `custom_components/sungrow_shx_inverter` into your configuration's
   `custom_components` directory. After publication, use the HACS custom
   repository `Wingman3434/sungrow-shx-inverter-hacs`.
4. Restart, then Settings → Devices & services → Add integration →
   **Sungrow SHx Inverter**.
5. Enter the inverter host, TCP port (usually 502), unit ID (usually 1), and
   message gap in **seconds**. Use your existing connection settings.

A 5 ms gap is **0.005 seconds**; 20 ms is 0.02; 100 ms is 0.1.
The upstream notes suggest 5 ms for internal LAN and 20–30 ms or more for
WiNet-S. This build defaults to a conservative 100 ms. Tune only after testing.

In the full build, use **Configure / Options** to set an optional battery power
cap in watts. Clear the field to use the reported BDC limit. The lower of the
two limits is enforced when controls are used; a BDC rating is not certification
of the installed battery's safe limit. Setting an option itself issues no write.
Use **Reconfigure** to change host, port, unit ID or message gap.

For multiple inverters add one entry per physical serial number. Devices on the
same endpoint but different unit IDs share the built-in Modbus connection.
There is no three-inverter limit or need to duplicate YAML. Aggregate only
non-overlapping energy flows to avoid double-counting.

## Energy Dashboard

Select the entities for the relevant inverter, using their actual entity IDs:

| Dashboard field | Entity |
| --- | --- |
| Grid consumption energy | Total imported energy |
| Return to grid energy | Total exported energy |
| Grid power | Meter active power (positive import, negative export) |
| Solar production energy | Total PV generation |
| Solar production power | Total DC power |
| Battery charged energy | Total battery charge |
| Battery discharged energy | Total battery discharge |
| Battery power | Battery power (negative charging, positive discharging) |

Do not count the combined PV-plus-battery generation sensor as solar generation,
or add derived and direct totals for the same flow. Phase V×I is an **apparent
power magnitude in VA**, not measured active power; reactive power is in var.
The raw grid-export register uses the opposite sign from meter active power.

Energy values are cached/restored without fabricating zero, but are marked
unavailable during failed polls. Daily counters reset; a retained value is not a
new measurement. Automated tests do not establish midnight behaviour on hardware.

## Full community controls and helpers

The full build has 120 sensor descriptions, seven immediate power-flow binary
sensors, nine numbers, three selects, three switches and two disabled-by-default
start/stop buttons. Model filtering reduces actual counts.

Controls cover EMS modes; forced battery charge/discharge/stop; minimum, maximum
and backup-reserved SoC; charge/discharge power and start thresholds; backup mode;
export limitation; and load adjustment. Settings writes check bounds, inverse
scaling and one-second delayed readback. Start/stop are write-only commands,
not falsely read-back-confirmed switches. No controls execute at setup/poll time.

The upstream low-SoC forced-start control remains excluded due to its documented
issue. Undocumented APL and active-limitation fields stay read-only where the
source provides no enabled control.

An **Operating preset** selector is built in, so no helpers or scripts are needed
for the common modes. Choosing an option applies the same sequence the upstream
scenes applied: EMS mode, forced charge/discharge command and the relevant
limit. The export and battery-power presets read the inverter's live maximum
instead of a configured secret. The same action is exposed as the
`sungrow_shx_inverter.set_preset` service for automations, and the selector
itself can be used from scenes and dashboards. Presets write only when chosen;
nothing executes at setup or poll time.

`scripts/generate_helpers.py` can generate an **optional** helper package:
seven delayed flags, the five-minute daily-consumption filter and a dashboard
visibility toggle with timed reset. The seven preset scripts it also emits are
now redundant with the built-in selector; keep only the parts you want. Nothing
installs it automatically. Review generated entity IDs. The visibility toggle
only hides dashboard controls; it is not an authorization mechanism. A script's
sequence is not an atomic inverter operation, and neither is a preset.

The upstream overview/details/EMS dashboards can inform your layout, but their
entity IDs and scenes do not automatically match this integration. They are not
bundled or silently installed. See OPTIONAL_HELPERS.md and SOURCE_COVERAGE.md.

## Testing and troubleshooting

Start with read-only observation across daylight, overnight and midnight.
Compare model/serial, signs, energy totals and power with local inverter readings,
allowing for app update delays. Verify restart and connection-loss recovery.
Then test one normally used control at a time and restore its original setting.

Check Settings → System → Logs for this integration. Full HACS/follow-up builds
provide downloadable diagnostics with host and serial identity omitted, including
raw serial words. Include firmware, model, interface, versions, expected/actual
behaviour, and a redacted diagnostic file in a report to **this project's**
issue tracker. Do not assume an absent optional register is a failed connection.

Home Assistant 2026.9.2's Modbus 4.10.0 uses a 10-second timeout without
configurable connect delay. That version cannot exactly reproduce the source's
30-second timeout/15-second delay. Current Core dev pins Modbus 4.12.0, which
supports per-unit timing requirements; the library automatically requests those
source timings when available. No private transport patch or user dependency
override is needed. See MODBUS_API_REVIEW.md.

## Earlier test bundle and rollback

This release changes the experimental domain from `sungrow` to
`sungrow_shx_inverter`. This is **not an in-place config-entry migration**.
If you installed the earlier unpublished bundle, disable its entry, keep a
backup of its files/settings, install the renamed folder, and add a new entry.
Review dashboard, automation and Energy Dashboard entity selections. Do not
edit `.storage` manually or delete recorder history to perform this rename.
Old and new versions must not poll the same inverter simultaneously.

For rollback, disable the new entry and restore the previous configuration from
your backup. To remove this integration, use its entry menu in Devices & services
and remove its HACS/manual files if desired, then restart. Removing an integration
does not restore settings previously written to the inverter.
