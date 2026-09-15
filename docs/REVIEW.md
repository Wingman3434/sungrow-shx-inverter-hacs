# Thorough review — Sungrow SHx Inverter

Reviewed 2026-09-14 against all **24 distinct requested development pages** (the
test-layout link was supplied twice), plus the upstream repository and its seven
linked context pages. Each source and its disposition is listed below; snapshot
hashes are in REVIEW_SOURCES.json. Research snapshots remain in the local review
workspace and are not copied into the standalone device library.

## Resolved findings

| Area | Finding and resolution |
| --- | --- |
| Naming | Display name **Sungrow SHx Inverter**. Domain/import `sungrow_shx_inverter`; PyPI distribution `sungrow-shx-inverter`; three clearly suffixed delivery folders. Updated manifests, imports, links, scripts, fixtures, lock and metadata. |
| Rename compatibility | Previous experimental `sungrow` entries do not migrate just by renaming a directory. Explicit backup/re-add/migration/rollback instructions supplied; no storage edits or live migration attempted. |
| Upstream context | Expanded descriptions: PV, load, grid, battery-optional storage, backup, EMS, Energy Dashboard, multi-inverter, LAN/WiNet-S and model/firmware restrictions. iHomeManager and other distinct products excluded. |
| Core PR size | Initial overlay now a sensor-only 15-entity contribution, polling only nine needed components. Full six-platform code and tests preserved under follow-up/ and in HACS. |
| Configuration | Battery cap moved out of connection data into an options flow with automatic reload and removal support. Connection settings remain reconfiguration data in the full build. |
| Message spacing | UI can represent 0.005 seconds (5 ms); guide clearly distinguishes milliseconds from seconds. Conservative 0.1-second default retained. |
| Stale values | Cached energy is retained/restored internally, but no longer presented as available during an outage. Recovery avoids zero insertion. |
| Apparent power | Signed phase current now produces `abs(V × I)` in VA, rather than negative apparent-power magnitude. Wire values remain unchanged. |
| Test layout | Separate setup, flow, sensor, control and diagnostic test modules. Added options/clearing, shared-link/multi-unit lifecycle, 5 ms gap, conflict and signed-power tests. |
| Library distribution | PEP 639-capable Hatchling minimum, Apache-2.0 AND MIT metadata and Python/OS classifiers. Wheel/sdist and README metadata checked. |
| Release workflow | Strict version-tag validation replaces arbitrary sed substitution. Release reruns checks; CI tests Python 3.12/3.13/3.14 and builds distributions. All nine unique pinned Action references were resolved publicly. |
| Current dependency | Clean-wheel installation revealed released 4.12.x timing APIs; source/pin rechecked and version-specific documentation corrected. |
| Brand provenance | Existing images retain their original `custom_integrations/sungrow` source. New-domain Core entry is a prepared addition, not a move/deletion or an already-published brand. |
| Readiness evidence | Removed claims that unpublished dependency/brand prerequisites are completed. They remain todo in the Core quality file, intentionally blocking all-green submission status. |
| HACS scope | Only the device library is vendored. Built-in Modbus owns its dependency and socket lifecycle. HACS custom-repository route documented; default-catalogue acceptance is not promised. |

## Retained architecture and deliberate omissions

- 99 active register sensors and all 40 source model codes remain mapped in
  29 typed components. No YAML is interpreted at runtime.
- The complete build retains 120 sensor descriptions and all source-derived
  immediate binary flags, nine numbers, three switches, three selects and two
  explicit opt-in start/stop buttons. Optional UI helpers remain opt-in artifacts.
- Input and holding 12999 remain separate: status reads cannot issue commands.
  Source-disabled low-SoC startup remains excluded.
- A battery is optional; meter and firmware-dependent fields can be unavailable.
  No claim of universal model/firmware support is made from model-code presence.
- Authentication/OAuth, discovery and a system-health endpoint are not invented
  for this local fixed-map device. Diagnostics remain in the full build only.
- Library scaling follows the source's engineering units. Optional derived
  computations never replace native register attributes.
- Timing support is version-specific: stable Home Assistant's 4.10.0 cannot
  reproduce the old 30-second timeout/15-second connect delay, while 4.12.x has
  public per-unit requirements that the library automatically uses. Current
  Core dev's 4.12.0 pin was checked; the installed wheel was tested on 4.12.1.
  No private API patch or custom transport version override was introduced.
- No inverter, live Home Assistant instance, account, repository or release was
  changed. The original delivery ZIP remains intact.

## Open publication/hardware prerequisites

1. Test supported models/interfaces on real hardware, including midnight,
   reconnect, batteryless operation and carefully selected write/readback cases.
2. Publish the renamed Python package and its public source/issue tracker.
3. Register the new Core brand domain and submit companion documentation.
4. Review every AI-assisted change personally, update against current Core dev,
   run hosted checks and follow the required upstream PR templates/review process.
