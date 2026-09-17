<p align="center">
  <img src="https://raw.githubusercontent.com/Wingman3434/sungrow-shx-inverter-hacs/main/custom_components/sungrow_shx_inverter/brand/icon.png" alt="Sungrow SHx Inverter" width="128">
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge" alt="HACS custom repository"></a>
  <a href="https://github.com/Wingman3434/sungrow-shx-inverter-hacs/releases"><img src="https://img.shields.io/github/v/release/Wingman3434/sungrow-shx-inverter-hacs?style=for-the-badge" alt="Latest release"></a>
  <a href="https://github.com/Wingman3434/sungrow-shx-inverter-hacs/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Wingman3434/sungrow-shx-inverter-hacs?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/Wingman3434/sungrow-shx-inverter-hacs/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/y/Wingman3434/sungrow-shx-inverter-hacs?style=for-the-badge" alt="Commit activity"></a>
  <a href="https://github.com/Wingman3434/sungrow-shx-inverter-hacs/commits/main"><img src="https://img.shields.io/github/last-commit/Wingman3434/sungrow-shx-inverter-hacs?style=for-the-badge" alt="Last commit"></a>
  <a href="https://github.com/Wingman3434/sungrow-shx-inverter-hacs/issues"><img src="https://img.shields.io/github/issues/Wingman3434/sungrow-shx-inverter-hacs?style=for-the-badge" alt="Open issues"></a>
</p>

# Sungrow SHx Inverter

Local Modbus monitoring and EMS controls for Sungrow residential hybrid
inverters: solar PV, household load, grid import/export, optional battery
storage, backup, operating state and firmware. Based on
[Martin Kaiser and contributors' Sungrow register map](https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/tree/main).
Includes model-aware entities and optional helpers for the source's energy
dashboard and EMS preset use cases; it does not install the upstream dashboards.

**Community testing build. Requires Home Assistant 2026.9.2+.**
Tested only on the maintainer's installation (see [Tested configuration](#tested-configuration)).
Other inverter models are unverified — please test and raise issues or pull requests.

## Install (HACS, custom repository)

1. HACS → ⋮ (top right) → **Custom repositories**
2. Repository: `https://github.com/Wingman3434/sungrow-shx-inverter-hacs`
   Type: **Integration** → **Add**
3. Search HACS for **Sungrow SHx Inverter** → **Download** → pick the latest version
4. Restart Home Assistant
5. Settings → Devices & services → **Add integration** → *Sungrow SHx Inverter*

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Wingman3434&repository=sungrow-shx-inverter-hacs&category=integration)

**This is a community testing build.** It has been exercised only on the
maintainer's SH20T installation; no other hardware has been tested. Read the
limitations below before installing.

Add the integration through Settings → Devices & services. Enter host, port,
unit ID and message gap in seconds. Set any optional battery power cap through
**Options** afterwards. Disable old Sungrow polling before enabling this build.

**If you installed the old `sungrow` test bundle, the renamed domain requires a
new entry; it is not an automatic upgrade.** Follow the migration/rollback
section in [the user guide](docs/USER_GUIDE.md).

## Connection overview

The integration talks to the inverter over **Modbus TCP** on your local network. No
cloud account, installer password or iSolarCloud access is involved.

- **Prefer the inverter's internal LAN port.** Connect it to your network and give
  it a fixed address or a DHCP reservation.
- The **WiNet-S** Ethernet port and Wi-Fi dongle also work, but are generally
  slower, expose fewer registers, and may need a larger message gap.
- You need, per inverter: **host**, **port** (normally `502`), **unit ID**
  (`1`–`247`) and a **message gap** (start at `0.005` s on LAN, higher for
  WiNet-S). All four are entered when you add the integration.
- The Modbus TCP connection is owned by Home Assistant's built-in `modbus`
  integration. This custom integration declares it as a dependency and does not
  install a second copy.
- Use one config entry per inverter serial, and disable any other Sungrow polling
  first so two clients do not contend for the connection.

The upstream project documents the physical side with diagrams — the SHxRT
connections overview and the inverter LAN port figure, in
[mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant](https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant#1-overview).
This repository links to those images rather than redistributing them.

## Testing build limitations

- No physical-inverter validation. Register semantics come from the source YAML
  map and the manufacturer's documented register list.
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

- Full six-platform implementation: 114 sensor descriptions, seven binary flags,
  nine numbers, three switches, three register-backed selects, a composed
  **Operating preset** selector and two opt-in command buttons.
- Register blocks your inverter does not implement are detected and skipped, so an
  unsupported group is never created as permanently unavailable entities.
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

[Installation, controls and troubleshooting](docs/USER_GUIDE.md) ·
[Dashboards and Energy Dashboard](docs/DASHBOARD.md) ·
[Source coverage](docs/SOURCE_COVERAGE.md) ·
[Optional helpers](docs/OPTIONAL_HELPERS.md) ·
[Validation record (0.0.2 delivery)](docs/VALIDATION.md)

## Tested configuration

The maintainer develops and tests against this installation:

| Component | Detail |
| --- | --- |
| PV | 35 × 470 W Jinko Solar Tiger Neo, monocrystalline (JKM470N-48HL4M-DV) |
| Inverter | Sungrow SH20T (AS4777-2 2020), 20 kW, three-phase |
| Battery | Sungrow SBH300, 30 kWh usable, LiFePO4 |

This is the **only** installation this integration has been tested on. It is one
data point, not a compatibility guarantee. The register map covers 40 model codes
with model-aware entity filtering, but models differ in which registers they
expose, and several behaviours — midnight rollover, reconnect handling, firmware
differences — remain unverified.

**Testing and bug reports are wanted.** If you run this on another model, please
open an issue or pull request with:

- your inverter model code and firmware version,
- whether you use the internal LAN port or WiNet-S,
- which entities and controls work, which do not, and the diagnostics dump.

Pull requests that extend model coverage, correct register handling, or improve
these docs are welcome. See [Reporting issues](#reporting-issues) for what to
include.

## Development

Run `scripts/setup`, then `.venv/bin/pytest` and `scripts/lint`. `scripts/develop`
starts a disposable Home Assistant configuration rather than your live
installation. Refresh the vendored library with:

```sh
python scripts/vendor.py --source ../library
python scripts/vendor.py --check
```

CI runs lint, hassfest, HACS validation and the test suite, and rejects drift in
the vendored library hashes.

This integration is **not** in the HACS default catalogue — custom integrations
used to test or override Core integrations are not accepted there. Install it
through the custom-repository route above.

## Versioning

Versions follow `Major.Minor.Fix`. The integration manifest `version` and the
GitHub release tag both identify a build, and the two always match — check the
latest release rather than this file. The standalone library is versioned
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
