"""ISO 8601 durations: ``PnYnMnDTnHnMnS`` and ``PnW``.

Days, hours, minutes and seconds have fixed lengths (a day is 24 hours, as in
XML Schema ``xs:duration`` arithmetic without time zones). Years and months do not, so
they are only accepted with a ``reference`` date and are then resolved on the calendar.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime

from ._errors import AmbiguousDurationError, DurationRangeError, DurationSyntaxError, syntax_error
from ._numbers import DAY, HOUR, MINUTE, SECOND, WEEK, frac_digits, scaled

Reference = date | datetime

_NUM = r"([0-9]+(?:[.,][0-9]+)?)"
_SHAPE = re.compile(
    rf"(?P<sign>[-+]?)P(?:(?P<W>{_NUM})W|(?:(?P<Y>{_NUM})Y)?(?:(?P<M>{_NUM})M)?(?:(?P<D>{_NUM})D)?"
    rf"(?:T(?:(?P<h>{_NUM})H)?(?:(?P<m>{_NUM})M)?(?:(?P<s>{_NUM})S)?)?)"
)
_FIXED = {"W": WEEK, "D": DAY, "h": HOUR, "m": MINUTE, "s": SECOND}
_ORDER = ("W", "Y", "M", "D", "h", "m", "s")


def _bad(text: str, message: str = "invalid ISO 8601 duration") -> DurationSyntaxError:
    return DurationSyntaxError(f"{message}: {text!r}", text=text, position=0, token=text)


def parse(text: str, reference: Reference | None = None) -> int:
    """Parse an ISO 8601 duration into integer nanoseconds."""
    match = _SHAPE.fullmatch(text)
    if match is None:
        raise _locate(text)
    fields = {key: match.group(key) for key in _ORDER if match.group(key) is not None}
    if not fields:
        raise _bad(text, "ISO 8601 duration has no fields")
    if text.endswith("T"):
        raise syntax_error("'T' with no time fields after it", text, len(text) - 1, "T")
    present = [key for key in _ORDER if key in fields]
    for key in present[:-1]:
        if any(c in fields[key] for c in ".,"):
            position = match.start(key)
            raise syntax_error(
                "only the last ISO 8601 field may have a fraction", text, position, fields[key]
            )
    sign = -1 if match.group("sign") == "-" else 1
    total = 0
    for key in ("W", "D", "h", "m", "s"):
        if key in fields:
            whole, _, frac = fields[key].replace(",", ".").partition(".")
            total += scaled(whole, frac, _FIXED[key])
    if "Y" in fields or "M" in fields:
        total += _calendar_part(text, match, fields, sign, reference)
    return sign * total


def _calendar_part(
    text: str,
    match: re.Match[str],
    fields: dict[str, str],
    sign: int,
    reference: Reference | None,
) -> int:
    for key in ("Y", "M"):
        if key in fields and not fields[key].isdigit():
            raise syntax_error(
                "fractional years or months have no exact length",
                text,
                match.start(key),
                fields[key],
            )
    if reference is None:
        key = "Y" if "Y" in fields else "M"
        token = fields[key] + key
        raise AmbiguousDurationError(
            f"years and months have no fixed length; pass reference= to resolve {text!r}",
            text=text,
            position=match.start(key),
            token=token,
        )
    months = int(fields.get("Y", "0")) * 12 + int(fields.get("M", "0"))
    start = reference.date() if isinstance(reference, datetime) else reference
    end = add_months(start, sign * months)
    return sign * (end - start).days * DAY


def add_months(day: date, months: int) -> date:
    """Move ``day`` by whole calendar months, clamping to the last day of the month."""
    index = day.year * 12 + day.month - 1 + months
    year, month = divmod(index, 12)
    if not 1 <= year <= 9999:
        raise DurationRangeError(f"calendar arithmetic leaves the year range: {year}")
    last = calendar.monthrange(year, month + 1)[1]
    return date(year, month + 1, min(day.day, last))


def _locate(text: str) -> DurationSyntaxError:
    body = text.lstrip("+-")
    offset = len(text) - len(body)
    if not body.startswith("P"):
        return syntax_error("ISO 8601 duration must start with 'P'", text, offset, body[:1] or text)
    if "W" in body and len(body) > body.index("W") + 1:
        return syntax_error("weeks cannot be combined with other fields", text, offset, body)
    head, _, tail = body.partition("T")
    for i, char in enumerate(head):
        if char in "HS":
            return syntax_error(f"'{char}' belongs after 'T'", text, offset + i, char)
    for i, char in enumerate(tail):
        if char in "YWD":
            return syntax_error(
                f"'{char}' belongs before 'T'", text, offset + len(head) + 1 + i, char
            )
    return _bad(text)


def format(ns: int) -> str:
    """Render nanoseconds as ``[-]PnDTnHnMnS`` (days are exact 24 hour days)."""
    if ns == 0:
        return "PT0S"
    sign = "-" if ns < 0 else ""
    days, rest = divmod(abs(ns), DAY)
    hours, rest = divmod(rest, HOUR)
    minutes, rest = divmod(rest, MINUTE)
    seconds, nanos = divmod(rest, SECOND)
    out = f"{sign}P{days}D" if days else f"{sign}P"
    time = ""
    if hours:
        time += f"{hours}H"
    if minutes:
        time += f"{minutes}M"
    if seconds or nanos:
        time += f"{seconds}{frac_digits(nanos, 9)}S"
    return out + ("T" + time if time else "")
