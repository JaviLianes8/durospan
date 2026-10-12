"""Golden vectors for the systemd dialect.

Sources: the "Parsing Time Spans" examples of ``systemd.time(7)`` (``2 h``, ``2hours``,
``48hr``, ``1y 12month``, ``55s500ms``, ``300ms20s 5day``), the ``systemd-analyze
timespan`` example of ``systemd-analyze(1)`` (``1s``, ``300s`` printed as ``5min``,
``1year 0.000001s`` printed as ``1y 1us``) and the unit lengths of
``src/basic/time-util.h`` (a year is 31557600 s, a month 2629800 s).
"""

from __future__ import annotations

S = 1_000_000_000
MS = 1_000_000
US = 1_000
MIN = 60 * S
H = 60 * MIN
D = 24 * H
YEAR = 31_557_600 * S
MONTH = 2_629_800 * S

PARSE: list[tuple[str, int]] = [
    ("2 h", 2 * H),
    ("2hours", 2 * H),
    ("48hr", 48 * H),
    ("1y 12month", YEAR + 12 * MONTH),
    ("55s500ms", 55 * S + 500 * MS),
    ("300ms20s 5day", 300 * MS + 20 * S + 5 * D),
    ("1s", S),
    ("300s", 300 * S),
    ("1year 0.000001s", YEAR + US),
    ("2 h 30 min", 2 * H + 30 * MIN),
    ("1week 2days", 9 * D),
    ("5", 5 * S),
    ("1M", MONTH),
    ("1m", MIN),
    ("1.5h", 90 * MIN),
    ("1h 1h", 2 * H),
    ("10µs", 10 * US),
    ("20nsec", 20),
]

ERRORS: list[str] = ["", "-1s", "+1s", "1x", "infinity", "1 2 x", "h", "1h,30min"]

FORMAT: list[tuple[int, str]] = [
    (0, "0"),
    (S, "1s"),
    (300 * S, "5min"),
    (YEAR + US, "1y 1us"),
    (90 * S, "1min 30s"),
    (2 * H + 30 * MIN, "2h 30min"),
    (D + 500 * MS, "1d 500ms"),
]
