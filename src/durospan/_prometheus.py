"""Prometheus durations, as parsed by ``model.ParseDuration`` in ``prometheus/common``.

The grammar is units ``y w d h m s ms`` with whole numbers, largest unit first, each
unit at most once, no sign and no spaces, plus the literal ``"0"``. Upstream implements
this with a hand-written loop; the anchored regex below accepts exactly the same inputs.
A year is 365 days and a week 7 days, by Prometheus's own definition. Values must fit an
int64 count of nanoseconds, the range of Go's ``time.Duration``.
"""

from __future__ import annotations

import re

from ._errors import DurationRangeError, DurationSyntaxError, syntax_error
from ._numbers import DAY, HOUR, INT64_MAX, MINUTE, MS, SECOND, WEEK

YEAR = 365 * DAY
_UNITS: tuple[tuple[str, int], ...] = (
    ("y", YEAR),
    ("w", WEEK),
    ("d", DAY),
    ("h", HOUR),
    ("m", MINUTE),
    ("s", SECOND),
    ("ms", MS),
)
_PATTERN = re.compile("".join(rf"(?:([0-9]+){symbol})?" for symbol, _ in _UNITS))
_SIZE = dict(_UNITS)


def parse(text: str) -> int:
    """Parse a Prometheus duration into integer nanoseconds."""
    if text == "0":
        return 0
    if text == "":
        raise DurationSyntaxError("empty duration string", text=text, position=0, token="")
    match = _PATTERN.fullmatch(text)
    if match is None:
        raise _locate(text)
    total = 0
    for (_, size), count in zip(_UNITS, match.groups(), strict=True):
        if count is not None:
            total += int(count) * size
            if total > INT64_MAX:
                raise DurationRangeError(f"duration out of range: {text!r}", text=text)
    return total


def _locate(text: str) -> DurationSyntaxError:
    pos, last = 0, -1
    for match in re.finditer(r"([0-9]+)([a-z]*)|.", text):
        if match.start() != pos or match.group(1) is None:
            return syntax_error("expected a whole number and a unit", text, pos, text[pos])
        unit = match.group(2)
        if not unit and text[match.end() : match.end() + 1] == ".":
            return syntax_error("only whole numbers are allowed", text, match.end(), ".")
        if unit not in _SIZE:
            label = "missing unit" if not unit else f"unknown unit {unit!r}"
            return syntax_error(label, text, match.start(2), unit or match.group(1))
        rank = [symbol for symbol, _ in _UNITS].index(unit)
        if rank <= last:
            return syntax_error(
                f"unit {unit!r} repeated or out of order", text, match.start(2), unit
            )
        last, pos = rank, match.end()
    return syntax_error("invalid Prometheus duration", text, 0, text)


def format(ns: int) -> str:
    """Render nanoseconds like Prometheus's ``Duration.String`` (``2w``, ``23d1h``, ``0s``)."""
    if ns < 0:
        raise DurationRangeError(f"Prometheus durations cannot be negative: {ns} ns")
    if ns % MS:
        raise DurationRangeError(f"Prometheus durations have millisecond precision: {ns} ns")
    if ns == 0:
        return "0s"
    parts = []
    for symbol, size in _UNITS:
        # Years and weeks only when they divide exactly: Prometheus prints 90d, not 12w6d.
        if symbol in ("y", "w") and ns % size:
            continue
        count, ns = divmod(ns, size)
        if count:
            parts.append(f"{count}{symbol}")
    return "".join(parts)
