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
durospan.parse("1d 4h30m")  # 102600.0
durospan.parse("2h30m")  # 9000.0
durospan.parse("90s")  # 90.0
durospan.parse("1.5h")  # 5400.0
durospan.parse("28:30:00")  # 102600.0  (clock input is accepted too)
durospan.parse_timedelta("1h 30m")  # datetime.timedelta(seconds=5400)

# Format seconds (or a timedelta) back, in the same grammar.
durospan.format(102600)  # "1d 4h 30m"   (default token style)
durospan.format(102600, style="compact")  # "1d4h30m"
durospan.format(102600, style="clock")  # "28:30:00"
durospan.format(90.5, style="clock")  # "00:01:30.5"
durospan.format_timedelta(td, style="clock")

# The two directions share one grammar, so the trip is lossless:
durospan.parse(durospan.format(seconds)) == seconds
```

Bad input raises `durospan.DurationError` (a `ValueError`): unknown units, repeated
units, trailing junk, negatives and non-finite values are all rejected.

## Real formats, exactly

`durospan` also reads and writes the duration formats other tools use, exactly, through
integer nanoseconds:

```python
from datetime import date
import durospan

durospan.parse_ns("1h30m", dialect="go")  # 5400000000000
durospan.parse_ns("-2562047h47m16.854775808s", dialect="go")  # -9223372036854775808
durospan.parse_ns("PT1H30M", dialect="iso8601")  # 5400000000000
durospan.parse_ns("2 h 30 min", dialect="systemd")  # 9000000000000
durospan.parse_ns("1w2d", dialect="prometheus")  # 777600000000000
durospan.parse_ns("1 hour, 30 minutes")  # 5400000000000 (human, the default)
durospan.parse_seconds("300ms", dialect="go")  # Decimal('0.300000000')

durospan.format_duration(5_400_000_000_000, dialect="go")  # '1h30m0s'
durospan.convert("2h45m30.5s", source="go", target="iso8601")  # 'PT2H45M30.5S'

# ISO years and months have no fixed length: give a date or get an error, never a guess.
durospan.parse_ns("P1M", dialect="iso8601", reference=date(2024, 1, 31))  # 29 days

durospan.humanize(3725 * 10**9, precision=2)  # '1h 2m'
durospan.humanize(3725 * 10**9, long=True)  # '1 hour, 2 minutes, 5 seconds'

durospan.find_durations("retry in 5 minutes, give up after 2 h 30 min")
# [DurationMatch(start=9, end=18, text='5 minutes', ns=300000000000), ...]
```

Dialects: `human`, `go` (`time.ParseDuration` and `Duration.String`, bit for bit),
`iso8601`, `systemd` (`systemd.time(7)`) and `prometheus` (`model.ParseDuration`). Errors
are typed (`DurationSyntaxError`, `DurationRangeError`, `AmbiguousDurationError`) and
carry the position of the bad token; `explain()` draws a caret under it.

## Command line

```
durospan parse 1h30m --dialect go                    # 5400000000000
durospan convert "2 h 30 min" --from systemd --to prometheus   # 2h30m
durospan humanize 5400s --long                       # 1 hour, 30 minutes
durospan find app.log --dialect go
```

See [GUIDE.md](GUIDE.md) for every dialect, the exactness rules and the sources the test
vectors come from.

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
text is accepted on input as well. On top of that it speaks the formats that Go,
ISO 8601, systemd and Prometheus emit, exactly, so a value can move between a Go config,
a systemd unit and a Prometheus rule without drifting.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
