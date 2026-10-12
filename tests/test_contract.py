import importlib.resources
import re
from pathlib import Path

import durospan

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "DIALECTS",
    "AmbiguousDurationError",
    "Dialect",
    "DurationError",
    "DurationMatch",
    "DurationRangeError",
    "DurationSyntaxError",
    "Style",
    "Unit",
    "convert",
    "find_durations",
    "format",
    "format_duration",
    "format_timedelta",
    "humanize",
    "parse",
    "parse_ns",
    "parse_seconds",
    "parse_timedelta",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(durospan.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in durospan.__all__:
        assert hasattr(durospan, name)


def test_version_is_a_three_part_string() -> None:
    parts = durospan.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("durospan").joinpath("py.typed").is_file()


def _pyproject() -> str:
    return (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")


def test_version_matches_the_package_metadata() -> None:
    match = re.search(r'^version = "([^"]+)"', _pyproject(), re.MULTILINE)
    assert match is not None
    assert match.group(1) == durospan.__version__


def test_the_command_line_entry_point_is_declared() -> None:
    assert 'durospan = "durospan._cli:main"' in _pyproject()


def test_every_dialect_parses_what_it_formats_at_the_edges() -> None:
    edges: dict[durospan.Dialect, list[int]] = {
        "go": [0, 1, -1, (1 << 63) - 1, -(1 << 63)],
        "iso8601": [0, 1, -1, 10**22],
        "human": [0, 1, -1, 10**22],
        "systemd": [0, 1, 10**22],
        "prometheus": [0, 10**6, ((1 << 63) - 1) // 10**6 * 10**6],
    }
    for dialect, values in edges.items():
        for ns in values:
            text = durospan.format_duration(ns, dialect=dialect)
            assert durospan.parse_ns(text, dialect=dialect) == ns
