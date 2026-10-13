"""Golden vectors for the prometheus dialect.

Most cases are hand-written for this project; they follow the rules of ``ParseDuration``
and ``Duration.String`` in ``model/time.go`` of ``prometheus/common`` (whole numbers,
units ``y w d h m s ms`` largest first and each at most once, no sign, no spaces, an
int64 nanosecond range; years and weeks printed only when they divide exactly) and are
labelled ``hand-written`` below. A few short vectors are cited verbatim from the upstream
test file at ``CITED_URL`` (Apache-2.0), with the line they come from. Values are integer
nanoseconds; a year is 365 days by Prometheus's definition.
"""

from __future__ import annotations

S = 1_000_000_000
MS = 1_000_000
M = 60 * S
H = 60 * M
D = 24 * H
W = 7 * D
Y = 365 * D

CITED_URL = "https://raw.githubusercontent.com/prometheus/common/v0.72.1/model/time_test.go"

# hand-written: (text, nanoseconds, canonical rendering), carries, exact-only years and
# weeks, leading zeros, every unit once and both ends of the range
HAND_PARSE: list[tuple[str, int, str]] = [
    ("0ms", 0, "0s"),
    ("1ms", MS, "1ms"),
    ("999ms", 999 * MS, "999ms"),
    ("1000ms", S, "1s"),
    ("90s", 90 * S, "1m30s"),
    ("60m", H, "1h"),
    ("36h", 36 * H, "1d12h"),
    ("7d", W, "1w"),
    ("8d", 8 * D, "8d"),
    ("52w1d", Y, "1y"),
    ("1y1d", Y + D, "366d"),
    ("007s", 7 * S, "7s"),
    ("1y2w3d4h5m6s7ms", Y + 2 * W + 3 * D + 4 * H + 5 * M + 6 * S + 7 * MS, "382d4h5m6s7ms"),
    ("292y", 292 * Y, "292y"),
    ("106751d23h47m16s854ms", 9_223_372_036_854 * MS, "106751d23h47m16s854ms"),
]

# Cited from CITED_URL, TestParseDuration (line of the case's ``in`` field).
CITED_PARSE: list[tuple[str, int, str]] = [
    ("324ms", 324 * MS, "324ms"),  # line 121
    ("14d", 14 * D, "2w"),  # line 157
    ("3w2d1h", 3 * W + 2 * D + H, "23d1h"),  # line 169
]

# hand-written: sign, repeated or out-of-order unit, case, spaces, fractions, units from
# other dialects, non-ASCII digits and one past the range
HAND_ERRORS: list[str] = [
    "",
    "s",
    "5",
    "-1w",
    "+1s",
    "1h1h",
    "1m1h",
    "1s1m",
    "1H",
    "1h 30m",
    " 1s",
    "1s ",
    "0.5s",
    "1us",
    "1ns",
    "1x",
    "s1",
    chr(0x0661) + "s",  # ARABIC-INDIC DIGIT ONE
    "293y",
    "106751d23h47m16s855ms",
]

# Cited from CITED_URL, TestParseBadDuration.
CITED_ERRORS: list[str] = [
    "1y1m1d",  # line 433
    "294y",  # line 436
    "2584200h",  # line 439
]

PARSE = HAND_PARSE + CITED_PARSE
ERRORS = HAND_ERRORS + CITED_ERRORS
