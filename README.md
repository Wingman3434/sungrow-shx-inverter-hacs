# Sungrow SHx Inverter

Local Modbus monitoring and EMS controls for Sungrow residential hybrid
inverters: solar PV, household load, grid import/export, optional battery
storage, backup, operating state and firmware. Based on
[Martin Kaiser and contributors' Sungrow register map](https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/tree/main).
Includes model-aware entities and optional helpers for the source's energy
dashboard and EMS preset use cases; it does not install the upstream dashboards.

**Community testing build 0.0.2. Requires Home Assistant 2026.9.2+.**
No physical inverter validation or publication is claimed.

> **Agent context:** `../CONTEXT_PACK.md` at the delivery repository root gives the
> project overview, architecture, data models and workflows for onboarding a new
> session. It sits outside this folder and is not shipped with it.

## Install (HACS, custom repository)

1. HACS → ⋮ (top right) → **Custom repositories**
2. Repository: `https://github.com/Wingman3434/sungrow-shx-inverter-hacs`
   Type: **Integration** → **Add**
3. Search HACS for **Sungrow SHx Inverter** → **Download** → pick `0.0.2`
4. Restart Home Assistant
5. Settings → Devices & services → **Add integration** → *Sungrow SHx Inverter*

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Wingman3434&repository=sungrow-shx-inverter-hacs&category=integration)

**Version 0.0.2 is a community testing build.** It has not been validated on
physical hardware. Read the limitations below before installing.

Add the integration through Settings → Devices & services. Enter host, port,
unit ID and message gap in seconds. Set any optional battery power cap through
**Options** afterwards. Disable old Sungrow polling before enabling this build.

**If you installed the old `sungrow` test bundle, the renamed domain requires a
new entry; it is not an automatic upgrade.** Follow the migration/rollback
section in [the user guide](docs/USER_GUIDE.md).

## Testing build limitations

- No physical-inverter validation. Register semantics come from the source YAML
  map and the manufacturer's documented register list.
- One register-scale ambiguity is unresolved: registers `33046`/`33047` are marked
  `scale: 10` in the source map, while that file's own comment cites a 0.01 kW
  datasheet unit (`scale: 100`). If you can check your inverter, please report it.
- iHomeManager, Logger1000, wallboxes and the iSolarCloud cloud API are not supported.
- Requires Home Assistant 2026.9.2+ and HACS 2.0.0+.

## Reporting issues

Open an issue at <https://github.com/Wingman3434/sungrow-shx-inverter-hacs/issues>
and include:

1. Inverter model code and firmware, and whether you use the LAN port or WiNet-S.
2. The integration's **diagnostics dump** (Settings → Devices & services → the
   integration → ⋮ → Download diagnostics).
3. Debug logs covering Home Assistant startup to the failure:
   ```yaml
   logger:
     logs:
       custom_components.sungrow_shx_inverter: debug
   ```
4. Exactly which entities or controls are wrong, and the register value expected.

## What is included

- Full six-platform implementation: 120 sensor descriptions, seven binary flags,
  nine numbers, three switches, three register-backed selects, a composed
  **Operating preset** selector and two opt-in command buttons.
- One-tap mode presets built in: self-consumption (max/no battery discharge),
  zero/max export, battery bypass and forced charge/discharge, applied as the
  source scenes were and reading the inverter's live limits. No generated
  helpers or user scripts required.
- 40 recognised model codes; model-specific filtering, not hardware certification.
- Shared built-in Modbus transport, bounded/confirmed settings writes and
  serial-based duplicate prevention.
- Redacted diagnostics, reconfiguration, options and outage-aware energy caching.
- Private typed library under `_vendor/sungrow_shx_inverter`; no separately
  installed Sungrow PyPI package. The `modbus_connection` **Python package** is a
  hard dependency (`config_flow.py`, `coordinator.py`, `entity.py` import
  `ModbusError`/`ModbusTcpParams`), but it is supplied by Home Assistant's
  built-in `modbus` integration (declared as `dependencies: ["modbus"]`), so you
  do not install it separately or as a second custom integration.

Batteryless installations work with battery-dependent data unavailable as
appropriate. Internal LAN is preferred; WiNet-S may expose fewer/slower readings.
iHomeManager, wallboxes and Logger1000 are not supported.

[Installation, Energy Dashboard, controls and troubleshooting](docs/USER_GUIDE.md) ·
[Source coverage](docs/SOURCE_COVERAGE.md) ·
[Optional helpers](docs/OPTIONAL_HELPERS.md) ·
[Review findings](docs/REVIEW.md) · [Validation](docs/VALIDATION.md)

## Development and publication

Run `scripts/setup`, `.venv/bin/pytest`, and `scripts/lint`.
`scripts/develop` starts a disposable configuration, not your live installation.
Refresh the private library with:

```sh
python scripts/vendor.py --source ../sungrow-shx-inverter-library
python scripts/vendor.py --check
```

Workflows retain the integration_blueprint lint, hassfest and HACS validation
pattern, with runtime tests and vendor hash verification. Local brand assets
are included. The built-in Modbus dependency owns its transport package version.

Publish the repository contents, including hidden files, not the outer
three-folder archive. Apply the description/topics from repository-settings.json,
enable issues, run hosted checks, then create a full GitHub release matching the
manifest version. A repository's existence, hosted checks and release are
unverified until publication.

**HACS default catalogue:** custom integrations used to alpha/beta-test Core
integrations or override Core integrations are not accepted as defaults.
Use the custom-repository route for this project. Core acceptance is a separate
process; no catalogue listing is promised.

## Versioning

Deliveries use `Major.Minor.Fix`, starting at `0.0.1`. The folder name carries the
version (`sungrow-shx-inverter-hacs-0.0.2`) and the integration manifest
`version` matches it, so this build is `0.0.2`. The Core delivery ships the
**same version and the same patch set**. The PyPI library is versioned
independently by its own release tag, so the manifest pin
(`sungrow-shx-inverter==0.1.0`) does not follow this scheme.

## AI-assisted development

This integration has been built with AI assistance under my direction. I review,
test and take responsibility for everything in this repository, including code
quality. I also manage GitHub issues and pull requests.

## Attribution

Integration Apache-2.0; vendored library Apache-2.0 with MIT register-map portions.
All notices are included. Architecture follows darkrain-nl/sofar-modbus and Core
Sofar; community repository tooling follows ludeeus/integration_blueprint.
Sungrow's marks remain its property; no endorsement is implied.
