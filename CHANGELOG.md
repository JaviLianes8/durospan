# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-11

### Added

- `parse` and `parse_timedelta`: read token text (`"1d 4h30m"`, `"90s"`, `"1.5h"`) and
  clock text (`"28:30:00"`) into seconds or a `timedelta`.
- `format` and `format_timedelta`: render back into the same grammar, with `token`,
  `compact` and `clock` styles.
- `DurationError` for unknown units, repeated units, trailing junk, negatives,
  non-finite values and out-of-range durations.
- One shared unit table behind both directions, so the round trip is lossless.
