# Contributing

Use Python 3.14.2+ and Home Assistant 2026.9.2 or later. Run scripts/setup,
.venv/bin/pytest, and scripts/lint. scripts/develop creates a disposable
local test instance; it does not touch a running installation.

Report your model, firmware, connection type and redacted integration diagnostics.
Do not include credentials, host addresses or inverter serials in public issues.
Provide a minimal reproduction and expected versus observed register values.

Edit the standalone sungrow-shx-inverter library first for protocol changes, run its
tests, then run: python scripts/vendor.py --source ../library
The vendor manifest records hashes; CI rejects drift. Entity/UI changes belong
in the Core submission tree first and are mirrored to this custom integration.
Keep the focused initial Core submission independently scoped.
Do not submit the _vendor directory to Home Assistant core.

This repository follows ludeeus/integration_blueprint's HACS, hassfest, lint,
issue-template, devcontainer and development-script layout. Dummy HTTP API,
credentials and example switches have been replaced with the shared Modbus API.