5. Publish a full HACS GitHub release before inviting installation by repository.
   This Core-testing build is not eligible for default-catalogue inclusion.

These are not failed local implementations or claimed completed work. The Core
Bronze quality validator deliberately exposes the two unpublished prerequisites.
Detailed command results and scope limits are in VALIDATION.md.

## Source-by-source disposition

| Requested guidance | Review outcome |
| --- | --- |
| [First integration](https://developers.home-assistant.io/docs/creating_component_index) | Native integration domain, config entry and correct custom/Core version distinction. |
| [Contributing to Core](https://developers.home-assistant.io/docs/core/integration/contributing_to_core) | Fixed: top-level overlay now one platform/15 sensors; complete work retained in follow-up, not one large PR. |
| [Integration file structure](https://developers.home-assistant.io/docs/creating_integration_file_structure/) | Renamed domain paths, manifests, tests/imports, shared modules and custom brand assets. |
| [Integration test file structure](https://developers.home-assistant.io/docs/creating_integration_tests_file_structure/) | Split tests into test_init, test_config_flow, test_sensor, test_controls and test_diagnostics as applicable. |
| [Integration manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/) | Product name, valid domain, device/local_polling, Modbus dependency, exact library pin; custom-only version/issues. |
| [Config flow](https://developers.home-assistant.io/docs/core/integration/config_flow/) | Serial uniqueness and test-before-configure; millisecond gap; user input/reconfigure tested. Reconfigure only in full build. |
| [Options flow](https://developers.home-assistant.io/docs/core/integration/options_flow/) | Fixed: optional installation battery cap uses ConfigEntry.options and OptionsFlowWithReload; can be cleared. |
| [YAML configuration](https://developers.home-assistant.io/docs/core/integration/yaml_configuration/) | UI setup only. Original YAML is immutable reference; optional helpers are not integration YAML configuration. |
| [Diagnostics](https://developers.home-assistant.io/docs/core/integration/diagnostics/) | Full build only. Host/serial omitted, raw identity words removed, exception messages not exported; tests retained. |
| [System health](https://developers.home-assistant.io/docs/core/integration/system_health/) | Reviewed, not added: no cloud endpoint/quota; coordinator, logs and diagnostics already describe local health. |
| [Development checklist](https://developers.home-assistant.io/docs/development_checklist/) | Pinned public dependency prerequisite, source distribution, issue tracker, generated metadata instructions, Ruff/typing. |
| [Component review checklist](https://developers.home-assistant.io/docs/creating_component_code_review/) | No direct protocol implementation in Core. Current UI/runtime_data guidance takes precedence over older YAML examples. |
| [Platform review checklist](https://developers.home-assistant.io/docs/creating_platform_code_review/) | CoordinatorEntity lifecycle; no I/O in entity properties; cached reads, unique IDs, platform parallelism. |
| [Modbus introduction](https://developers.home-assistant.io/docs/modbus/introduction/) | Rechecked async_get_unit/temporary_unit and connection ownership; real shared-transport multi-unit test added. |
| [Integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) | Bronze is a target, not an award. Library-publication and new-brand prerequisites remain todo. |
| [Quality-scale checklist](https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist) | Every Bronze rule has implementation evidence or exemption; no unsupported claim that public steps are done. |
| [PR review process](https://developers.home-assistant.io/docs/review-process/) | Initial small PR plus sequenced future work, current dev/human review requirements; no PR opened. |
| [Library introduction](https://developers.home-assistant.io/docs/api_lib_index) | Standalone async typed library with OSI metadata, public issue/release preparation, editable development. |
| [Library authentication](https://developers.home-assistant.io/docs/api_lib_auth) | Local Modbus has no authentication/OAuth. Caller injects the unit; no irrelevant HTTP auth/state storage added. |
| [Library data models](https://developers.home-assistant.io/docs/api_lib_data_models) | Native register fields retained; engineering scaling is wire decoding. Optional arithmetic stays separately exposed. |
| [Packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) | Hatchling minimum, SPDX licence expression, classifiers, lock, wheel/sdist build and Twine metadata validation. |
| [HACS publishing start](https://www.hacs.xyz/docs/publish/start/) | README, prepared repo description/topics/issues, hacs.json and full-release instructions. |
| [HACS default inclusion](https://www.hacs.xyz/docs/publish/include/) | Explicitly documented Core-testing/override exclusion; custom-repository distribution remains the supported route. |
| [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/) | One custom_components domain, self-contained vendor tree, version/issue metadata, icon and validator workflows. |
| [Sungrow upstream repository](https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/tree/main) | README plus installation, usage, FAQ, dashboards, migration and changelog read. Main YAML unchanged from supplied source. |

Original/live YAML SHA-256: `4c1580bb02cd2e6213ea5f600b0b593231841e4991b066ba08476554f50ea0b6`.
