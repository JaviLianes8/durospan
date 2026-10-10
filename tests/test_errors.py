import math

import pytest

import durospan


def test_empty_string_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("   ")


def test_bad_token_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("1x")


def test_garbage_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("abc")


def test_trailing_junk_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("1h junk")


def test_repeated_unit_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("1h 2h")


def test_negative_token_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("-5m")


def test_malformed_clock_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("1:2:3:4")


def test_clock_with_a_non_numeric_field_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse("aa:bb")


def test_formatting_a_negative_value_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.format(-1)


def test_formatting_a_non_finite_value_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.format(math.inf)


def test_unknown_style_is_rejected() -> None:
    with pytest.raises(durospan.DurationError):
        durospan.format(60, style="fancy")  # type: ignore[arg-type]
