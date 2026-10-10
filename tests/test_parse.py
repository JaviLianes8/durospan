from datetime import timedelta

import pytest

import durospan


def test_parse_each_unit_on_its_own() -> None:
    assert durospan.parse("1w") == 604800
    assert durospan.parse("1d") == 86400
    assert durospan.parse("1h") == 3600
    assert durospan.parse("1m") == 60
    assert durospan.parse("1s") == 1


def test_parse_seconds_only() -> None:
    assert durospan.parse("90s") == 90


def test_parse_combined_tokens_with_mixed_spacing() -> None:
    assert durospan.parse("1d 4h30m") == 102600


def test_parse_is_order_independent() -> None:
    assert durospan.parse("30m 1h") == durospan.parse("1h 30m")


def test_parse_accepts_fractional_values() -> None:
    assert durospan.parse("1.5h") == 5400
    assert durospan.parse("90.5s") == 90.5


def test_parse_is_case_insensitive_on_units() -> None:
    assert durospan.parse("1H") == 3600


def test_parse_clock_hms() -> None:
    assert durospan.parse("28:30:00") == 102600


def test_parse_clock_ms() -> None:
    assert durospan.parse("01:30") == 90


def test_parse_clock_with_fraction() -> None:
    assert durospan.parse("00:01:30.5") == 90.5


def test_parse_timedelta_returns_a_timedelta() -> None:
    assert durospan.parse_timedelta("1h 30m") == timedelta(hours=1, minutes=30)


def test_parse_rejects_leading_and_trailing_whitespace_harmlessly() -> None:
    assert durospan.parse("  2h30m  ") == 9000


def test_parse_timedelta_overflow_becomes_a_duration_error() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_timedelta("999999999999d")
