# Revision scope note

The inventory below describes the **full community/follow-up build**. The first
Core submission deliberately exposes only the sensor subset listed in that
folder's README. No original register definitions were dropped from the library.
Energy totals now retain their cached value internally while presenting
unavailable during outages. Phase V×I now uses its magnitude.

# Source-to-integration coverage

The complete attachment was parsed, not its truncated chat preview.
Source: source/modbus_sungrow.yaml (90066 bytes), SHA-256 4c1580bb02cd2e6213ea5f600b0b593231841e4991b066ba08476554f50ea0b6.

| Source item | Count | Destination |
| --- | ---: | --- |
| Active Modbus sensors | 99 | Typed library fields and core sensor descriptions |
| Direct Modbus switches | 3 | Switch entities, 0xAA/0x55 write/readback |
| Arithmetic/status template sensors | 21 | Library derived properties and core sensors |
| Immediate power-flow binary sensors | 7 | Library derived properties and core binary sensors |
| Delayed binary sensors | 7 | Optional generated helper package, 60-second delay_on |
| Template numbers | 9 | Number entities with inverse scaling and validation |
| Template selects | 3 | Select entities with exact vendor words |
| Start/stop buttons | 2 | Buttons, disabled by default, holding register 12999 |
| Dashboard danger-mode switch | 1 | Optional input_boolean plus automatic reset |
| Five-minute moving average | 1 | Optional filter helper |
| Mode scenes | 7 | Optional scripts preserving modes and dynamic power caps |
| Dashboard/preset automations | 3 | Reset automation plus dynamic script actions |

## Deliberate corrections and boundaries

- Reactive power: var/reactive_power, not W/power.
- Phase V×I: VA/apparent_power, not measured active power. The calculations remain unchanged.
- Maximum charge/discharge power: 10 W step, so the source's 10 W minimum and 0.01 kW resolution are representable (source UI step 100 was inconsistent).
- Unknown selects remain unknown; no silent fallback to self-consumption or stop.
- Unsupported fields are excluded by model identity, rather than displayed as zero or 6553.5.
- Derived fields depend on every contributing subsystem's freshness; a failed register never becomes a fabricated zero.
- Raw settings/identity are diagnostic and disabled by default; the corresponding controls are normal config entities.
- Totals retain and restore the last valid value during outages; no unproven firmware high-water heuristic was copied from Sofar.
- Calculated consumed energy inherits the source formulas. Daily counters sampled across a reset may briefly disagree; the optional filter remains a presentation helper, not a replacement billing meter.
- Device detection uses the complete 40-code table in the attachment. Family capabilities are based on its comments and clear single/three-phase model families, not hardware certification.
- The optional mode presets are scripts, not scenes with follow-up automations: scripts can read live maximum limits in the same invocation and avoid unresolved secrets in scenes.
- The legacy danger-mode item had no turn_on/turn_off implementation. An input_boolean is the appropriate working helper; it is dashboard presentation, not a device interlock.
- The legacy source's disabled low-SoC forced startup, old battery registers 13020/13021 and separate battery-slave serial remain disabled.
- Active-limitation/APL words remain readable but not writable because the attachment provides no active control for them.
- New unique IDs are serial-scoped. Existing YAML entity history is not automatically migrated or deleted.

## Register versus command addressing

Input 12999 is the running state; holding 12999 accepts 0xCF start / 0xCE stop.
The read-only identification path sends no commands. Diagnostic exports omit
input addresses 4989–4998, all host settings and exception text.

## Every original register

