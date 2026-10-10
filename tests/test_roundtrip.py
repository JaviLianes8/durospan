import pytest

import durospan
from durospan._style import Style

_SECONDS = [0, 1, 59, 60, 90, 3600, 102600, 604800, 694861, 90.5, 5400.25]
_STYLES: list[Style] = ["token", "compact", "clock"]


@pytest.mark.parametrize("seconds", _SECONDS)
@pytest.mark.parametrize("style", _STYLES)
def test_parse_recovers_the_value_format_wrote(seconds: float, style: Style) -> None:
    assert durospan.parse(durospan.format(seconds, style=style)) == seconds


@pytest.mark.parametrize("seconds", _SECONDS)
@pytest.mark.parametrize("style", _STYLES)
def test_format_is_stable_across_a_round_trip(seconds: float, style: Style) -> None:
    rendered = durospan.format(seconds, style=style)
    assert durospan.format(durospan.parse(rendered), style=style) == rendered


@pytest.mark.parametrize("text", ["1d 4h30m", "2h30m", "90s", "1.5h", "28:30:00", "1d4h30m"])
def test_the_documented_inputs_round_trip(text: str) -> None:
    seconds = durospan.parse(text)
    assert durospan.parse(durospan.format(seconds)) == seconds
