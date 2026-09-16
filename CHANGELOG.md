# Changelog

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
