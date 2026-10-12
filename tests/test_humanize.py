from __future__ import annotations

from datetime import timedelta

import pytest

import durospan

S = 1_000_000_000


def test_short_form_is_the_default() -> None:
    assert durospan.humanize(5400 * S) == "1h 30m"


def test_long_form_spells_units_and_plurals() -> None:
    assert durospan.humanize(3661 * S, long=True) == "1 hour, 1 minute, 1 second"


def test_timedelta_input_is_accepted() -> None:
    assert durospan.humanize(timedelta(days=8)) == "1w 1d"


def test_precision_keeps_the_most_significant_units() -> None:
    assert durospan.humanize(3725 * S, precision=2) == "1h 2m"


def test_precision_rounds_half_up_on_the_last_unit() -> None:
    assert durospan.humanize(90 * S, precision=1) == "2m"
    assert durospan.humanize(89 * S, precision=1) == "1m"


def test_rounding_carries_into_larger_units() -> None:
    assert durospan.humanize(3599 * S + S // 2, precision=2) == "1h"


def test_precision_does_not_round_twice() -> None:
    assert durospan.humanize(29 * 60 * S + 29_600_000_000, precision=1) == "29m"


def test_smallest_unit_rounds_the_rest() -> None:
    assert durospan.humanize(1_499_999_999) == "1s"
    assert durospan.humanize(1_500_000_000, smallest="ms") == "1s 500ms"


def test_largest_unit_absorbs_bigger_ones() -> None:
    assert durospan.humanize(3 * 86400 * S, largest="h") == "72h"


def test_zero_is_named_in_the_smallest_unit() -> None:
    assert durospan.humanize(0) == "0s"
    assert durospan.humanize(0, long=True, smallest="ms") == "0 milliseconds"


def test_values_below_the_smallest_unit_round_to_zero() -> None:
    assert durospan.humanize(400_000_000) == "0s"


def test_negative_values_keep_their_sign() -> None:
    assert durospan.humanize(-5400 * S) == "-1h 30m"


def test_sub_second_units_are_available() -> None:
    assert durospan.humanize(1_234_567, smallest="ns", long=True) == (
        "1 millisecond, 234 microseconds, 567 nanoseconds"
    )


@pytest.mark.parametrize(
    "kwargs",
    [{"precision": 0}, {"smallest": "y"}, {"largest": "ns", "smallest": "s"}],
)
def test_bad_options_are_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(durospan.DurationError):
        durospan.humanize(S, **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [1.5, "1s", True])
def test_non_integer_values_are_rejected(value: object) -> None:
    with pytest.raises(durospan.DurationError):
        durospan.humanize(value)  # type: ignore[arg-type]
