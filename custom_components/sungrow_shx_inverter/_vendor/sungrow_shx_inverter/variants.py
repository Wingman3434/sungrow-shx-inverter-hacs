"""Model codes and capabilities from the supplied residential hybrid register map."""

from dataclasses import dataclass


class UnsupportedDeviceError(ValueError):
    """The unit did not identify as a supported residential hybrid inverter."""


@dataclass(frozen=True)
class Model:
    """Capabilities inferable from the device code, not from live power values."""

    name: str
    phases: int
    mppts: int
    extended_firmware: bool
    active_limitation: bool


MODEL_NAMES: dict[int, str] = {
    3334: "SH3K6",
    3335: "SH4K6",
    3337: "SH5K-20",
    3331: "SH5K-V13",
    3338: "SH3K6-30",
    3339: "SH4K6-30",
    3340: "SH5K-30",
    3351: "SH3.0RS",
    3341: "SH3.6RS",
    3352: "SH4.0RS",
    3343: "SH5.0RS",
    3344: "SH6.0RS",
    3354: "SH8.0RS",
    3355: "SH10RS",
    3584: "SH5.0RT",
    3585: "SH6.0RT",
    3586: "SH8.0RT",
    3587: "SH10RT",
    3600: "SH5.0RT-20",
    3601: "SH6.0RT-20",
    3602: "SH8.0RT-20",
    3603: "SH10RT-20",
    3596: "SH5.0RT-V112",
    3597: "SH6.0RT-V112",
    3598: "SH8.0RT-V112",
    3599: "SH10RT-V112",
    3592: "SH5.0RT-V122",
    3593: "SH6.0RT-V122",
    3594: "SH8.0RT-V122",
    3595: "SH10RT-V122",
    3616: "SH5T",
    3617: "SH6T",
    3618: "SH8T",
    3619: "SH10T",
    3620: "SH12T",
    3621: "SH15T",
    3622: "SH20T",
    3624: "SH25T",
    3367: "MG5RL",
    3368: "MG6RL",
}


def identify(code: int | None) -> Model:
    """Identify a supported model; refuse unknown devices."""
    if code not in MODEL_NAMES:
        raise UnsupportedDeviceError(f"Unknown device code: {code!r}")
    name = MODEL_NAMES[code]
    rs = "RS" in name
    mg = name.startswith("MG")
    three_phase = "RT" in name or name.endswith("T")
    return Model(
        name=name,
        phases=3 if three_phase else 1,
        mppts=4
        if name in ("SH8.0RS", "SH10RS")
        else 3
        if name.endswith("T") and "RT" not in name
        else 2,
        extended_firmware=not (rs or mg),
        active_limitation=not mg,
    )
