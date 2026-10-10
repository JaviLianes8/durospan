"""The one unit table that both parsing and formatting read from."""

from __future__ import annotations

# Largest first: this order drives decomposition on the way out and is the set of
# symbols accepted on the way in. Keeping it in a single place is what makes the
# round-trip share a grammar instead of duplicating one.
UNITS: tuple[tuple[str, int], ...] = (
    ("w", 604800),
    ("d", 86400),
    ("h", 3600),
    ("m", 60),
    ("s", 1),
)

SECONDS_BY_UNIT: dict[str, int] = {symbol: size for symbol, size in UNITS}
