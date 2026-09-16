# Validation record — 0.0.2 delivery (2026-09-14)

> **Point-in-time record.** This documents the local checks run for the 0.0.2
delivery. Test counts and coverage figures below reflect that revision and have
since changed; the CI runs on `main` are the current result. The hosted checks and
publication items listed as outstanding at the end were completed on 2026-09-16.

## Completed local checks

| Check | Result |
| --- | --- |
| Complete supplied YAML vs upstream main | Exact byte match, 90,066 bytes; 99 active register sensors / 40 model codes |
| Library — Python 3.12.14, Modbus 4.11.1 | 188 passed |
| Library — Python 3.13.5, Modbus 4.11.1 | 188 passed |
| Library — Python 3.14.5, Modbus 4.10.0 | 188 passed |
| Installed wheel — Python 3.12.14, Modbus 4.12.1 | 188 passed; imported in a clean environment |
| Initial sensor-only Core | 14 passed; 99% statement coverage; 100% config-flow coverage |
| Complete Core follow-up | 25 passed; 99% statement coverage; 100% config-flow coverage |
| Complete Core with current dev's 4.12.0 dependency | 25 passed on the local Core runtime snapshot |
| Stable HACS — Home Assistant 2026.9.2 / Modbus 4.10.0 | 25 passed; 99% adapter coverage excluding vendor |
| Strict library mypy | Passed, 38 files |
| Strict initial/full Core mypy | Passed, 6 / 12 files, using --follow-imports=silent |
| Ruff lint/format | Library: passed. HACS/initial Core/full Core: `ruff check` passed; `ruff format --check` fails on the corrected `except (ModbusError, HomeAssistantError):` because the pinned Ruff formatter (0.16.5-0.16.7) emits invalid Python 2 syntax at target py314/py315. See "Lint gate defect" below. |
| Initial Core hassfest | All validators except two explicit quality-scale publication prerequisites passed |
| Custom hassfest | Passed; local overlay causes an expected same-domain warning |
| Wheel and source distribution | Built; Twine metadata checks passed; SPDX Apache-2.0 AND MIT |
| Vendored library | Exact source and licence hashes checked |
| Pinned Actions | All nine distinct upstream commit references resolved successfully |
| Delivery | Three clean folders, no environments/caches, source parity and archive hashes checked |

Core tests use the previously obtained Home Assistant 2026.10.0.dev0 source
snapshot. Current dev's Modbus pin was separately fetched and the adapter tested
with 4.12.0. The current connection.py delta only canonicalizes RTU/ASCII-over-TCP
links; this integration requests normal Modbus TCP. This is not a claim to have
tested the entire newest Core repository or its other integrations.

The baseline Core suites used Modbus 4.11.1. The custom suite runs in a separate
2026.9.2 environment with no standalone Sungrow package installed and imports
its private vendor tree. Shared-connection tests use the real Home Assistant
connection owner with only its underlying connection replaced by the official
Modbus mock. No physical network request is made to an inverter.

Coverage excludes private vendored code from the HACS adapter metric; the
library has its own 188-test suite. Coverage is a statement metric, not proof
that all hardware states or regressions have been tested.

## Two intentional Core readiness blockers

The quality file keeps `brands` and `dependency-transparency` as `todo`:
the new brand domain and renamed public library/issue tracker are prepared
locally but not published. Accordingly **Core hassfest is not wholly green**.
Its exact quality-scale errors are recorded with the Core delivery's own notes.
Do not change these to done until those publication prerequisites really exist.

HACS hassfest sees the temporary Core overlay and warns of the shared domain.
The stable runtime test installation has no built-in Sungrow SHx Inverter domain.
The intended Core and custom implementations must not run alongside each other.

## Lint gate defect (2026-09-15)

The delivered trees shipped `except ModbusError, HomeAssistantError:` (missing
parentheses) in all three `config_flow.py` copies. Reproduced against the actual
artifacts with the pinned toolchain:

- CPython 3.12/3.13 reject it: `SyntaxError: multiple exception types must be
  parenthesized`. The integration's own 3.14 interpreter accepts it, and Ruff's
  parser accepts it too (`ruff check .` prints "All checks passed!" at
  `target-version = "py314"`), so the old gate could not catch it.
- The pinned Ruff formatter actively prefers it: at py314 `ruff format` rewrites
  the corrected `except (A, B):` back to `except A, B:`. Running `ruff format`
  is what produced the shipped syntax error. Ruff's py314 target cannot simply be
  lowered, because the integration uses PEP 695 `type` aliases that Ruff does not
  resolve below py314.

Fixes applied: `scripts/check_syntax.py` parses every shipped module with
`ast.parse(..., feature_version=(3, 12))`, which rejects 3.14-only syntax such as
the unparenthesized clause regardless of the running interpreter, and now runs
first in `scripts/lint`, `.github/workflows/lint.yml` and the library `ci.yml`
(the library copy lives at `script/check_syntax.py`). The three corrected
`config_flow.py` lines keep the portable parentheses with an explicit
`# fmt: skip` so the py314 formatter cannot rewrite them. The original "Passed for
… HACS" claim above was not reproducible and has been corrected.

## Config-flow frontend serialization defect (2026-09-15)

