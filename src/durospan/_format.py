"""Format a duration (seconds or timedelta) back into the shared grammar."""

from __future__ import annotations

import math
from datetime import timedelta

from ._errors import DurationError
from ._style import Style
from ._units import UNITS


def format(seconds: float, *, style: Style = "token") -> str:
    """Render ``seconds`` as a duration string in the given ``style``."""
    value = _finite_non_negative(seconds)
    if style == "clock":
        return _clock(value)
    if style == "token":
        return _tokens(value, separator=" ")
    if style == "compact":
        return _tokens(value, separator="")
    raise DurationError(f"unknown style {style!r}")


def format_timedelta(delta: timedelta, *, style: Style = "token") -> str:
    """Render a :class:`datetime.timedelta` in the given ``style``."""
    return format(delta.total_seconds(), style=style)


def _finite_non_negative(seconds: float) -> float:
    value = float(seconds)
    if math.isnan(value) or math.isinf(value):
        raise DurationError(f"not a finite duration: {seconds!r}")
    if value < 0:
        raise DurationError(f"negative duration: {seconds!r}")
    return value


def _tokens(seconds: float, *, separator: str) -> str:
    counts = _split(seconds)
    parts = [f"{_number(value)}{symbol}" for symbol, value in counts if value]
    return separator.join(parts) if parts else "0s"


def _split(seconds: float) -> list[tuple[str, float]]:
    whole = int(seconds)
    frac = seconds - whole
    counts: list[tuple[str, float]] = []
    for symbol, size in UNITS:
        if size == 1:
            counts.append((symbol, whole + frac))
        else:
            count, whole = divmod(whole, size)
            counts.append((symbol, float(count)))
    return counts


def _clock(seconds: float) -> str:
    whole = int(seconds)
    frac = seconds - whole
    hours, rest = divmod(whole, 3600)
    minutes, secs = divmod(rest, 60)
    tail = repr(frac)[1:] if frac else ""
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{tail}"


def _number(value: float) -> str:
    return str(int(value)) if value == int(value) else repr(value)
