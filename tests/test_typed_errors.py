from __future__ import annotations

from datetime import timedelta

import pytest

import durospan


def test_every_error_is_a_duration_error_and_a_value_error() -> None:
    for kind in (
        durospan.DurationSyntaxError,
        durospan.DurationRangeError,
        durospan.AmbiguousDurationError,
    ):
        assert issubclass(kind, durospan.DurationError)
        assert issubclass(kind, ValueError)


def test_syntax_errors_point_at_the_bad_token() -> None:
    with pytest.raises(durospan.DurationSyntaxError) as info:
        durospan.parse_ns("1h 30x")
    error = info.value
    assert (error.text, error.position, error.token) == ("1h 30x", 5, "x")
    assert error.explain().splitlines()[-1] == "       ^"


def test_go_unknown_unit_points_at_the_unit() -> None:
    with pytest.raises(durospan.DurationSyntaxError) as info:
        durospan.parse_ns("1h2d", dialect="go")
    assert (info.value.position, info.value.token) == (3, "d")


def test_ambiguous_errors_point_at_the_calendar_field() -> None:
    with pytest.raises(durospan.AmbiguousDurationError) as info:
        durospan.parse_ns("2 weeks 1 month")
    assert info.value.token == "month"


def test_errors_without_a_location_explain_with_the_message_only() -> None:
    error = durospan.DurationError("plain")
    assert error.explain() == "plain"
    assert error.position is None


def test_overlong_input_is_refused_before_parsing() -> None:
    with pytest.raises(durospan.DurationRangeError):
        durospan.parse_ns("1" * 5000 + "s", dialect="go")


def test_human_values_beyond_timedelta_are_refused() -> None:
    with pytest.raises(durospan.DurationRangeError):
        durospan.parse_ns("9999999999 weeks")


def test_go_formatting_refuses_values_outside_int64() -> None:
    with pytest.raises(durospan.DurationRangeError):
        durospan.format_duration(1 << 63, dialect="go")


def test_systemd_and_prometheus_refuse_negative_values() -> None:
    for dialect in ("systemd", "prometheus"):
        with pytest.raises(durospan.DurationRangeError):
            durospan.format_duration(-1, dialect=dialect)


def test_prometheus_refuses_sub_millisecond_values() -> None:
    with pytest.raises(durospan.DurationRangeError):
        durospan.format_duration(1, dialect="prometheus")


def test_unknown_dialect_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_ns("1s", dialect="java")  # type: ignore[arg-type]


def test_non_text_input_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_ns(5)  # type: ignore[arg-type]


def test_empty_text_is_a_syntax_error_in_every_dialect() -> None:
    for dialect in durospan.DIALECTS:
        with pytest.raises(durospan.DurationSyntaxError):
            durospan.parse_ns("", dialect=dialect)


def test_timedelta_refuses_to_drop_nanoseconds() -> None:
    with pytest.raises(durospan.DurationRangeError):
        durospan.parse_timedelta("1500ns", dialect="go")
    assert durospan.parse_timedelta("1500us", dialect="go") == timedelta(microseconds=1500)


def test_format_duration_rejects_floats_and_bools() -> None:
    for value in (1.5, True):
        with pytest.raises(durospan.DurationError):
            durospan.format_duration(value)  # type: ignore[arg-type]