Field testing surfaced a hard failure on "Add integration": Home Assistant returned
`Config flow could not be loaded: 500 Internal Server Error` and logged
`ValueError: unable to serialize schema: <method 'strip' of 'str' objects>`.

Cause: `STEP_SCHEMA` used the bare `str.strip` method as a validator
(`vol.All(TextSelector(), str.strip, vol.Length(min=1))`). Home Assistant
serializes `data_schema` through probatio's `to_field_list` before sending it to
the frontend, and a bare callable cannot be serialized. The unit suite missed it
because it only inspected the schema object, never the serialized form.

Fix (all three `config_flow.py` copies): the schema keeps a serializable
`vol.All(TextSelector(), vol.Length(min=1))`, and the host string is stripped in
`_async_form` / `async_step_user` before probing. A regression test
(`test_form_schema_serializes_for_frontend`) now serializes the real form result
with `to_field_list`, which fails on the old schema.

## Battery setpoint step defect (2026-09-15)

Field testing showed `Battery forced charge discharge power` rejecting the valid
value 6750 W with "the two nearest valid values are 6700 and 6800". Register
13051 is a plain `uint16` in watts (source map: no `scale`), so it has 1 W
resolution; the entity wrongly declared `native_step = 100` (copied from the
upstream YAML's slider step). Fixed to `native_step = 1` in the HACS and Core
follow-up `number.py`, with a regression test that writes 6750 and reads back
register 13051.

The two sibling setpoints, `battery_max_charge_power` (33046) and
`battery_max_discharge_power` (33047), keep `native_step = 10`: the source map
gives them `scale: 10`, so the register cannot hold values that are not
multiples of 10 W. Only the forced charge/discharge setpoint is 1 W capable.

## Built-in operating presets

Users previously had to run `scripts/generate_helpers.py` to get mode presets.
That does not scale to a HACS install, and research established that Home
Assistant exposes no supported way for an integration to
create `input_boolean`/`input_number` helpers (those domains ship no config
flow), so a "setup helpers" button was not viable.

The presets are now part of the integration itself: a non-register-backed
`select` entity `operating_preset` plus the `sungrow_shx_inverter.set_preset`
service. Both apply the same register sequence as the source scenes
(`presets.py`), reading `device.battery_max_power` and
`export_bounds.export_power_limit_max` instead of a secret. They are only
available where the preset's fields exist, write through the same
bounded/confirmed `device.async_write` path as every other control, refresh the
cohorts they touched, and never run at setup or poll time. Seven presets are
covered by `tests/test_preset.py`, including a missing-export-bounds failure.

## Maximum-preset cap fix

Field testing of the operating presets showed
`self_consumption_max_battery_discharge` failing with "The inverter did not
confirm the write" on a real SH10RT, while the fixed-value
`self_consumption_no_battery_discharge` (10 W) succeeded. The preset writes the
live `battery_max_power` to register 33047; real inverters can cap that register
below the requested rating, so the strict read-back equality rejected a write
that had actually taken effect.

Fix: `PresetStep.is_maximum` marks the two "use the maximum" steps. Such a step
may settle on the inverter's own lower cap, and is accepted when the write
demonstrably changed the value; an explicit value is still confirmed exactly, so
`self_consumption_no_battery_discharge` and every fixed write keep the strict
guarantee. Covered by `test_maximum_step_accepts_the_inverter_cap` and
`test_explicit_value_still_requires_confirmation` in both trees.

## Maximum-step fallback and diagnostics (0.0.2)

0.0.1 tolerated a maximum step that the inverter *capped* (value changed), but
field testing still failed: the inverter kept its previous value, so the write
had been refused outright. `battery_max_power` is only bounded by the reported
BDC rating and the configured cap; it ignores the inverter's own rated output
(register 5000), so the requested maximum can exceed what registers 33046/33047
accept.

0.0.2 adds, for the two "use the maximum" steps only: one retry at the
device-derived ceiling (`inverter_rated_output`, when lower), then a WARNING
naming the requested value, the value the device kept, `bdc_rated_power`,
`inverter_rated_output`, `battery_max_power` and the fallback, before failing.
Explicit values are unchanged and still require exact confirmation. Covered by
`test_maximum_step_falls_back_to_inverter_rating` and
`test_maximum_step_reports_when_nothing_is_accepted` in both trees.

## Not completed or claimed

- No hardware tests, live installation, inverter reads/writes or configuration
  migrations. Midnight/reconnect/firmware/interface behaviour requires field testing.
- No GitHub repository, issue, PR, release, PyPI upload, brand registration or
  HACS catalogue submission.
- Hosted Actions, HACS repository checks, a documentation-site build, and the
  whole-repository Core pre-commit/test suite have not run.
- Strict mypy is scoped to the new integration with imported modules silenced.
  A broader run encountered existing unrelated frontend/matter/stream/tts typing
  issues; these were not changed as part of this integration review.
- Core Bronze is a target, not an awarded tier or acceptance.
- Source library version 0.0.0 is a development placeholder replaced at release.
  The intended first library release is 0.1.0; custom build is 0.0.2.
- The full feature set is follow-up/community implementation material, not a
  single first Core PR. HACS default-catalogue policy excludes Core-testing builds.
