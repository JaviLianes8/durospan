"""Parse a human duration string into seconds, using the shared grammar."""

from __future__ import annotations

import re
from datetime import timedelta

from ._errors import DurationError
from ._units import SECONDS_BY_UNIT

_TOKEN = re.compile(r"\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s*")


def parse(text: str) -> float:
    """Return the seconds described by ``text`` (e.g. ``"1d 4h30m"`` or ``"28:30:00"``)."""
    cleaned = text.strip()
    if not cleaned:
        raise DurationError("empty duration")
    if ":" in cleaned:
        return _parse_clock(cleaned)
    return _parse_tokens(cleaned)


def parse_timedelta(text: str) -> timedelta:
    """Return ``text`` as a :class:`datetime.timedelta`."""
    try:
        return timedelta(seconds=parse(text))
    except OverflowError as exc:
        raise DurationError(f"duration out of range: {text!r}") from exc


def _parse_tokens(text: str) -> float:
    total = 0.0
    seen: set[str] = set()
    position = 0
    for match in _TOKEN.finditer(text):
        if match.start() != position:
            break
        symbol = match.group(2).lower()
        size = SECONDS_BY_UNIT.get(symbol)
        if size is None:
            raise DurationError(f"unknown unit {symbol!r} in {text!r}")
        if symbol in seen:
            raise DurationError(f"unit {symbol!r} repeated in {text!r}")
        seen.add(symbol)
        total += float(match.group(1)) * size
        position = match.end()
    if position != len(text) or not seen:
        raise DurationError(f"cannot parse duration {text!r}")
    return total


def _parse_clock(text: str) -> float:
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise DurationError(f"cannot parse clock duration {text!r}")
    *lead, last = parts
    total = 0.0
    for field in lead:
        if not field.isdigit():
            raise DurationError(f"cannot parse clock duration {text!r}")
        total = total * 60 + int(field)
    try:
        seconds = float(last)
    except ValueError as exc:
        raise DurationError(f"cannot parse clock duration {text!r}") from exc
    if seconds < 0:
        raise DurationError(f"negative seconds in {text!r}")
    return total * 60 + seconds
