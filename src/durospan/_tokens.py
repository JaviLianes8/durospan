"""A scanner for ``<number> <unit>`` sequences, shared by the systemd and human dialects."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from ._errors import AmbiguousDurationError, syntax_error
from ._numbers import SECOND, scaled

_TOKEN = re.compile(r"(\d+(?:\.\d+)?|\.\d+)[ \t]*([^\W\d_]+)?")
_SPACES = re.compile(r"\s*")
_HUMAN_SEP = re.compile(r"\s*(?:,\s*(?:and\s+)?|and\s+)?", re.IGNORECASE)


@dataclass(frozen=True)
class Grammar:
    """How a dialect spells its tokens: unit table and the rules around it."""

    name: str
    units: Mapping[str, int]
    case_sensitive: bool
    bare_seconds: bool
    repeats: bool
    words: bool
    ambiguous: frozenset[str] = frozenset()


def scan(text: str, grammar: Grammar, start: int = 0) -> int:
    """Sum the tokens in ``text[start:]`` and return the total in nanoseconds."""
    pos = len(text) - len(text[start:].lstrip()) if text[start:].strip() else len(text)
    if pos == len(text):
        raise syntax_error("expected a number", text, pos, "")
    total = 0
    seen: set[str] = set()
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None:
            raise syntax_error("expected a number", text, pos, _word_at(text, pos))
        number, unit = match.group(1), match.group(2)
        size, key = _unit_size(text, grammar, match, unit)
        if key in seen and not grammar.repeats:
            raise syntax_error(f"unit {unit!r} repeated", text, match.start(2), unit or "")
        seen.add(key)
        whole, _, frac = number.partition(".")
        total += scaled(whole, frac, size)
        pos = _skip_separator(text, match.end(), grammar)
    return total


def _unit_size(
    text: str, grammar: Grammar, match: re.Match[str], unit: str | None
) -> tuple[int, str]:
    if unit is None:
        if grammar.bare_seconds:
            return SECOND, "s"
        raise syntax_error("missing unit", text, match.start(1), match.group(1))
    key = unit if grammar.case_sensitive else unit.lower()
    if key in grammar.ambiguous:
        raise AmbiguousDurationError(
            f"{unit!r} has no fixed length in the {grammar.name} dialect"
            f" at position {match.start(2)} in {text!r}",
            text=text,
            position=match.start(2),
            token=unit,
        )
    size = grammar.units.get(key)
    if size is None:
        raise syntax_error(f"unknown unit {unit!r}", text, match.start(2), unit)
    return size, key


def _skip_separator(text: str, pos: int, grammar: Grammar) -> int:
    pattern = _HUMAN_SEP if grammar.words else _SPACES
    sep = pattern.match(text, pos)
    end = sep.end() if sep else pos
    if end == len(text) and text[pos:end].strip():
        raise syntax_error("dangling separator", text, pos, text[pos:end].strip())
    return end


def _word_at(text: str, pos: int) -> str:
    match = re.compile(r"\S+").match(text, pos)
    return match.group(0) if match else text[pos : pos + 1]


def unit_names(grammar: Grammar) -> list[str]:
    """Every fixed-length unit spelling, longest first, for building search patterns."""
    return sorted(grammar.units, key=len, reverse=True)
