# Dashboard and Energy Dashboard

How to point Home Assistant's built-in Energy Dashboard and your own Lovelace
dashboards at this integration's entities. This document **complements**
[USER_GUIDE.md](USER_GUIDE.md); it does not repeat its "Energy Dashboard" or
"Full community controls and helpers" sections, which remain the authority on
signs, caching and controls. Read those first if you have not.

Nothing here has been run on a physical inverter. The entity IDs below are
**derived from the source code**, not confirmed against a live installation.

## Entity IDs are model-specific

This integration names each entity as `"<device name> <entity name>"`:

- `entity.py` sets `_attr_has_entity_name = True`, so Home Assistant builds the
  entity ID from the device name plus the translated entity name.
- `coordinator.py` sets
  `DeviceInfo(name=f"Sungrow SHx Inverter {self.device.model}")`, and
  `device.model` returns the detected profile name (for example `SH20T`, device
  code `3622` in `_vendor/sungrow_shx_inverter/variants.py`).

So the entity ID is the slug of `"Sungrow SHx Inverter <MODEL> <ENTITY NAME>"`.
For an SH20T the device-name slug is `sungrow_shx_inverter_sh20t`, giving:

```
sensor.sungrow_shx_inverter_sh20t_total_pv_generation
```

Every entity on that device shares the same prefix; only the trailing entity
name changes. **Different models produce different IDs** — an SH10RT yields
`sungrow_shx_inverter_sh10rt_...`, and so on.

### Confirm your own IDs

The IDs below are examples for the maintainer's SH20T. **Confirm yours before
copying anything:**

1. Settings → Devices & services → **Sungrow SHx Inverter** → open the inverter
   device.
2. The entity list shows each entity's ID (the "Entity ID" column / the ⓘ
   dialog).
3. Or use Developer Tools → States and filter on `sungrow_shx_inverter`.

## 1. Built-in Energy Dashboard

Settings → Dashboards → **Energy** → ⋮ → **Edit**. Map each field to the entity
of the matching name. The upstream YAML package used the same concepts under
its own entity names; the table notes the upstream name you would be migrating
from and the SH20T ID here.

| Energy Dashboard field | New entity (name) | Upstream entity | SH20T example entity ID |
| --- | --- | --- | --- |
| Grid consumption | Total imported energy | Total imported energy | `sensor.sungrow_shx_inverter_sh20t_total_imported_energy` |
| Return to grid | Total exported energy | Total exported energy | `sensor.sungrow_shx_inverter_sh20t_total_exported_energy` |
| Grid power | Meter active power | Meter active power | `sensor.sungrow_shx_inverter_sh20t_meter_active_power` |
| Solar production → energy | Total PV generation | Total PV generation | `sensor.sungrow_shx_inverter_sh20t_total_pv_generation` |
| Solar production → power | Total DC power | Total DC power | `sensor.sungrow_shx_inverter_sh20t_total_dc_power` |
| Battery → energy charged | Total battery charge | Total battery charge | `sensor.sungrow_shx_inverter_sh20t_total_battery_charge` |
| Battery → energy discharged | Total battery discharge | Total battery discharge | `sensor.sungrow_shx_inverter_sh20t_total_battery_discharge` |
| Battery → power | Battery power | Battery discharging power signed | `sensor.sungrow_shx_inverter_sh20t_battery_power` |

Caveats carried from USER_GUIDE.md, repeated here because they change the
Energy Dashboard result:

- **Meter active power** is positive on import and negative on export; the raw
  grid-export register uses the opposite sign. Do not substitute one for the
  other.
- Do **not** select the combined **Total PV generation & battery discharge**
  (`..._total_pv_generation_battery_discharge`) as solar production, and do not
  also add the PV and battery totals for the same flow.
- **Phase A/B/C apparent power** (`..._phase_a_power`) is a VA magnitude, not
  measured active power; reactive power is in var. Keep them off the Energy
  Dashboard power fields.
- **Battery power** and **Battery discharging power signed** are the *same
  reading with the same sign* — both derive from holding register `5213`, positive
  while discharging and negative while charging (`derived.py` returns the raw
  value for the discharging sensor and its negation for the charging one). Pick
  either, but never add both. This document uses `Battery power` to match
  USER_GUIDE.md; the upstream package selected the equivalent
  `Battery discharging power signed`.

## 2. Custom Lovelace dashboard (optional)

The upstream project ships three example tabs — **Overview**, **Details** and
**EMS control**. This integration does not bundle or install any dashboard, and
the upstream entity IDs and scenes do not match it. If you want that layout
back, rebuild it against the entity **names** below.

