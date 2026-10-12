"""Typed, zero-dependency round-trip between human durations and seconds, one grammar both ways.

Exact parsing to integer nanoseconds and canonical formatting in the Go, ISO 8601,
systemd, Prometheus and human dialects.
"""

from __future__ import annotations

from ._api import DIALECTS, Dialect, convert, format_duration, parse_ns, parse_seconds
from ._errors import (
    AmbiguousDurationError,
    DurationError,
    DurationRangeError,
    DurationSyntaxError,
)
from ._format import format, format_timedelta
from ._parse import parse, parse_timedelta
from ._style import Style

__version__ = "0.2.0"

__all__ = [
    "DIALECTS",
    "AmbiguousDurationError",
    "Dialect",
    "DurationError",
    "DurationRangeError",
    "DurationSyntaxError",
    "Style",
    "convert",
    "format",
    "format_duration",
    "format_timedelta",
    "parse",
    "parse_ns",
    "parse_seconds",
    "parse_timedelta",
]
