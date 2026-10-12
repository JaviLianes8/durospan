"""Exact integer arithmetic, unit sizes and range guards shared by every dialect."""

from __future__ import annotations

from datetime import timedelta

from ._errors import DurationRangeError

NS = 1
US = 1_000
MS = 1_000_000
SECOND = 1_000_000_000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

INT64_MAX = (1 << 63) - 1
INT64_MIN = -(1 << 63)
TIMEDELTA_MAX_NS: int = (timedelta.max.days * 86400 + timedelta.max.seconds) * SECOND + (
    timedelta.max.microseconds * US
)
TIMEDELTA_MIN_NS: int = timedelta.min.days * 86400 * SECOND

# Long enough for any real duration, short enough that no input can make int() or the
# regex engines do unbounded work.
MAX_INPUT = 4096


def check_length(text: str) -> None:
    """Refuse inputs longer than ``MAX_INPUT`` before any parsing work happens."""
    if len(text) > MAX_INPUT:
        raise DurationRangeError(f"duration text longer than {MAX_INPUT} characters")


def scaled(whole: str, fraction: str, unit: int) -> int:
    """Return ``whole.fraction`` units in nanoseconds, truncating toward zero, exactly."""
    digits = len(fraction)
    scale: int = 10**digits
    numerator = int(whole or "0") * scale + int(fraction or "0")
    return numerator * unit // scale


def check_range(ns: int, text: str, low: int, high: int) -> int:
    """Return ``ns`` unchanged, or raise when it falls outside ``[low, high]``."""
    if ns < low or ns > high:
        raise DurationRangeError(f"duration out of range: {text!r}", text=text)
    return ns


def check_timedelta_range(ns: int, text: str) -> int:
    """Keep a value inside what ``datetime.timedelta`` can represent."""
    return check_range(ns, text, TIMEDELTA_MIN_NS, TIMEDELTA_MAX_NS)


def to_timedelta(ns: int) -> timedelta:
    """Convert nanoseconds to a ``timedelta``, refusing to drop sub-microsecond digits."""
    micros, rest = divmod(ns, US)
    if rest:
        raise DurationRangeError(
            f"{ns} ns has a sub-microsecond part that timedelta cannot hold; use parse_ns"
        )
    try:
        return timedelta(microseconds=micros)
    except OverflowError as exc:
        raise DurationRangeError(f"{ns} ns is outside the timedelta range") from exc


def from_timedelta(delta: timedelta) -> int:
    """Convert a ``timedelta`` to integer nanoseconds without going through ``float``."""
    return ((delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds) * US


def frac_digits(value: int, digits: int) -> str:
    """Render ``value`` (< 10**digits) as a fraction without trailing zeros, '' for 0."""
    if value == 0:
        return ""
    return "." + str(value).rjust(digits, "0").rstrip("0")