**Untested starter only.** The YAML at the end of this section is a minimal
sketch, not a guaranteed-working dashboard. It assumes the SH20T device-name
prefix `sungrow_shx_inverter_sh20t`; replace it with your own prefix and verify
each entity ID first. Treat it as a starting point to edit in the raw
configuration editor, not something to paste blindly.

Suggested contents by tab:

- **Overview** — live flows and today's energy:
  `Total DC power`, `Load power`, `Meter active power`, `Battery power`,
  `Battery level`, `Daily PV generation`.
- **Details** — per-string and electrical detail:
  `MPPT1..4 voltage` / `MPPT1..4 current`, `Phase A/B/C voltage`,
  `Phase A/B/C current`, `Inverter temperature`, `Running state raw`,
  `Inverter Firmware Version`.
- **EMS control** — the built-in controls (no helpers needed):
  the **Operating preset** selector, `EMS mode`,
  `Battery forced charge discharge`, `Battery Min Soc`, `Battery Max Soc`,
  `Export power limit`.

The **Operating preset** selector replaces the upstream preset scenes; see
USER_GUIDE.md and OPTIONAL_HELPERS.md for why the generated preset scripts are
now redundant.

Minimal starter (untested — verify and edit):

```yaml
# Starter Lovelace tab. Replace the sungrow_shx_inverter_sh20t_* prefix with
# your device's prefix and confirm every entity ID before use.
title: Sungrow
views:
  - title: Overview
    cards:
      - type: entities
        title: Live power (W)
        entities:
          - sensor.sungrow_shx_inverter_sh20t_total_dc_power
          - sensor.sungrow_shx_inverter_sh20t_load_power
          - sensor.sungrow_shx_inverter_sh20t_meter_active_power
          - sensor.sungrow_shx_inverter_sh20t_battery_power
          - sensor.sungrow_shx_inverter_sh20t_battery_level
      - type: entities
        title: Today (kWh)
        entities:
          - sensor.sungrow_shx_inverter_sh20t_daily_pv_generation
  - title: Details
    cards:
      - type: entities
        title: Strings
        entities:
          - sensor.sungrow_shx_inverter_sh20t_mppt1_voltage
          - sensor.sungrow_shx_inverter_sh20t_mppt1_current
          - sensor.sungrow_shx_inverter_sh20t_inverter_temperature
          - sensor.sungrow_shx_inverter_sh20t_running_state_raw
  - title: EMS control
    cards:
      - type: entities
        title: Mode and limits (writes on change)
        entities:
          - select.sungrow_shx_inverter_sh20t_operating_preset
          - select.sungrow_shx_inverter_sh20t_ems_mode
          - number.sungrow_shx_inverter_sh20t_battery_min_soc
          - number.sungrow_shx_inverter_sh20t_battery_max_soc
          - number.sungrow_shx_inverter_sh20t_export_power_limit
```

## 3. Notes

**Battery-less installations.** Battery-dependent entities may simply be
unavailable without a battery; that is expected, not a failed connection. Leave
the Energy Dashboard **Battery** fields empty rather than pointing them at an
unavailable sensor.

**Multiple inverters.** Add one config entry per physical serial number; each
becomes its own device with its own `sun..._<model>_` prefix. Two inverters of
the **same** model share a prefix, so Home Assistant appends a suffix
(`..._sh20t_2_...`) to keep IDs unique — confirm the actual IDs rather than
assuming. Aggregate only non-overlapping energy flows so grid or load energy is
not counted twice.

**Daily vs total energy sensors.** Both exist for most flows:

- `Daily ...` sensors (e.g. `Daily PV generation`, `Daily imported energy`) use
  state class `total_increasing` and reset with the inverter's day boundary.
- `... Total ...` sensors (e.g. `Total PV generation`, `Total imported energy`)
  use state class `total` and are lifetime counters.

Use the **total** counters for the Energy Dashboard and lifetime statistics, and
the **daily** sensors for a "today" view. A retained value after a failed poll
is not a fresh measurement, and a daily counter reset is not a new measurement
(see USER_GUIDE.md).

## 4. Attribution

The dashboard concept — the Overview / Details / EMS control tabs and the Energy
Dashboard field mapping — comes from **mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant**,
MIT licensed, Copyright (c) 2025 Martin Kaiser and contributors:
<https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant>.

That project's `doc/dashboard.md` and its `images/*.drawio.svg` screenshots are
the originals. This document links to them rather than copying them, because
this repository does not redistribute the upstream assets. Refer to the upstream
repository for the reference screenshots.