"""Typed, zero-dependency round-trip between human durations and seconds, one grammar both ways."""

from __future__ import annotations

from ._errors import DurationError
from ._format import format, format_timedelta
from ._parse import parse, parse_timedelta
from ._style import Style

__version__ = "0.1.0"

__all__ = [
    "DurationError",
    "Style",
    "format",
    "format_timedelta",
    "parse",
    "parse_timedelta",
]
