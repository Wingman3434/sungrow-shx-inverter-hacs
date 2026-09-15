"""Register command values and human-readable running states."""

from enum import IntEnum


class Enable(IntEnum):
    """The vendor's enable/disable words (not Boolean 1/0)."""

    DISABLED = 0x55
    ENABLED = 0xAA


class EmsMode(IntEnum):
    """Energy management policy."""

    SELF_CONSUMPTION = 0
    FORCED = 2
    EXTERNAL_EMS = 3
    VPP = 4


class ForcedChargeDischarge(IntEnum):
    """Battery forced operation."""

    STOP = 0xCC
    CHARGE = 0xAA
    DISCHARGE = 0xBB


class LoadAdjustment(IntEnum):
    """Load adjustment policy."""

    TIMING = 0
    ON_OFF = 1
    POWER_OPTIMIZATION = 2
    DISABLED = 3


class InverterCommand(IntEnum):
    """Write-only operating commands."""

    START = 0xCF
    STOP = 0xCE


RUNNING_STATES: dict[int, str] = {
    0: "Running",
    1: "Stop",
    2: "Key stop",
    4: "Emergency Stop",
    8: "Standby",
    32: "Starting",
    16: "Initial standby",
    20: "Microgrid Operation",
    64: "Running",
    65: "Off-grid Charge",
    128: "Derating Running",
    256: "Fault",
    512: "Update Failed",
    1024: "Running in maintain mode",
    2048: "Running in compulsory (forced) mode",
    4096: "Running (off-grid)",
    4369: "Uninitialized",
    4608: "Initial standby",
    4864: "Key stop",
    5120: "Standby",
    5376: "Emergency Stop",
    5632: "Starting",
    5888: "AFCI self-test shutdown",
    6144: "Intelligent Station Building Status",
    6400: "Safe Mode",
    8192: "Open loop",
    9472: "Communicate fault",
    9473: "Restarting",
    16384: "Running in External EMS mode",
    16385: "Emergency Charging Operation",
    32768: "Stop",
    21760: "Fault",
    33024: "Derating Running",
    33280: "Dispatch Running",
    37120: "Warn Running",
}
