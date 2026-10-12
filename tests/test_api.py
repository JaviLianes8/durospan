from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import durospan

S = 1_000_000_000


def test_parse_ns_defaults_to_the_human_dialect() -> None:
    assert durospan.parse_ns("1 hour, 30 minutes") == 5400 * S


def test_parse_ns_keeps_values_a_float_cannot_hold() -> None:
    assert durospan.parse_ns("9007199254740993ns", dialect="go") == 2**53 + 1


def test_parse_seconds_is_an_exact_decimal() -> None:
    assert durospan.parse_seconds("0.1s") == Decimal("0.1")
    assert durospan.parse_seconds("1ns", dialect="go") == Decimal("1E-9")


def test_sub_nanosecond_fractions_truncate_toward_zero() -> None:
    assert durospan.parse_ns("0.0000000019s") == 1
    assert durospan.parse_ns("-0.0000000019s") == -1


def test_parse_timedelta_with_a_dialect() -> None:
    assert durospan.parse_timedelta("P1DT2H", dialect="iso8601") == timedelta(days=1, hours=2)


def test_parse_timedelta_without_a_dialect_keeps_the_original_grammar() -> None:
    assert durospan.parse_timedelta("28:30:00") == timedelta(hours=28, minutes=30)


def test_datetime_references_use_their_calendar_date() -> None:
    reference = datetime(2024, 1, 31, 23, 59)
    assert durospan.parse_ns("P1M", dialect="iso8601", reference=reference) == 29 * 86400 * S


def test_format_duration_accepts_a_timedelta() -> None:
    assert durospan.format_duration(timedelta(minutes=90), dialect="go") == "1h30m0s"


def test_format_duration_defaults_to_the_human_dialect() -> None:
    assert durospan.format_duration(90_500_000_000) == "1m 30s 500ms"


def test_convert_between_dialects() -> None:
    assert durospan.convert("2h45m30.5s", source="go", target="iso8601") == "PT2H45M30.5S"
    assert durospan.convert("2 h 30 min", source="systemd", target="prometheus") == "2h30m"
    assert durospan.convert("PT36H", source="iso8601", target="systemd") == "1d 12h"


def test_convert_resolves_calendar_units_with_a_reference() -> None:
    converted = durospan.convert(
        "P1M", source="iso8601", target="human", reference=date(2023, 2, 1)
    )
    assert converted == "4w"


def test_dialects_lists_every_dialect() -> None:
    assert set(durospan.DIALECTS) == {"human", "go", "iso8601", "systemd", "prometheus"}


def test_the_original_float_api_is_unchanged() -> None:
    assert durospan.parse("1d 4h30m") == 102600.0
    assert durospan.format(102600) == "1d 4h 30m"
