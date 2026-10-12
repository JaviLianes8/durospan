# durospan guide

This guide explains the dialects, the exactness rules and the choices behind them. The
README has the short tour.

## The model: integer nanoseconds

Every dialect parses into an exact `int` count of nanoseconds and formats from one.
Nothing goes through `float`, so `9007199254740993ns` (2**53 + 1) and `0.1s` come back
exactly. Use:

- `parse_ns(text, dialect=...)` for the exact integer,
- `parse_seconds(text, dialect=...)` for an exact `Decimal` of seconds,
- `parse_timedelta(text, dialect=...)` for a `timedelta` (it raises
  `DurationRangeError` instead of dropping a sub-microsecond remainder),
- `format_duration(value, dialect=...)` with an `int` (nanoseconds) or a `timedelta`.

Fractions finer than a nanosecond truncate toward zero, which is what Go does.

The 0.1.0 functions `parse`, `parse_timedelta` (without `dialect`), `format` and
`format_timedelta` are unchanged and keep their float-based grammar.

## Dialects

| Dialect | Reads | Writes | Sign | Range |
|---|---|---|---|---|
| `human` (default) | `1 hour, 30 minutes`, `1h30m`, `1:30:00`, `-2d` | `1h 30m` | yes | `timedelta` |
| `go` | `time.ParseDuration` | `Duration.String` | yes | int64 ns |
| `iso8601` | `P3Y6M4DT12H30M5S`, `P1W`, `PT0,5S` | `P1DT2H` | yes | `timedelta` |
| `systemd` | `2 h 30 min`, `1week 2days`, `5` | `2h 30min` | no | `timedelta` |
| `prometheus` | `1w2d`, `90s`, `324ms` | `2w`, `23d1h` | no | int64 ns |

Each parser rejects anything its reference rejects, and `parse_ns(format_duration(x))`
equals `x` in every dialect.

### go

A step-by-step port of `ParseDuration` from `src/time/format.go`. Units are `ns`, `us`,
`µs` (U+00B5), `μs` (U+03BC), `ms`, `s`, `m`, `h`, case-sensitive. One optional sign,
`"0"` alone is zero, `".5s"` and `"5.s"` are valid, units may repeat in any order, no
spaces. Overflow follows Go's uint64 checks, so the range is exactly
`-9223372036854775808ns` to `9223372036854775807ns`.

Go computes the fractional part of each token with one float64 multiplication. That step
is reproduced on purpose, because it is what makes `0.3333333333333333333h` exactly
`20m` in Go; every other dialect uses pure integer arithmetic.

Formatting matches `Duration.String`: `0s`, `1ns`, `1.1µs`, `2.2ms`, `4m5s`, `1h0m0s`.

### iso8601

`[+-]PnYnMnDTnHnMnS` or `[+-]PnW`. The decimal mark may be `.` or `,`, and only the last
field may carry a fraction. Weeks stand alone. Days are exact 24 hour days.

Years and months have no fixed length. Without a reference date they raise
`AmbiguousDurationError`, whose `position` points at the field. With
`reference=date(...)` or a `datetime`, they are added on the calendar first (the day
clamps to the end of a shorter month, so `P1M` from 31 January 2024 is 29 days), then the
fixed fields are added. A leading `-` subtracts the whole span from the reference.

Formatting writes days, hours, minutes and seconds: `PT0S`, `PT1H30M`, `P1DT12H`,
`PT0.000000001S`, `-P1D`.

### systemd

The units of `systemd.time(7)`: `usec us µs`, `msec ms`, `seconds second sec s`,
`minutes minute min m`, `hours hour hr h`, `days day d`, `weeks week w`,
`months month M`, `years year y`, plus `nsec ns`. Case matters (`M` is a month), spaces
may appear anywhere between tokens, a bare number is seconds and repeated units add up.
A year is 365.25 days and a month a twelfth of a year (2629800 seconds), the values in
`src/basic/time-util.h`. `infinity` is refused, since it is not a finite span.

Formatting follows `format_timespan`: `0`, `1min 30s`, `1y 1us`.

### prometheus

The anchored regex of `model.ParseDuration`: `y w d h m s ms`, whole numbers, largest
unit first, each at most once, and the literal `"0"`. A year is 365 days. Formatting
matches `Duration.String`, which writes years and weeks only when they divide exactly
(`14d` becomes `2w`, `3w2d1h` becomes `23d1h`). Values must be whole milliseconds.

### human

For text people type. Long and short unit names, case-insensitive, separated by spaces,
commas or `and`; a leading sign; clock text `H:MM:SS` or `M:SS` with an optional
fraction. Units: weeks, days, hours, minutes, seconds, milliseconds, microseconds and
nanoseconds. Months and years raise `AmbiguousDurationError`. A unit may appear once.

## Converting

```python
durospan.convert("2h45m30.5s", source="go", target="iso8601")  # 'PT2H45M30.5S'
durospan.convert("P1M", source="iso8601", target="human", reference=date(2023, 2, 1))  # '4w'
```

The target's limits apply: a negative value cannot become systemd text, a nanosecond
cannot become a Prometheus duration. Those raise `DurationRangeError`.

## Humanizing

```python
durospan.humanize(3725 * 10**9)  # '1h 2m 5s'
durospan.humanize(3725 * 10**9, precision=2)  # '1h 2m'
durospan.humanize(3725 * 10**9, long=True)  # '1 hour, 2 minutes, 5 seconds'
durospan.humanize(timedelta(days=3), largest="h")  # '72h'
```

`precision` keeps the N most significant units. The last kept unit is rounded half up
from the original value (never rounded twice) and carries, so `59m 59.6s` at precision
2 is `1h`. `smallest` and `largest` bound the units; zero renders in the smallest unit.

## Finding durations in text

`find_durations(text, dialect=...)` returns `DurationMatch(start, end, text, ns)` for
each span that the dialect's full parser accepts. Candidates that fail (a repeated unit,
a month without a reference) are skipped, never guessed. Clock text is not reported in
the human dialect because in prose `10:30` is usually a time of day.

## Errors

All errors derive from `DurationError`, a `ValueError`:

- `DurationSyntaxError`: the text does not follow the grammar,
- `DurationRangeError`: overflow, input over 4096 characters, a negative value for a
  dialect without a sign, or precision a target cannot hold,
- `AmbiguousDurationError`: years or months without a reference date.

When the location is known, `text`, `position` and `token` are set and `explain()`
draws a caret under the token:

```
unknown unit 'x' at position 5 in '1h 30x'
  1h 30x
       ^
```

## Command line

```
durospan parse 1h30m --dialect go                    # 5400000000000
durospan parse "1 hour, 30 minutes" --unit s         # 5400
durospan convert "2 h 30 min" --from systemd --to prometheus   # 2h30m
durospan humanize 3725s --precision 2                # 1h 2m
durospan find app.log --dialect go                   # start, end, ns, text per line
durospan parse --dialect go -- -1.5h                 # "--" before a leading minus
```

Errors go to stderr with the caret diagram and the exit status is 1. `python -m durospan`
works too.

## Sources

- Go: `src/time/format.go` and `src/time/time_test.go` in the Go repository.
- ISO 8601-1:2019, clause 5.5.2, and W3C XML Schema 1.1 Part 2, `xs:duration`.
- systemd: `systemd.time(7)`, `systemd-analyze(1)` and `src/basic/time-util.[ch]`.
- Prometheus: `model/time.go` and `model/time_test.go` in `prometheus/common`.

The golden vectors in `tests/golden_*.py` are short excerpts from these sources.
