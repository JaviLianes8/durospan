# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1]

### Changed

- The go dialect golden vectors are now hand-written, plus a few short vectors cited from
  the Go test file with their URL and line, instead of a copy of the whole Go test table.
- The sdist ships only the sources, tests and docs.

## [0.2.0] - 2026-10-12

### Added

- Named dialects: `human`, `go`, `iso8601`, `systemd` and `prometheus`, each matching
  its reference grammar (Go's `time.ParseDuration`, ISO 8601 durations, `systemd.time(7)`
  time spans, Prometheus `model.ParseDuration`).
- `parse_ns` and `parse_seconds`: exact parsing to integer nanoseconds or a `Decimal`.
- `format_duration`: canonical output per dialect, exact round trip in each one within
  the dialect's range.
- `convert`: re-spell a duration from one dialect into another.
- `humanize`: short or long rendering with precision, rounding and unit bounds.
- `find_durations` and `DurationMatch`: locate durations in free text.
- `DurationSyntaxError`, `DurationRangeError` and `AmbiguousDurationError`, with
  `text`, `position`, `token` and `explain()` on every `DurationError`.
- ISO 8601 years and months resolved against a `reference` date, refused without one.
- `parse_timedelta` accepts `dialect=` and `reference=`.
- Overflow guards (int64 for Go and Prometheus, the `timedelta` range elsewhere) and a
  4096 character input limit.
- The `durospan` command (`parse`, `convert`, `humanize`, `find`) and `python -m durospan`.
- `GUIDE.md`.

## [0.1.0] - 2026-10-11

### Added

- `parse` and `parse_timedelta`: read token text (`"1d 4h30m"`, `"90s"`, `"1.5h"`) and
  clock text (`"28:30:00"`) into seconds or a `timedelta`.
- `format` and `format_timedelta`: render back into the same grammar, with `token`,
  `compact` and `clock` styles.
- `DurationError` for unknown units, repeated units, trailing junk, negatives,
  non-finite values and out-of-range durations.
- One shared unit table behind both directions, so the round trip is lossless.
