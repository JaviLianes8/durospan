# Improvement round: ranked plan

The 0.1.0 grammar round-trips its own text, but it parses through `float`, knows one
private dialect and cannot read the formats people already have in config files. This
round makes `durospan` the exact, typed bridge between the duration formats that real
tools emit. Ranked by value to users; everything is additive, the 0.1.0 API is unchanged.

## 1. Exact arithmetic everywhere (integer nanoseconds)

Parsing goes through integers, never `float`: `parse_ns` returns `int` nanoseconds,
`parse_seconds` returns an exact `Decimal`. Sub-nanosecond fractions truncate toward zero,
the rule Go uses. `9007199254740993ns` (2**53 + 1) survives, which a float cannot hold.

## 2. Named dialects that match the real grammars

`dialect=` accepts `go`, `iso8601`, `systemd`, `prometheus` and `human`, each pinned to its
reference implementation:

- `go`: `time.ParseDuration`, bit for bit, including the sign rules, `"0"`, `".5s"`,
  `"5.s"`, both micro signs, the int64 overflow edges and the float64 fraction step Go
  itself uses (so `0.3333333333333333333h` is exactly `20m`, as in Go).
- `iso8601`: `PnYnMnDTnHnMnS` and `PnW`, decimal comma, fraction only on the last field,
  optional leading `-`. Years and months have no fixed length, so they raise
  `AmbiguousDurationError` unless a `reference` datetime is given; then they are resolved
  on the calendar (month ends clamp). Nothing is guessed silently.
- `systemd`: every unit in `systemd.time(7)` with spaces allowed (`"2 h 30 min"`,
  `"1week 2days"`), bare numbers as seconds, case-sensitive `M` (month) versus `m`
  (minute), month and year at the lengths systemd defines in `time-util.h`.
- `prometheus`: the `y w d h m s ms` grammar of `model.ParseDuration`, integers
  only, fixed order, each unit once, `"0"` allowed.
- `human`: the forgiving superset for people: long names (`"1 hour, 30 minutes"`),
  `and`, sub-second units, clock text and a sign. Months and years are refused as
  ambiguous.

## 3. Canonical formatting per dialect

`format_duration(value, dialect=...)` writes the form each tool writes itself:
Go's `Duration.String` (`1h0m0s`, `1.5ms`, `-2562047h47m16.854775808s`), ISO
(`P1DT2H`, `PT0.5S`), systemd's `format_timespan` (`1min 30s`), Prometheus
(`2w`, `23d1h`, `0s`) and human (`1h 30m`). `parse(format(x)) == x` holds exactly in every
dialect, and `convert(text, source=..., target=...)` moves text between them.

## 4. Humanizing with real control

`humanize(value, long=..., precision=..., smallest=..., largest=...)` renders
`"1h 30m"` or `"1 hour, 30 minutes"`, keeps the N most significant units, rounds half up
on the last kept unit and carries (`59m 59.6s` at precision 2 is `1h`).

## 5. Typed errors that point at the bad token

`DurationError` keeps its role as the single `ValueError` base and gains `text`,
`position` and `token`, plus `explain()` for a caret diagram. Three subclasses split the
causes: `DurationSyntaxError`, `DurationRangeError` (overflow, input too long, value not
representable) and `AmbiguousDurationError` (years or months without a reference).

## 6. Overflow and abuse guards

Go and Prometheus stay inside int64 nanoseconds, like the originals; every other dialect
stays inside the `timedelta` range. Inputs over 4096 characters are refused before any
work, which also keeps huge digit strings away from `int()`.

## 7. Finding durations in free text

`find_durations(text, dialect=...)` returns `DurationMatch(start, end, text, ns)` for each
valid span, so logs and messages can be scanned without hand-written regexes.

## 8. Command line

`durospan parse`, `convert`, `humanize` and `find`, with runnable examples in `--help`,
errors on stderr with the caret diagram and exit status 1. Also `python -m durospan`.

## 9. Documentation and proof

A `GUIDE.md` that explains each dialect with its source, the exactness rules and the
ambiguity policy. Golden vectors copied from the Go test suite, the ISO standard examples,
`systemd.time(7)` and the Prometheus parser; seeded round-trip property tests per dialect;
an end-to-end test that builds the wheel, installs it into a fresh venv and drives the
real `durospan` script; an optional cross-check against a local Go toolchain.
