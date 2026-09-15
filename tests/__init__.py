"""Common Sungrow test data."""

from modbus_connection.mock import MockModbusUnit

DOMAIN = "sungrow_shx_inverter"
SERIAL = "SGTEST12345"
USER_INPUT = {"host": "192.0.2.2", "port": 502, "unit_id": 1, "message_wait": 0.1}


def seed(unit: MockModbusUnit, code: int = 0x0E03) -> None:
    """Seed a deterministic SH10RT with writable settings."""
    serial = SERIAL.encode().ljust(20, b"\0")
    unit.input[4989] = [
        int.from_bytes(serial[i : i + 2], "big") for i in range(0, 20, 2)
    ]
    unit.input[4999] = code
    unit.input[5000] = 100
    unit.input[5010] = 2300
    unit.input[5011] = 100
    unit.input[13000] = 3
    unit.input[13001] = 120
    unit.input[13002] = [1000, 0]
    unit.input[5627] = 100
    unit.input[5621] = 0
    unit.input[5622] = 1000
    unit.holding[13057] = 1000
    unit.holding[13058] = 100
    unit.holding[13074] = 0x55
    unit.holding[13050] = 0xCC
