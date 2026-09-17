# Changelog

## 0.0.7 — community testing build

- **Brand art is icon-only.** The large "SUNGROW" wordmark tile and its dark variant are
  gone; the square emblem icon now represents the integration everywhere. This is the
  arrangement the brands repository recommends when a brand uses one image for both its
  icon and its logo — the icon is served as the logo fallback.
- **README header image no longer disappears.** It used a repository-relative path, which
  renders on GitHub but breaks everywhere the README is rendered from fetched Markdown
  (including HACS); it now uses an absolute URL.
- **README badge row** added: HACS custom repository, latest release, license, commit
  activity, last commit and open issues.
- No functional change — entities, controls and diagnostics behave exactly as in 0.0.6.

## 0.0.6 — community testing build

- **Diagnostics are usable again on this inverter.** The raw register dump
  aborted on the first block the device declined, so the export came back with an
  empty snapshot. It now keeps every readable register and separately names the
  blocks the inverter refused.
- **Unsupported blocks are detected instead of assumed.** When a unit answers a
  register block with an illegal-data-address exception — a block that model does
  not implement, such as the legacy version strings on an SH20T — the block is
  treated as absent: it is dropped from polling, recorded once in the log, and its
  entities are never created. Previously the block failed on every poll cycle
  forever and its entities sat permanently unavailable. This also stops the
  integration from guessing support from the model code alone.
- **Removed: the six meter phase V×I sensors** (input 5740–5745) and the register
  block behind them. The maintainer's SH20T declines that block while every
  neighbouring meter register answers, so the sensors could never report. Meter
  and per-phase *power* (5600/5602/5604/5606) are unaffected.

## 0.0.5 — community testing build

- Brand assets: the icon now has a transparent background (the white was keyed
  out, keeping the anti-aliased edges), and the integration ships `dark_icon` and
  `dark_logo` variants for dark mode. Light mode keeps the orange-tile logo; dark
  mode shows a white wordmark on transparency.

## 0.0.4 — community testing build

- Brand assets: the integration now ships its own icons and logos
  (`brand/icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png`), replacing the
  placeholder artwork. Home Assistant and HACS show these from the installed
  version, so they arrive with this release.
- README displays the logo.
- `scripts/setup` probes for a Python 3.14.2+ interpreter instead of assuming the
  `python3` on `PATH` qualifies, so the documented test environment can be
  recreated on machines where `python3` is older (for example Python 3.13 with
  `python3.14` installed alongside).
- NOTICE records the artwork provenance.

## 0.0.3 — community testing build

Documentation release on top of 0.0.2, plus the regression test for the
translation defect found during publication.

- README: new **Tested configuration** section recording the maintainer's
  installation — the only setup this build has been tested on — and an explicit
  request for other owners to test and raise issues or pull requests.
- README: new **Connection overview** section.
- New `docs/DASHBOARD.md`: Energy Dashboard field mapping and optional Lovelace
  layouts, migrated from the upstream YAML package, with model-specific entity IDs
  and instructions to confirm your own.
- User guide: upstream scene → built-in preset migration table.
- Tests: added a regression test asserting the `strings.json` exception shape and
  that `translations/en.json` stays byte-identical to it.
- README: documented AI-assisted development.

## 0.0.2 — community testing build

- First public testing release.
- Six platforms: 120 sensor descriptions, seven binary sensors, nine numbers,
  three switches, three register-backed selects plus the composed **Operating
  preset** selector, and two opt-in command buttons.
- 40 recognised model codes with model-aware entity filtering.
- Shared built-in Modbus transport; bounded, confirmed settings writes.
- Redacted diagnostics, reconfiguration, options and outage-aware energy caching.
- Fixed: config-flow schema serialization (the `Config flow could not be loaded`
  500 caused by a non-serializable validator in `data_schema`).
- Fixed: CPython syntax gate, so the Python 3.14-only `except A, B:` form cannot
  ship again.
- Fixed: `exceptions.no_preset_target` was a bare string, so the `set_preset`
  service error could not be translated into a message and hassfest validation
  failed on it.
