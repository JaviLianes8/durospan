"""systemd time spans, as described in ``systemd.time(7)`` and ``src/basic/time-util.c``.

Units are case-sensitive (``M`` is a month, ``m`` a minute), spaces may sit anywhere
between tokens, a bare number means seconds and repeated units add up. Months and years
use the fixed lengths systemd defines in ``time-util.h``: a year is 365.25 days and a
month is a twelfth of that (the man page rounds it to "30.44 days").
"""

from __future__ import annotations

from ._errors import DurationRangeError, syntax_error
from ._numbers import DAY, HOUR, MINUTE, MS, NS, SECOND, US, WEEK
from ._tokens import Grammar, scan

YEAR = 31_557_600 * SECOND
MONTH = 2_629_800 * SECOND

_SPELLINGS: dict[int, tuple[str, ...]] = {
    NS: ("nsec", "ns"),
    US: ("usec", "us", "µs", "μs"),
    MS: ("msec", "ms"),
    SECOND: ("seconds", "second", "sec", "s"),
    MINUTE: ("minutes", "minute", "min", "m"),
    HOUR: ("hours", "hour", "hr", "h"),
    DAY: ("days", "day", "d"),
    WEEK: ("weeks", "week", "w"),
    MONTH: ("months", "month", "M"),
    YEAR: ("years", "year", "y"),
}

GRAMMAR = Grammar(
    name="systemd",
    units={name: size for size, names in _SPELLINGS.items() for name in names},
    case_sensitive=True,
    bare_seconds=True,
    repeats=True,
    words=False,
)

# The output table of format_timespan(), largest first, plus ns for sub-microsecond rests.
_OUTPUT = (
    ("y", YEAR),
    ("month", MONTH),
    ("w", WEEK),
    ("d", DAY),
    ("h", HOUR),
    ("min", MINUTE),
    ("s", SECOND),
    ("ms", MS),
    ("us", US),
    ("ns", NS),
)


def parse(text: str) -> int:
    """Parse a systemd time span into integer nanoseconds."""
    stripped = text.strip()
    if stripped == "infinity":
        raise DurationRangeError("'infinity' is not a finite duration", text=text)
    if stripped.startswith(("-", "+")):
        position = text.index(stripped[0])
        raise syntax_error("systemd time spans have no sign", text, position, stripped[0])
    return scan(text, GRAMMAR)


def format(ns: int) -> str:
    """Render nanoseconds like systemd's ``format_timespan`` (``1min 30s``, ``0``)."""
    if ns < 0:
        raise DurationRangeError(f"systemd time spans cannot be negative: {ns} ns")
    if ns == 0:
        return "0"
    parts = []
    for symbol, size in _OUTPUT:
        count, ns = divmod(ns, size)
        if count:
            parts.append(f"{count}{symbol}")
    return " ".join(parts)
