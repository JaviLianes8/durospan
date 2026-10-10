from datetime import timedelta

import durospan


def test_token_style_is_the_default() -> None:
    assert durospan.format(102600) == "1d 4h 30m"


def test_token_style_skips_zero_units() -> None:
    assert durospan.format(3600) == "1h"


def test_zero_renders_as_zero_seconds() -> None:
    assert durospan.format(0) == "0s"


def test_compact_style_drops_the_spaces() -> None:
    assert durospan.format(102600, style="compact") == "1d4h30m"


def test_clock_style_rolls_days_into_hours() -> None:
    assert durospan.format(102600, style="clock") == "28:30:00"


def test_clock_style_pads_small_durations() -> None:
    assert durospan.format(90, style="clock") == "00:01:30"


def test_clock_style_keeps_fractional_seconds() -> None:
    assert durospan.format(90.5, style="clock") == "00:01:30.5"


def test_fractional_seconds_in_token_style() -> None:
    assert durospan.format(90.5) == "1m 30.5s"


def test_weeks_are_used_in_the_decomposition() -> None:
    assert durospan.format(604800) == "1w"


def test_format_timedelta_matches_format() -> None:
    assert durospan.format_timedelta(timedelta(hours=1, minutes=30)) == "1h 30m"
