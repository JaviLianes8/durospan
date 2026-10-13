"""The complete promise, checked against golden vectors for each dialect (see tests/golden_*.py)."""

from __future__ import annotations

from datetime import date

import golden_go
import golden_iso
import golden_prometheus
import golden_systemd
import pytest

import durospan


@pytest.mark.parametrize(("text", "ns"), golden_go.PARSE)
def test_go_parse_follows_parse_duration(text: str, ns: int) -> None:
    assert durospan.parse_ns(text, dialect="go") == ns


@pytest.mark.parametrize("text", golden_go.ERRORS)
def test_go_rejects_what_go_rejects(text: str) -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_ns(text, dialect="go")


@pytest.mark.parametrize(("ns", "text"), golden_go.FORMAT)
def test_go_format_follows_duration_string(ns: int, text: str) -> None:
    assert durospan.format_duration(ns, dialect="go") == text
    assert durospan.parse_ns(text, dialect="go") == ns


@pytest.mark.parametrize(("text", "ns"), golden_iso.FIXED)
def test_iso_fixed_length_durations(text: str, ns: int) -> None:
    assert durospan.parse_ns(text, dialect="iso8601") == ns


@pytest.mark.parametrize(("text", "reference", "ns"), golden_iso.CALENDAR)
def test_iso_calendar_durations_with_a_reference(text: str, reference: date, ns: int) -> None:
    assert durospan.parse_ns(text, dialect="iso8601", reference=reference) == ns


@pytest.mark.parametrize("text", golden_iso.AMBIGUOUS)
def test_iso_years_and_months_never_get_a_guessed_length(text: str) -> None:
    with pytest.raises(durospan.AmbiguousDurationError) as info:
        durospan.parse_ns(text, dialect="iso8601")
    assert info.value.position is not None


@pytest.mark.parametrize("text", golden_iso.ERRORS)
def test_iso_rejects_malformed_text(text: str) -> None:
    with pytest.raises(durospan.DurationSyntaxError):
        durospan.parse_ns(text, dialect="iso8601", reference=date(2000, 1, 1))


@pytest.mark.parametrize(("ns", "text"), golden_iso.FORMAT)
def test_iso_format(ns: int, text: str) -> None:
    assert durospan.format_duration(ns, dialect="iso8601") == text


@pytest.mark.parametrize(("text", "ns"), golden_systemd.PARSE)
def test_systemd_parse_matches_the_man_page(text: str, ns: int) -> None:
    assert durospan.parse_ns(text, dialect="systemd") == ns


@pytest.mark.parametrize("text", golden_systemd.ERRORS)
def test_systemd_rejects_malformed_text(text: str) -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_ns(text, dialect="systemd")


@pytest.mark.parametrize(("ns", "text"), golden_systemd.FORMAT)
def test_systemd_format_matches_format_timespan(ns: int, text: str) -> None:
    assert durospan.format_duration(ns, dialect="systemd") == text


@pytest.mark.parametrize(("text", "ns", "canonical"), golden_prometheus.PARSE)
def test_prometheus_parse_and_string(text: str, ns: int, canonical: str) -> None:
    assert durospan.parse_ns(text, dialect="prometheus") == ns
    rendered = durospan.format_duration(ns, dialect="prometheus")
    if canonical:
        assert rendered == canonical
    assert durospan.parse_ns(rendered, dialect="prometheus") == ns


@pytest.mark.parametrize("text", golden_prometheus.ERRORS)
def test_prometheus_rejects_what_prometheus_rejects(text: str) -> None:
    with pytest.raises(durospan.DurationError):
        durospan.parse_ns(text, dialect="prometheus")


@pytest.mark.parametrize(
    ("text", "dialect", "ns"),
    [
        ("1 hour, 30 minutes", "human", 5_400 * golden_go.S),
        ("2 hours and 5 minutes", "human", 7_500 * golden_go.S),
        ("-1h30m", "human", -5_400 * golden_go.S),
        ("1:30:00.25", "human", 5_400_250 * golden_go.MS),
        ("1 week 2 days", "human", 9 * golden_iso.D),
        ("250 ms", "human", 250 * golden_go.MS),
    ],
)
def test_human_reads_what_people_type(text: str, dialect: durospan.Dialect, ns: int) -> None:
    assert durospan.parse_ns(text, dialect=dialect) == ns


def test_go_uint64_wraparound_is_reproduced() -> None:
    # Go sums tokens in uint64: 2**63 + 2**63 wraps to 0 and ParseDuration returns 0.
    assert durospan.parse_ns("9223372036854775808ns9223372036854775808ns", dialect="go") == 0
