"""Golden vectors for the prometheus dialect.

Source: ``model/time_test.go`` in ``prometheus/common`` (``TestParseDuration`` and its
bad-input cases, Apache-2.0), plus the anchored grammar of ``model.ParseDuration``.
Values are integer nanoseconds; a year is 365 days by Prometheus's definition.
"""

from __future__ import annotations

S = 1_000_000_000
MS = 1_000_000
M = 60 * S
H = 60 * M
D = 24 * H
W = 7 * D
Y = 365 * D

# (text, nanoseconds, canonical rendering)
PARSE: list[tuple[str, int, str]] = [
    ("0", 0, "0s"),
    ("0w", 0, "0s"),
    ("0s", 0, "0s"),
    ("324ms", 324 * MS, "324ms"),
    ("3s", 3 * S, "3s"),
    ("5m", 5 * M, "5m"),
    ("1h", H, "1h"),
    ("4d", 4 * D, "4d"),
    ("4d1h", 4 * D + H, "4d1h"),
    ("14d", 14 * D, "2w"),
    ("3w", 3 * W, "3w"),
    ("3w2d1h", 3 * W + 2 * D + H, "23d1h"),
    ("10y", 10 * Y, "10y"),
    ("1y2w3d4h5m6s7ms", Y + 2 * W + 3 * D + 4 * H + 5 * M + 6 * S + 7 * MS, ""),
]

ERRORS: list[str] = [
    "",
    "1",
    "1y1m1d",
    "-1w",
    "1.5d",
    "d",
    "294y",
    "200y10400w",
    "107675d",
    "2584200h",
    "1h1h",
    "1H",
    "1h 30m",
]