| Original unique ID | Library attribute | New serial-scoped sensor key |
| --- | --- | --- |
| sg_version_1 | legacy_firmware.version_1 | version_1 |
| sg_version_2 | legacy_firmware.version_2 | version_2 |
| sg_version_3 | legacy_firmware.version_3 | version_3 |
| sg_version_4_battery | legacy_firmware.version_4_sungrow_battery | version_4_sungrow_battery |
| sg_protocol_version | software.protocol_version | protocol_version |
| sg_arm_software | software.arm_software | arm_software |
| sg_dsp_software | software.dsp_software | dsp_software |
| sg_inverter_serial | identity.inverter_serial | inverter_serial |
| sg_dev_code | identity.device_type_code | device_type_code |
| sg_inverter_rated_output | identity.inverter_rated_output | inverter_rated_output |
| sg_daily_pv_gen_battery_discharge | combined_energy.daily_pv_generation_battery_discharge | daily_pv_generation_battery_discharge |
| sg_total_pv_gen_battery_discharge | combined_energy.total_pv_generation_battery_discharge | total_pv_generation_battery_discharge |
| sg_inverter_temperature | inverter_temperature.inverter_temperature | inverter_temperature |
| sg_mppt1_voltage | pv.mppt1_voltage | mppt1_voltage |
| sg_mppt1_current | pv.mppt1_current | mppt1_current |
| sg_mppt2_voltage | pv.mppt2_voltage | mppt2_voltage |
| sg_mppt2_current | pv.mppt2_current | mppt2_current |
| sg_mppt3_voltage | pv.mppt3_voltage | mppt3_voltage |
| sg_mppt3_current | pv.mppt3_current | mppt3_current |
| sg_total_dc_power | pv.total_dc_power | total_dc_power |
| sg_phase_a_voltage | grid.phase_a_voltage | phase_a_voltage |
| sg_phase_b_voltage | grid.phase_b_voltage | phase_b_voltage |
| sg_phase_c_voltage | grid.phase_c_voltage | phase_c_voltage |
| sg_reactive_power | grid.reactive_power | reactive_power |
| sg_power_factor | grid.power_factor | power_factor |
| sg_mppt4_voltage | pv.mppt4_voltage | mppt4_voltage |
| sg_mppt4_current | pv.mppt4_current | mppt4_current |
| sg_battery_power | battery.battery_power | battery_power |
| sg_grid_frequency | grid.grid_frequency | grid_frequency |
| sg_meter_active_power | meter_power.meter_active_power | meter_active_power |
| sg_meter_phase_a_active_power | meter_power.meter_phase_a_active_power | meter_phase_a_active_power |
| sg_meter_phase_b_active_power | meter_power.meter_phase_b_active_power | meter_phase_b_active_power |
| sg_meter_phase_c_active_power | meter_power.meter_phase_c_active_power | meter_phase_c_active_power |
| sg_export_power_limit_min | export_bounds.export_power_limit_min | export_power_limit_min |
| sg_export_power_limit_max | export_bounds.export_power_limit_max | export_power_limit_max |
| sg_bdc_rated_power | battery_info.bdc_rated_power | bdc_rated_power |
| sg_battery_current | battery.battery_current | battery_current |
| sg_bms_max_charging_current | battery_info.bms_max_charging_current | bms_max_charging_current |
| sg_bms_max_discharging_current | battery_info.bms_max_discharging_current | bms_max_discharging_current |
| uid_battery_capacity_high_precision | battery_info.battery_capacity_high_precision | battery_capacity_high_precision |
| sg_backup_phase_a_power | backup.backup_phase_a_power | backup_phase_a_power |
| sg_backup_phase_b_power | backup.backup_phase_b_power | backup_phase_b_power |
| sg_backup_phase_c_power | backup.backup_phase_c_power | backup_phase_c_power |
| sg_total_backup_power | backup.total_backup_power | total_backup_power |
| sg_meter_phase_a_voltage | meter_electrical.meter_phase_a_voltage | meter_phase_a_voltage |
| sg_meter_phase_b_voltage | meter_electrical.meter_phase_b_voltage | meter_phase_b_voltage |
| sg_meter_phase_c_voltage | meter_electrical.meter_phase_c_voltage | meter_phase_c_voltage |
| sg_meter_phase_a_current | meter_electrical.meter_phase_a_current | meter_phase_a_current |
| sg_meter_phase_b_current | meter_electrical.meter_phase_b_current | meter_phase_b_current |
| sg_meter_phase_c_current | meter_electrical.meter_phase_c_current | meter_phase_c_current |
| uid_sg_running_state_raw | state.running_state_raw | running_state_raw |
| uid_power_flow_status | state.power_flow_status | power_flow_status |
| sg_daily_pv_generation | energy.daily_pv_generation | daily_pv_generation |
| sg_total_pv_generation | energy.total_pv_generation | total_pv_generation |
| sg_daily_exported_energy_from_PV | energy.daily_exported_energy_from_pv | daily_exported_energy_from_pv |
| sg_total_exported_energy_from_pv | energy.total_exported_energy_from_pv | total_exported_energy_from_pv |
| sg_load_power | state.load_power | load_power |
| sg_battery_export_power_raw | grid_flow.export_power_raw | export_power_raw |
| sg_daily_battery_charge_from_pv | energy.daily_battery_charge_from_pv | daily_battery_charge_from_pv |
| sg_total_battery_charge_from_pv | energy.total_battery_charge_from_pv | total_battery_charge_from_pv |
| sg_daily_direct_energy_consumption | energy.daily_direct_energy_consumption | daily_direct_energy_consumption |
| sg_total_direct_energy_consumption | energy.total_direct_energy_consumption | total_direct_energy_consumption |
| sg_battery_voltage | battery.battery_voltage | battery_voltage |
| sg_battery_level | battery_status.battery_level | battery_level |
| sg_battery_state_of_health | battery_health.battery_state_of_health | battery_state_of_health |
| sg_battery_temperature | battery_status.battery_temperature | battery_temperature |
| sg_daily_battery_discharge | energy.daily_battery_discharge | daily_battery_discharge |
| sg_total_battery_discharge | energy.total_battery_discharge | total_battery_discharge |
| sg_phase_a_current | grid_output.phase_a_current | phase_a_current |
| sg_phase_b_current | grid_output.phase_b_current | phase_b_current |
| sg_phase_c_current | grid_output.phase_c_current | phase_c_current |
| sg_total_active_power | grid_output.total_active_power | total_active_power |
| sg_daily_imported_energy | energy.daily_imported_energy | daily_imported_energy |
| sg_total_imported_energy | energy.total_imported_energy | total_imported_energy |
| sg_daily_battery_charge | energy.daily_battery_charge | daily_battery_charge |
| sg_total_battery_charge | energy.total_battery_charge | total_battery_charge |
| sg_daily_exported_energy | energy.daily_exported_energy | daily_exported_energy |
| sg_total_exported_energy | energy.total_exported_energy | total_exported_energy |
| sg_load_adjustment_mode_selection_raw | load_settings.load_adjustment_mode_selection_raw | load_adjustment_mode_selection_raw |
| sg_load_adjustment_mode_enable_raw | load_settings.load_adjustment_mode_enable_raw | load_adjustment_mode_enable_raw |
| sg_ems_mode_selection_raw | battery_settings.ems_mode_selection_raw | ems_mode_selection_raw |
| sg_battery_forced_charge_discharge_cmd_raw | battery_settings.battery_forced_charge_discharge_cmd_raw | battery_forced_charge_discharge_cmd_raw |
| sg_battery_forced_charge_discharge_power | battery_settings.battery_forced_charge_discharge_power | battery_forced_charge_discharge_power |
| uid_sg_battery_max_soc | battery_settings.battery_max_soc | battery_max_soc |
| uid_sg_battery_min_soc | battery_settings.battery_min_soc | battery_min_soc |
| sg_export_power_limit | export_settings.export_power_limit | export_power_limit |
| sg_backup_mode_raw | export_settings.backup_mode_raw | backup_mode_raw |
| sg_export_power_limit_mode_raw | export_settings.export_power_limit_mode_raw | export_power_limit_mode_raw |
| sg_active_power_limitation_raw | active_limitation.active_power_limitation_raw | active_power_limitation_raw |
| sg_active_power_limitation_ratio_raw | active_limitation.active_power_limitation_ratio_raw | active_power_limitation_ratio_raw |
| sg_battery_reserved_soc_for_backup | battery_settings.battery_reserved_soc_for_backup | battery_reserved_soc_for_backup |
| sg_inverter_firmware_version | inverter_firmware.inverter_firmware_version | inverter_firmware_version |
| sg_communication_module_firmware_version | communication_firmware.communication_module_firmware_version | communication_module_firmware_version |
| sg_battery_firmware_version | battery_firmware.battery_firmware_version | battery_firmware_version |
| sg_apl_shutdown_on_zero_raw | apl.apl_shutdown_at_zero_raw | apl_shutdown_at_zero_raw |
| sg_battery_max_charge_power | battery_limits.battery_max_charge_power | battery_max_charge_power |
| sg_battery_max_discharge_power | battery_limits.battery_max_discharge_power | battery_max_discharge_power |
| sg_battery_charging_start_power | battery_thresholds.battery_charging_start_power | battery_charging_start_power |
| sg_battery_discharging_start_power | battery_thresholds.battery_discharging_start_power | battery_discharging_start_power |

New unique IDs use serial_key within each entity platform. Entity IDs are
assigned by the entity registry; do not assume that a display name is its ID.
