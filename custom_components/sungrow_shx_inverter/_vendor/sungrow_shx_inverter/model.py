"""Component base, write validation, and update reports."""

from collections.abc import Callable
from dataclasses import dataclass, field
from math import isclose, isfinite
from typing import Any

from modbus_connection import ModbusError
from modbus_connection.model import Component


def bounded(minimum: float, maximum: float, step: float = 1) -> Callable[[Any], float]:
    """Reject non-finite, out-of-range and off-step writes before any I/O."""

    def validate(value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("A numeric value is required")
        number = float(value)
        if not isfinite(number) or not minimum <= number <= maximum:
            raise ValueError(f"Value must be between {minimum} and {maximum}")
        # Step is register resolution, relative to zero, not a UI slider origin.
        if not isclose(number / step, round(number / step), abs_tol=1e-8):
            raise ValueError(f"Value must be a multiple of {step}")
        return number

    return validate


def one_of(*values: int) -> Callable[[Any], int]:
    """Validate command words without silently truncating floats."""

    def validate(value: Any) -> int:
        if isinstance(value, bool) or value not in values:
            raise ValueError(f"Value must be one of {values}")
        return int(value)

    return validate


class SungrowComponent(Component):
    """Read only declared contiguous words; never bridge undocumented gaps."""

    max_gap = 0
    max_span = 100


@dataclass(frozen=True)
class UpdateReport:
    """Successful and failed subsystems in one poll."""

    updated: set[str] = field(default_factory=set)
    failed: dict[str, ModbusError] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        """Whether every attempted subsystem answered."""
        return not self.failed
