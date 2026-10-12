from __future__ import annotations

from datetime import date

import durospan

S = 1_000_000_000


def _texts(text: str, dialect: durospan.Dialect = "human") -> list[str]:
    return [match.text for match in durospan.find_durations(text, dialect=dialect)]


def test_human_durations_are_found_with_spans_and_values() -> None:
    text = "retry in 5 minutes, give up after 2 h 30 min"
    first, second = durospan.find_durations(text)
    assert (first.start, first.end, first.ns) == (9, 18, 300 * S)
    assert text[second.start : second.end] == "2 h 30 min"
    assert second.ns == 9000 * S


def test_human_lists_with_and_are_one_duration() -> None:
    assert _texts("wait 1 hour, 30 minutes and 5 seconds please") == [
        "1 hour, 30 minutes and 5 seconds"
    ]


def test_ambiguous_units_end_a_match_instead_of_being_guessed() -> None:
    assert _texts("2 h 30 min and 1 month") == ["2 h 30 min"]


def test_clock_text_is_not_reported() -> None:
    assert _texts("meet at 10:30") == []


def test_words_that_start_like_units_are_not_matches() -> None:
    assert _texts("5 mice and 3 hats") == []


def test_go_durations_are_found() -> None:
    assert _texts("timeout: 1h30m, interval=-5s, x5s 3d", "go") == ["1h30m", "-5s"]


def test_prometheus_candidates_that_fail_the_grammar_are_skipped() -> None:
    assert _texts("scrape 15s; keep 2w3d; bad 1h1h", "prometheus") == ["15s", "2w3d"]


def test_iso_calendar_spans_need_a_reference() -> None:
    text = "a PT1H30M b P1M c -P2D"
    assert _texts(text, "iso8601") == ["PT1H30M", "-P2D"]
    found = durospan.find_durations(text, dialect="iso8601", reference=date(2024, 2, 1))
    assert [match.text for match in found] == ["PT1H30M", "P1M", "-P2D"]


def test_systemd_spans_are_found() -> None:
    assert _texts("RestartSec=5min 20s TimeoutSec=90", "systemd") == ["5min 20s"]


def test_nothing_found_is_an_empty_list() -> None:
    assert durospan.find_durations("no durations here") == []
