"""Go's ``time.ParseDuration`` and ``Duration.String``, reproduced exactly.

The parser follows ``src/time/format.go`` step by step, including its uint64 overflow
checks and the float64 step it uses for fractions (``0.3333333333333333333h`` is exactly
``20m`` in Go, so it is here too). Units are case-sensitive.
"""

from __future__ import annotations

from ._errors import DurationRangeError, DurationSyntaxError
from ._numbers import HOUR, MINUTE, MS, NS, SECOND, US, frac_digits

UNITS: dict[str, int] = {
    "ns": NS,
    "us": US,
    "µs": US,  # MICRO SIGN
    "μs": US,  # GREEK SMALL LETTER MU
    "ms": MS,
    "s": SECOND,
    "m": MINUTE,
    "h": HOUR,
}

_TOP = 1 << 63
_MASK = (1 << 64) - 1


def _invalid(text: str, position: int = 0, token: str = "") -> DurationSyntaxError:
    return DurationSyntaxError(
        f"invalid duration {text!r}", text=text, position=position, token=token or text
    )


def _overflow(text: str) -> DurationRangeError:
    return DurationRangeError(f"invalid duration {text!r}: out of int64 range", text=text)


def _leading_int(s: str, i: int) -> tuple[int, int, bool]:
    value = 0
    while i < len(s) and "0" <= s[i] <= "9":
        if value > _TOP // 10:
            return value, i, True
        value = value * 10 + ord(s[i]) - 48
        if value > _TOP:
            return value, i, True
        i += 1
    return value, i, False


def _leading_fraction(s: str, i: int) -> tuple[int, float, int]:
    value, scale, overflow = 0, 1.0, False
    while i < len(s) and "0" <= s[i] <= "9":
        if not overflow:
            nxt = value * 10 + ord(s[i]) - 48
            if value > (_TOP - 1) // 10 or nxt > _TOP:
                overflow = True
            else:
                value, scale = nxt, scale * 10
        i += 1
    return value, scale, i


def parse(text: str) -> int:
    """Parse Go duration text into integer nanoseconds, with Go's exact semantics."""
    s, i, negative = text, 0, False
    if s and s[0] in "+-":
        negative, i = s[0] == "-", 1
    if s[i:] == "0":
        return 0
    if i == len(s):
        raise _invalid(text)
    total = 0
    while i < len(s):
        start = i
        if not (s[i] == "." or "0" <= s[i] <= "9"):
            raise _invalid(text, i, s[i])
        whole, i, overflow = _leading_int(s, i)
        if overflow:
            raise _overflow(text)
        pre = i != start
        fraction, scale, post = 0, 1.0, False
        if i < len(s) and s[i] == ".":
            mark = i + 1
            fraction, scale, i = _leading_fraction(s, mark)
            post = i != mark
        if not pre and not post:
            raise _invalid(text, start, s[start:i] or s[start])
        unit_start = i
        while i < len(s) and not (s[i] == "." or "0" <= s[i] <= "9"):
            i += 1
        symbol = s[unit_start:i]
        if not symbol:
            raise DurationSyntaxError(
                f"missing unit in duration {text!r}", text=text, position=start, token=s[start:i]
            )
        unit = UNITS.get(symbol)
        if unit is None:
            raise DurationSyntaxError(
                f"unknown unit {symbol!r} in duration {text!r}",
                text=text,
                position=unit_start,
                token=symbol,
            )
        if whole > _TOP // unit:
            raise _overflow(text)
        whole *= unit
        if fraction > 0:
            whole += int(float(fraction) * (float(unit) / scale))
            if whole > _TOP:
                raise _overflow(text)
        # Go adds in uint64, so 2**63 + 2**63 wraps to 0 and is accepted there too.
        total = (total + whole) & _MASK
        if total > _TOP:
            raise _overflow(text)
    if negative:
        return -total
    if total > _TOP - 1:
        raise _overflow(text)
    return total


def format(ns: int) -> str:
    """Render nanoseconds the way Go's ``Duration.String`` does (``1h0m0s``, ``1.5ms``)."""
    if ns == 0:
        return "0s"
    sign = "-" if ns < 0 else ""
    u = abs(ns)
    if u < SECOND:
        if u < US:
            return f"{sign}{u}ns"
        if u < MS:
            return f"{sign}{u // US}{frac_digits(u % US, 3)}µs"
        return f"{sign}{u // MS}{frac_digits(u % MS, 6)}ms"
    seconds, rest = divmod(u, SECOND)
    text = f"{seconds % 60}{frac_digits(rest, 9)}s"
    minutes = seconds // 60
    if minutes:
        text = f"{minutes % 60}m{text}"
        hours = minutes // 60
        if hours:
            text = f"{hours}h{text}"
    return sign + text
