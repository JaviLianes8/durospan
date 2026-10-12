"""Readable renderings with a chosen precision and unit range."""

from __future__ import annotations

from datetime import timedelta
from typing import Literal

from ._errors import DurationError
from ._numbers import DAY, HOUR, MINUTE, MS, NS, SECOND, US, WEEK, from_timedelta

Unit = Literal["w", "d", "h", "m", "s", "ms", "us", "ns"]
"""Unit symbols accepted by :func:`humanize` for ``smallest`` and ``largest``."""

_TABLE: tuple[tuple[str, int, str], ...] = (
    ("w", WEEK, "week"),
    ("d", DAY, "day"),
    ("h", HOUR, "hour"),
    ("m", MINUTE, "minute"),
    ("s", SECOND, "second"),
    ("ms", MS, "millisecond"),
    ("us", US, "microsecond"),
    ("ns", NS, "nanosecond"),
)
_INDEX = {symbol: i for i, (symbol, _, _) in enumerate(_TABLE)}


def humanize(
    value: int | timedelta,
    *,
    long: bool = False,
    precision: int | None = None,
    smallest: Unit = "s",
    largest: Unit = "w",
) -> str:
    """Render ``value`` (integer nanoseconds or a ``timedelta``) for people to read.

    ``precision`` keeps that many of the most significant units; the last kept unit is
    rounded half up and carries upward. ``smallest`` and ``largest`` bound the units used:
    anything above ``largest`` is expressed in it, anything below ``smallest`` is rounded.

    >>> humanize(5_400_000_000_000)
    '1h 30m'
    >>> humanize(timedelta(hours=1, minutes=30, seconds=5), long=True)
    '1 hour, 30 minutes, 5 seconds'
    >>> humanize(timedelta(minutes=59, seconds=59.6), precision=2)
    '1h'
    >>> humanize(timedelta(days=3), largest="h")
    '72h'
    """
    ns = from_timedelta(value) if isinstance(value, timedelta) else _checked_int(value)
    top, bottom = _bounds(largest, smallest)
    if precision is not None and precision < 1:
        raise DurationError(f"precision must be at least 1, got {precision}")
    magnitude = abs(ns)
    last = bottom
    if precision is not None:
        lead = _leading(_round(magnitude, _TABLE[bottom][1]), top, bottom)
        if lead is not None:
            last = min(lead + precision - 1, bottom)
    magnitude = _round(magnitude, _TABLE[last][1])
    parts = []
    for i in range(top, last + 1):
        symbol, size, name = _TABLE[i]
        count, magnitude = divmod(magnitude, size)
        if count:
            parts.append(_word(count, symbol, name, long))
    if not parts:
        symbol, _, name = _TABLE[bottom]
        return _word(0, symbol, name, long)
    sign = "-" if ns < 0 else ""
    return sign + (", " if long else " ").join(parts)


def _checked_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DurationError(f"expected integer nanoseconds or a timedelta, got {value!r}")
    return value


def _bounds(largest: str, smallest: str) -> tuple[int, int]:
    for label, unit in (("largest", largest), ("smallest", smallest)):
        if unit not in _INDEX:
            raise DurationError(f"unknown {label} unit {unit!r}; use one of {', '.join(_INDEX)}")
    top, bottom = _INDEX[largest], _INDEX[smallest]
    if top > bottom:
        raise DurationError(f"largest unit {largest!r} is smaller than smallest {smallest!r}")
    return top, bottom


def _round(magnitude: int, step: int) -> int:
    return (magnitude + step // 2) // step * step


def _leading(magnitude: int, top: int, bottom: int) -> int | None:
    for i in range(top, bottom + 1):
        if magnitude >= _TABLE[i][1]:
            return i
    return None


def _word(count: int, symbol: str, name: str, long: bool) -> str:
    if not long:
        return f"{count}{symbol}"
    return f"{count} {name}" + ("" if count == 1 else "s")
