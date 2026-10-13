"""Golden vectors for the go dialect.

Most cases are hand-written for this project; they follow the rules of Go's
``time.ParseDuration`` and ``Duration.String`` and are labelled ``hand-written`` below.
A few short vectors are cited verbatim from the Go standard library test file at
``CITED_URL`` (BSD-3-Clause), with the line they come from, values written as integer
nanoseconds.
"""

from __future__ import annotations

S = 1_000_000_000
MS = 1_000_000
US = 1_000
M = 60 * S
H = 60 * M
MAX = (1 << 63) - 1
MIN = -(1 << 63)

CITED_URL = "https://raw.githubusercontent.com/golang/go/go1.25.0/src/time/time_test.go"

# hand-written: plain numbers, signs, decimal forms, every unit, mixed and overflow edges
HAND_PARSE: list[tuple[str, int]] = [
    ("0", 0),
    ("7s", 7 * S),
    ("45s", 45 * S),
    ("2500s", 2500 * S),
    ("-7s", -7 * S),
    ("+7s", 7 * S),
    ("-0", 0),
    ("+0", 0),
    ("7.0s", 7 * S),
    ("7.25s", 7 * S + 250 * MS),
    ("7.s", 7 * S),
    (".25s", 250 * MS),
    ("2.000s", 2 * S),
    ("2.008s", 2 * S + 8 * MS),
    ("2.0080s", 2 * S + 8 * MS),
    ("200.00200s", 200 * S + 2 * MS),
    ("20ns", 20),
    ("21us", 21 * US),
    ("22µs", 22 * US),
    ("22μs", 22 * US),
    ("23ms", 23 * MS),
    ("25m", 25 * M),
    ("26h", 26 * H),
    ("2h15m", 2 * H + 15 * M),
    ("20.5s3m", 3 * M + 20 * S + 500 * MS),
    ("6h5m4s3ms2us1ns", 6 * H + 5 * M + 4 * S + 3 * MS + 2 * US + 1),
    ("12345678900ns", 12345678900),
    ("0.5h", 30 * M),
    ("0.6666666666666666666h", 40 * M),
    ("9007199254740995ns", (1 << 53) + 3),
    ("9223372036854775807ns", MAX),
    ("9223372036854775.807us", MAX),
    ("-9223372036854775808ns", MIN),
    ("-9223372036854775.808us", MIN),
    ("-2562047h47m16.854775808s", MIN),
]

# Cited from CITED_URL, parseDurationTests (line numbers in that file).
CITED_PARSE: list[tuple[str, int]] = [
    ("12µs", 12 * US),  # line 972
    ("-2m3.4s", -(2 * M + 3 * S + 400 * MS)),  # line 981
    ("1h2m3s4ms5us6ns", 1 * H + 2 * M + 3 * S + 4 * MS + 5 * US + 6),  # line 982
    ("39h9m14.425s", 39 * H + 9 * M + 14 * S + 425 * MS),  # line 983
]

# hand-written: empty, bare number, lone sign or dot, unknown unit, junk and overflow
HAND_ERRORS: list[str] = [
    "",
    "8",
    "+",
    "m",
    ".",
    "+.",
    ".m",
    "-.m",
    "2w",
    "�",
    "x � y",
    "9223372036854775900ns",
    "-9223372036854775809ns",
    "9223372036854777us",
    "9223372036854775.808us",
    "9223372036854ms775us808ns",
]

# Cited from CITED_URL, parseDurationErrorTests.
CITED_ERRORS: list[str] = [
    "1d",  # line 1029
    "9223372036854775808ns",  # line 1037
    "3000000h",  # line 1040
]

# hand-written: Duration.String output for every unit size and both extremes
HAND_FORMAT: list[tuple[int, str]] = [
    (0, "0s"),
    (7, "7ns"),
    (2500, "2.5µs"),
    (4500 * US, "4.5ms"),
    (6500 * MS, "6.5s"),
    (9 * M + 8 * S, "9m8s"),
    (3 * H + 2 * M + 1500 * MS, "3h2m1.5s"),
    (2 * M + 1, "2m0.000000001s"),
    (MIN, "-2562047h47m16.854775808s"),
]

# Cited from CITED_URL, durationTests.
CITED_FORMAT: list[tuple[int, str]] = [
    (4 * M + 5001 * MS, "4m5.001s"),  # line 624
    (MAX, "2562047h47m16.854775807s"),  # line 627
]

PARSE = HAND_PARSE + CITED_PARSE
ERRORS = HAND_ERRORS + CITED_ERRORS
FORMAT = HAND_FORMAT + CITED_FORMAT
