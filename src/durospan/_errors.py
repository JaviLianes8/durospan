"""The single error type raised by the duration grammar."""

from __future__ import annotations


class DurationError(ValueError):
    """Raised when a duration string or value does not fit the grammar."""
