"""Typed, zero-dependency round-trip between human durations and seconds, one grammar both ways.

Exact parsing to integer nanoseconds and canonical formatting in the Go, ISO 8601,
systemd, Prometheus and human dialects, plus humanizing and search in free text.
"""

from __future__ import annotations

from ._api import DIALECTS, Dialect, convert, format_duration, parse_ns, parse_seconds
from ._errors import (
    AmbiguousDurationError,
    DurationError,
    DurationRangeError,
    DurationSyntaxError,
)
from ._find import DurationMatch, find_durations
from ._format import format, format_timedelta
from ._humanize import Unit, humanize
from ._parse import parse, parse_timedelta
from ._style import Style

__version__ = "0.2.2"

__all__ = [
    "DIALECTS",
    "AmbiguousDurationError",
    "Dialect",
    "DurationError",
    "DurationMatch",
    "DurationRangeError",
    "DurationSyntaxError",
    "Style",
    "Unit",
    "convert",
    "find_durations",
    "format",
    "format_duration",
    "format_timedelta",
    "humanize",
    "parse",
    "parse_ns",
    "parse_seconds",
    "parse_timedelta",
]
