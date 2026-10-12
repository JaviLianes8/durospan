"""Locate durations inside free text, one candidate pattern per dialect."""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import _human, _systemd
from ._api import Dialect, _check_dialect, parse_ns
from ._errors import DurationError
from ._iso import Reference
from ._tokens import Grammar, unit_names


@dataclass(frozen=True)
class DurationMatch:
    """A duration found in text: its ``[start, end)`` span, the matched text and its value."""

    start: int
    end: int
    text: str
    ns: int


_NUMBER = r"(?:\d+(?:\.\d+)?|\.\d+)"
_LEFT = r"(?<![\w.])"
_RIGHT = r"(?![\w.])"


def _token_pattern(grammar: Grammar, separator: str, flags: int) -> re.Pattern[str]:
    units = "|".join(re.escape(name) for name in unit_names(grammar))
    token = rf"{_NUMBER}[ \t]*(?:{units})(?![^\W\d_])"
    sign = r"(?:(?<![^\s(])[-+])?" if grammar.words else ""
    return re.compile(rf"{_LEFT}{sign}{token}(?:{separator}{token})*{_RIGHT}", flags)


_PATTERNS: dict[str, re.Pattern[str]] = {
    "go": re.compile(
        rf"(?<![\w.+-])[-+]?(?:(?:\d+(?:\.\d*)?|\.\d+)(?:ns|us|µs|μs|ms|h|m|s))+{_RIGHT}"
    ),
    "prometheus": re.compile(rf"{_LEFT}(?:\d+(?:ms|y|w|d|h|m|s))+{_RIGHT}"),
    "iso8601": re.compile(rf"(?<![\w.+-])[-+]?P(?:T|\d+(?:[.,]\d+)?[YMWDHS])+{_RIGHT}"),
    "systemd": _token_pattern(_systemd.GRAMMAR, r"[ \t]*", 0),
    "human": _token_pattern(
        _human.GRAMMAR, r"(?:\s*,\s*(?:and\s+)?|\s+and\s+|[ \t]*)", re.IGNORECASE
    ),
}


def find_durations(
    text: str, *, dialect: Dialect = "human", reference: Reference | None = None
) -> list[DurationMatch]:
    """Return every valid ``dialect`` duration in ``text``, left to right.

    Candidates that look like a duration but fail the full parser (a repeated unit, an
    ambiguous month without ``reference``) are skipped rather than guessed. Clock text
    such as ``10:30`` is not reported, since in prose it is usually a time of day.

    >>> [m.text for m in find_durations("retry in 5 minutes, give up after 2 h 30 min")]
    ['5 minutes', '2 h 30 min']
    >>> find_durations("timeout=1m30s", dialect="go")[0].ns
    90000000000
    """
    _check_dialect(dialect)
    found = []
    for match in _PATTERNS[dialect].finditer(text):
        candidate = match.group(0)
        try:
            ns = parse_ns(candidate, dialect=dialect, reference=reference)
        except DurationError:
            continue
        found.append(DurationMatch(match.start(), match.end(), candidate, ns))
    return found
