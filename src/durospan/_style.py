"""The shared vocabulary of output styles."""

from __future__ import annotations

from typing import Literal

# Output styles: "token" (1d 4h 30m), "compact" (1d4h30m), "clock" (HH:MM:SS).
Style = Literal["token", "clock", "compact"]
