"""The forgiving dialect for text people type: names, commas, ``and``, clocks, a sign."""

from __future__ import annotations

import re

from ._errors import syntax_error
from ._numbers import DAY, HOUR, MINUTE, MS, NS, SECOND, US, WEEK, scaled
from ._tokens import Grammar, scan

_SPELLINGS: dict[int, tuple[str, ...]] = {
    NS: ("ns", "nsec", "nsecs", "nanosecond", "nanoseconds"),
    US: ("us", "µs", "μs", "usec", "usecs", "microsecond", "microseconds"),
    MS: ("ms", "msec", "msecs", "millisecond", "milliseconds"),
    SECOND: ("s", "sec", "secs", "second", "seconds"),
    MINUTE: ("m", "min", "mins", "minute", "minutes"),
    HOUR: ("h", "hr", "hrs", "hour", "hours"),
    DAY: ("d", "day", "days"),
    WEEK: ("w", "wk", "wks", "week", "weeks"),
}

# Spellings that name a calendar unit: refused, because their length depends on a date.
AMBIGUOUS = frozenset({"mo", "mos", "mon", "month", "months", "y", "yr", "yrs", "year", "years"})

GRAMMAR = Grammar(
    name="human",
    units={name: size for size, names in _SPELLINGS.items() for name in names},
    case_sensitive=False,
    bare_seconds=False,
    repeats=False,
    words=True,
    ambiguous=AMBIGUOUS,
)

_CLOCK = re.compile(r"([0-9]+):([0-5][0-9])(?::([0-5][0-9]))?(?:\.([0-9]+))?")

_OUTPUT = (
    ("w", WEEK),
    ("d", DAY),
    ("h", HOUR),
    ("m", MINUTE),
    ("s", SECOND),
    ("ms", MS),
    ("us", US),
    ("ns", NS),
)


def parse(text: str) -> int:
    """Parse human duration text (``"1 hour, 30 minutes"``, ``"-1h30m"``, ``"1:30:00"``)."""
    body = text.lstrip()
    start = len(text) - len(body)
    sign = 1
    if body[:1] in ("-", "+"):
        sign = -1 if body[0] == "-" else 1
        start += 1
    if ":" in text:
        return sign * _clock(text, start)
    return sign * scan(text, GRAMMAR, start)


def _clock(text: str, start: int) -> int:
    body = text[start:].strip()
    match = _CLOCK.fullmatch(body)
    if match is None:
        position = text.index(body[:1], start) if body else start
        raise syntax_error("expected H:MM:SS or M:SS", text, position, body or text)
    first, second, third, frac = match.groups()
    if third is None:
        minutes, seconds = int(first), int(second)
        hours = 0
    else:
        hours, minutes, seconds = int(first), int(second), int(third)
    total = hours * HOUR + minutes * MINUTE + seconds * SECOND
    return total + scaled("0", frac or "", SECOND)


def format(ns: int) -> str:
    """Render nanoseconds canonically: ``1h 30m``, ``1m 500ms``, ``-2d``, ``0s``."""
    if ns == 0:
        return "0s"
    sign = "-" if ns < 0 else ""
    rest = abs(ns)
    parts = []
    for symbol, size in _OUTPUT:
        count, rest = divmod(rest, size)
        if count:
            parts.append(f"{count}{symbol}")
    return sign + " ".join(parts)
