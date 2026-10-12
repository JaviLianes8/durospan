"""The error types raised by the duration grammars."""

from __future__ import annotations


class DurationError(ValueError):
    """Raised when a duration string or value does not fit the grammar.

    Every error raised by ``durospan`` is a ``DurationError`` (and so a ``ValueError``).
    When the problem sits at a known place in the input, ``text`` holds the input,
    ``position`` the zero-based index of the offending character and ``token`` the
    offending piece of text; otherwise they are ``None``.
    """

    def __init__(
        self,
        message: str,
        *,
        text: str | None = None,
        position: int | None = None,
        token: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.text = text
        self.position = position
        self.token = token

    def explain(self) -> str:
        """Return the message, plus the input and a caret under the bad token if known.

        >>> import durospan
        >>> try:
        ...     durospan.parse_ns("1h 30x")
        ... except durospan.DurationError as exc:
        ...     print(exc.explain())
        unknown unit 'x' at position 5 in '1h 30x'
          1h 30x
               ^
        """
        if self.text is None or self.position is None:
            return self.message
        width = max(1, len(self.token or ""))
        return f"{self.message}\n  {self.text}\n  {' ' * self.position}{'^' * width}"


class DurationSyntaxError(DurationError):
    """The text does not follow the dialect's grammar (bad unit, junk, missing number)."""


class DurationRangeError(DurationError):
    """The value exists but cannot be held: overflow, input too long, or lost precision."""


class AmbiguousDurationError(DurationError):
    """The text uses years or months, whose length depends on a calendar date.

    Pass ``reference=`` (a ``datetime`` or ``date``) to resolve ISO 8601 years and months
    on the calendar; ``durospan`` never assumes a fixed length for them on its own.
    """


def syntax_error(message: str, text: str, position: int, token: str) -> DurationSyntaxError:
    """Build a syntax error whose message names the token and its position."""
    full = f"{message} at position {position} in {text!r}"
    return DurationSyntaxError(full, text=text, position=position, token=token)
