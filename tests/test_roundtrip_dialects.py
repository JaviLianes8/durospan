"""Seeded property tests: every dialect gives back exactly the value it wrote."""

from __future__ import annotations

import random
from collections.abc import Callable

import pytest

import durospan

SEED = 20261012
SAMPLES = 400

_MAGNITUDES = (10**3, 10**6, 10**9, 10**12, 10**15, 10**18)


def _any_ns(rng: random.Random) -> int:
    return rng.randrange(-_MAGNITUDES[-1], _MAGNITUDES[-1]) // rng.choice(_MAGNITUDES)


def _go_ns(rng: random.Random) -> int:
    edge = rng.random() < 0.05
    return rng.choice([(1 << 63) - 1, -(1 << 63)]) if edge else _any_ns(rng) * rng.randrange(1, 9)


def _non_negative(rng: random.Random) -> int:
    return abs(_any_ns(rng))


def _milliseconds(rng: random.Random) -> int:
    return abs(_any_ns(rng)) // 10**6 * 10**6


GENERATORS: dict[durospan.Dialect, Callable[[random.Random], int]] = {
    "go": _go_ns,
    "iso8601": _any_ns,
    "human": _any_ns,
    "systemd": _non_negative,
    "prometheus": _milliseconds,
}


@pytest.mark.parametrize("dialect", list(GENERATORS))
def test_parse_inverts_format_exactly(dialect: durospan.Dialect) -> None:
    rng = random.Random(f"{SEED}-{dialect}")
    for _ in range(SAMPLES):
        ns = GENERATORS[dialect](rng)
        text = durospan.format_duration(ns, dialect=dialect)
        assert durospan.parse_ns(text, dialect=dialect) == ns, text


@pytest.mark.parametrize("dialect", list(GENERATORS))
def test_format_is_a_fixed_point(dialect: durospan.Dialect) -> None:
    rng = random.Random(f"{SEED}-fixed-{dialect}")
    for _ in range(SAMPLES):
        text = durospan.format_duration(GENERATORS[dialect](rng), dialect=dialect)
        again = durospan.format_duration(durospan.parse_ns(text, dialect=dialect), dialect=dialect)
        assert again == text


@pytest.mark.parametrize("source", list(GENERATORS))
@pytest.mark.parametrize("target", ["go", "iso8601", "human"])
def test_convert_preserves_the_value(source: durospan.Dialect, target: durospan.Dialect) -> None:
    rng = random.Random(f"{SEED}-{source}-{target}")
    for _ in range(SAMPLES // 4):
        ns = GENERATORS[source](rng)
        text = durospan.format_duration(ns, dialect=source)
        converted = durospan.convert(text, source=source, target=target)
        assert durospan.parse_ns(converted, dialect=target) == ns
