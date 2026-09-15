# Upstream context reviewed — 2026-09-14

Primary source:
https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/tree/main

Read the README and linked installation, usage, FAQ, dashboard, migration and
changelog pages. The live main-branch `modbus_sungrow.yaml` is byte-for-byte
identical to the supplied 90,066-byte 2026-06-19 attachment. Original evidence
and its licence remain unchanged in `source/`.

Carried into the description and guide: local PV/grid/load/battery/backup
monitoring; EMS controls and seven presets; battery optional; meter-dependent
fields; internal LAN versus WiNet-S restrictions; model/firmware quirks;
multiple inverters; current Energy Dashboard signs and sensor selections;
migration from older entity IDs; optional dashboard controls.

Not claimed as implemented: iHomeManager (different map), wallboxes,
Logger1000, cloud login, installer commissioning, firmware upgrades, automatic
dashboard installation or automatic migration of old entity IDs/history.
The upstream author's physical SH10RT testing does not certify this build.
No source-project credentials, reboot procedures or proxy setup changes were
copied into this integration.

This is an independent implementation, not an official Sungrow product or a
published release by the upstream YAML maintainers. Preserve Martin Kaiser and
contributors' MIT attribution and direct new implementation bugs to this
project's issue tracker.
