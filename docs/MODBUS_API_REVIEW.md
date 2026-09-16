# Modbus design and version review

Read on 2026-09-13:

- https://developers.home-assistant.io/docs/modbus/introduction/
- https://home-assistant-libs.github.io/modbus-connection/
- modbus-connection source: model/fields.py, component.py, component_group.py,
  _writing.py, _protocol.py, mock.py, cli_helper.py; connection and modelling docs.
- https://github.com/darkrain-nl/sofar-modbus — typed component files, device
  assembly, model filtering, UpdateReport, all workflows, Renovate, query helper,
  pyproject, README and release guide.
- https://github.com/home-assistant/core/tree/dev/homeassistant/components/sofar
  and its tests, plus the shared modbus connection implementation.
- https://github.com/ludeeus/integration_blueprint — all repository tooling,
  manifests, development environment, issue templates and HACS validation.

## Architecture

The device library accepts only a ModbusUnit. It does not open/close sockets,
depend on an application framework or start polling tasks. Each subsystem is a
statically declared Component. Adjacent declared words are pooled automatically;
unrelated or optional blocks are isolated rather than put in one all-or-nothing
ComponentGroup. The source has no repeated dynamically sized banks.

Home Assistant obtains a held unit with modbus.async_get_unit and probes with
modbus.async_get_temporary_unit. It never constructs a transport, stores private
Modbus client objects, reloads on an ordinary connection drop or closes shared
connections. Modbus releases the connection when the last consumer unloads.

One coordinator schedules 5/10/60/600-second cohorts. A component's due time is
measured after completion so slow gateways do not trigger catch-up storms.
Freshness persists for non-due groups and is cleared on full connection failure.
Standard Home Assistant request-refresh debouncing remains in effect; direct
writes themselves are read back and verified by the library.

## Field support checked against source

| Model field family | Relevant options |
| --- | --- |
| integer/gauge | signed, scale, offset, raw nan, stride, unit, writable validator |
| uint32/int32/uint64/int64 | count implied by width, big/little word_order, scale/offset |
| float32/float64 | IEEE-754, scaling, word order; NaN yields None |
| string | register count; fixed-length null-padded ASCII |
| enum/flags | IntEnum/IntFlag conversion; unknown enum becomes None, unknown flag bits retained |
| boolean | 0/1 only; unsuitable for Sungrow 0xAA/0x55 controls |
| bit/bits | packed register fields; bits can use read-modify-write |
| coil/discrete_input | separate address spaces; not holding-register switches |
| raw_register | raw words, no signed/scaling/sentinel interpretation |
| RegisterField/NumberField | custom converters, count and scale-register support |
| Writable fields | inverse encode, validator, optional force_fc16; FC06 by default |
| Placement/repeating_group | indexed/offset/static or register-count repetitions |
| Component | register_space, max_gap/max_span, declared/resolved fields, restrict_fields, listeners |
| ComponentGroup | pooled reads across compatible components with common limits |
| SunSpec | discovery and specialised sentinel/SF models; not applicable to this fixed map |

The attachment needs signed/unsigned 16/32-bit numbers, gauges, ASCII strings,
raw sentinels and writable validators. It does not need float16, custom struct,
byte swaps, coils, SunSpec, scale-register indirection or dynamic repeating
groups. Decimal presentation belongs to sensor descriptions, not the wire codec.

## Version-specific timing — updated 2026-09-14

Home Assistant 2026.9.2 pins modbus-connection 4.10.0. The original local Core
snapshot pins 4.11.1. Both have shared units and message spacing, but neither has
`require_timeout` or `require_connect_delay`. In the stable Home Assistant
shared manager this means a 10-second timeout and no initial connect delay;
the source YAML's timeout=30/delay=15 cannot be matched on that version.

The final clean-wheel install resolved **modbus-connection 4.12.1**, whose public
unit interface now includes both timing methods. Current Core dev at commit
`74639e3063769b42411e2c0eff48a773bbde3db6` pins **4.12.0**. Its shared connection
entry points were compared with the local snapshot. The library already
capability-detects the public methods and requests timeout=30/connect-delay=15.
Thus this limitation applies to older dependencies, not all current libraries.

The HACS manifest does not override the transport pin: the built-in Modbus
integration owns it. Do not manually change dependencies in a running installation.
The standalone package permits compatible 4.x releases and was additionally
tested using the installed wheel against 4.12.1. Full Core adapter tests also
cover the current 4.12.0 dependency on the local Core runtime snapshot; that is
not a claim of running the complete latest Core repository test suite.

The Core manifest pins sungrow-shx-inverter 0.1.0 as the intended first release.
Publish that library before a Core PR can install it normally.

## No hardware validation claimed

Tests exercise the real library against the Modbus mock and the real Core and
stable Home Assistant runtimes. Real inverter/firmware compatibility, gateway
timing, HACS catalog registration, hosted Actions and PyPI publishing remain
external checks. Nothing in this task connects to or modifies a live inverter.

Re-reviewed 2026-09-14: the new domain is sungrow_shx_inverter; the Core and HACS
builds poll all cohorts their platforms use. Energy caching does not imply
availability.
