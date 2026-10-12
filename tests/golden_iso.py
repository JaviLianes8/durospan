"""Golden vectors for the iso8601 dialect.

Sources: the duration examples of ISO 8601-1:2019 clause 5.5.2 (``P3Y6M4DT12H30M5S``,
``P23DT23H``, ``P4Y``, ``PT36H`` against ``P1DT12H``, the decimal comma) and the
``xs:duration`` lexical examples of W3C XML Schema 1.1 Part 2, section 3.3.6
(``P1347Y``, ``P1347M``, ``P1Y2MT2H``, ``-P1347M``, and the invalid ``P-1347M`` and
``P1Y2MT``). Values are integer nanoseconds; calendar values use the reference date.
"""

from __future__ import annotations

from datetime import date

S = 1_000_000_000
H = 3600 * S
D = 24 * H

FIXED: list[tuple[str, int]] = [
    ("P23DT23H", 23 * D + 23 * H),
    ("PT36H", 36 * H),
    ("P1DT12H", 36 * H),
    ("PT0S", 0),
    ("P0D", 0),
    ("PT1M", 60 * S),
    ("P1W", 7 * D),
    ("PT0,5S", S // 2),
    ("PT0.5S", S // 2),
    ("P1DT2H3M4.5S", D + 2 * H + 3 * 60 * S + 4 * S + S // 2),
    ("-P1D", -D),
    ("PT1.5H", 90 * 60 * S),
]

# (text, reference date, nanoseconds): years and months resolved on the calendar.
CALENDAR: list[tuple[str, date, int]] = [
    (
        "P3Y6M4DT12H30M5S",
        date(2000, 1, 1),
        ((date(2003, 7, 1) - date(2000, 1, 1)).days + 4) * D + 12 * H + 1805 * S,
    ),
    ("P4Y", date(2000, 1, 1), 1461 * D),
    ("P1M", date(2024, 1, 31), 29 * D),
    ("P1M", date(2023, 1, 31), 28 * D),
    ("P1347M", date(2000, 1, 1), (date(2112, 4, 1) - date(2000, 1, 1)).days * D),
    ("P1347Y", date(2000, 1, 1), (date(3347, 1, 1) - date(2000, 1, 1)).days * D),
    ("P1Y2MT2H", date(2000, 1, 1), (date(2001, 3, 1) - date(2000, 1, 1)).days * D + 2 * H),
    ("-P1347M", date(2200, 1, 1), -(date(2200, 1, 1) - date(2087, 10, 1)).days * D),
]

# Year and month spans that must refuse to guess a length without a reference date.
AMBIGUOUS: list[str] = ["P3Y6M4DT12H30M5S", "P4Y", "P1M", "P1347M", "P1Y2MT2H"]

ERRORS: list[str] = [
    "P-1347M",
    "P1Y2MT",
    "P",
    "PT",
    "P1H",
    "PT1D",
    "1D",
    "P1.5H",
    "PT1.5H30M",
    "P1W1D",
    "P0.5Y",
    "PT1S2M",
    "P 1D",
]

FORMAT: list[tuple[int, str]] = [
    (0, "PT0S"),
    (36 * H, "P1DT12H"),
    (23 * D + 23 * H, "P23DT23H"),
    (90 * 60 * S, "PT1H30M"),
    (S // 2, "PT0.5S"),
    (-D, "-P1D"),
    (1, "PT0.000000001S"),
]
