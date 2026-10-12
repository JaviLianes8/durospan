"""Exact, dialect-aware parsing and formatting on integer nanoseconds."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal, get_args

from . import _go, _human, _iso, _prometheus, _systemd
from ._errors import DurationError, DurationSyntaxError
from ._iso import Reference
from ._numbers import (
    INT64_MAX,
    INT64_MIN,
    check_length,
    check_range,
    check_timedelta_range,
    from_timedelta,
)

Dialect = Literal["human", "go", "iso8601", "systemd", "prometheus"]
"""The duration grammars ``durospan`` reads and writes."""

DIALECTS: tuple[Dialect, ...] = get_args(Dialect)

_FORMATTERS: dict[str, Callable[[int], str]] = {
    "human": _human.format,
    "go": _go.format,
    "iso8601": _iso.format,
    "systemd": _systemd.format,
    "prometheus": _prometheus.format,
}


def _check_dialect(dialect: str) -> None:
    if dialect not in _FORMATTERS:
        raise DurationError(f"unknown dialect {dialect!r}; choose one of {', '.join(DIALECTS)}")


def parse_ns(text: str, *, dialect: Dialect = "human", reference: Reference | None = None) -> int:
    """Parse ``text`` in ``dialect`` into an exact integer number of nanoseconds.

    ``reference`` (a ``date`` or ``datetime``) resolves ISO 8601 years and months on the
    calendar; without it they raise :class:`AmbiguousDurationError`. Other dialects have
    no calendar units and ignore it. Fractions finer than
    a nanosecond truncate toward zero, as in Go.

    >>> parse_ns("1h30m", dialect="go")
    5400000000000
    >>> parse_ns("PT1.5S", dialect="iso8601")
    1500000000
    >>> parse_ns("2 h 30 min", dialect="systemd")
    9000000000000
    >>> parse_ns("1 hour, 30 minutes")
    5400000000000
    """
    _check_dialect(dialect)
    if not isinstance(text, str):
        raise DurationError(f"expected text, got {type(text).__name__}")
    if reference is not None and not isinstance(reference, date):
        raise DurationError(f"reference must be a date or datetime, got {reference!r}")
    check_length(text)
    if dialect == "go":
        return _go.parse(text)
    if dialect == "prometheus":
        return check_range(_prometheus.parse(text), text, INT64_MIN, INT64_MAX)
    if not text.strip():
        raise DurationSyntaxError("empty duration", text=text, position=0, token="")
    if dialect == "iso8601":
        ns = _iso.parse(text, reference)
    elif dialect == "systemd":
        ns = _systemd.parse(text)
    else:
        ns = _human.parse(text)
    return check_timedelta_range(ns, text)


def parse_seconds(
    text: str, *, dialect: Dialect = "human", reference: Reference | None = None
) -> Decimal:
    """Parse ``text`` into an exact ``Decimal`` number of seconds.

    >>> parse_seconds("300ms", dialect="go")
    Decimal('0.300000000')
    """
    return Decimal(parse_ns(text, dialect=dialect, reference=reference)).scaleb(-9)


def format_duration(value: int | timedelta, *, dialect: Dialect = "human") -> str:
    """Render ``value`` (integer nanoseconds or a ``timedelta``) canonically in ``dialect``.

    Each dialect writes the form its reference tool writes, and parsing the result in
    the same dialect gives the exact value back. Values must fit the dialect's range:
    int64 nanoseconds for go and prometheus, the ``timedelta`` range for the others.

    >>> format_duration(5_400_000_000_000, dialect="go")
    '1h30m0s'
    >>> format_duration(timedelta(days=1, hours=2), dialect="iso8601")
    'P1DT2H'
    >>> format_duration(90_000_000_000, dialect="systemd")
    '1min 30s'
    """
    _check_dialect(dialect)
    ns = _as_ns(value)
    if dialect in ("go", "prometheus"):
        check_range(ns, str(value), INT64_MIN, INT64_MAX)
    else:
        check_timedelta_range(ns, str(value))
    return _FORMATTERS[dialect](ns)


def convert(
    text: str,
    *,
    source: Dialect,
    target: Dialect,
    reference: Reference | None = None,
) -> str:
    """Re-spell duration ``text`` from the ``source`` dialect into the ``target`` dialect.

    >>> convert("1h30m", source="go", target="iso8601")
    'PT1H30M'
    >>> convert("P1W", source="iso8601", target="prometheus")
    '1w'
    """
    _check_dialect(target)
    return format_duration(parse_ns(text, dialect=source, reference=reference), dialect=target)


def _as_ns(value: int | timedelta) -> int:
    if isinstance(value, timedelta):
        return from_timedelta(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise DurationError(f"expected integer nanoseconds or a timedelta, got {value!r}")
    return value
