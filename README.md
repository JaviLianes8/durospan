# durospan

Typed, zero-dependency round-trip between human durations and seconds, one grammar both ways.

## Install

```
pip install durospan
```

## Usage

```python
import durospan

# Parse human text into seconds (a float) or a timedelta.
durospan.parse("1d 4h30m")        # 102600.0
durospan.parse("2h30m")           # 9000.0
durospan.parse("90s")             # 90.0
durospan.parse("1.5h")            # 5400.0
durospan.parse("28:30:00")        # 102600.0  (clock input is accepted too)
durospan.parse_timedelta("1h 30m")  # datetime.timedelta(seconds=5400)

# Format seconds (or a timedelta) back, in the same grammar.
durospan.format(102600)                    # "1d 4h 30m"   (default token style)
durospan.format(102600, style="compact")   # "1d4h30m"
durospan.format(102600, style="clock")     # "28:30:00"
durospan.format(90.5, style="clock")       # "00:01:30.5"
durospan.format_timedelta(td, style="clock")

# The two directions share one grammar, so the trip is lossless:
durospan.parse(durospan.format(seconds)) == seconds
```

Bad input raises `durospan.DurationError` (a `ValueError`): unknown units, repeated
units, trailing junk, negatives and non-finite values are all rejected.

## Why

Python makes you choose one direction or a kitchen sink:

- `pytimeparse` parses `"1h30m"` into seconds but cannot format a number back.
- `humanize` formats a number into prose but cannot parse it back.
- `humanfriendly` does both, but it is a broad grab-bag of terminal helpers whose last
  release was in 2021 and which is not typed.
- `pydura` does both with nanosecond precision, but it requires Python 3.14+.

`durospan` is the small, focused piece in the middle: one shared unit table drives both
the parser and the formatter, so a value survives the round trip, and it is fully typed,
`py.typed`, zero-dependency and runs on Python 3.10+. Three output styles cover the common
shapes: `token` (`1d 4h 30m`), `compact` (`1d4h30m`) and `clock` (`HH:MM:SS`), and clock
text is accepted on input as well.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
