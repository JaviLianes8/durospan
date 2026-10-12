"""The ``durospan`` command: parse, convert, humanize and find durations."""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import NoReturn

from ._api import DIALECTS, convert, parse_ns
from ._errors import DurationError
from ._find import find_durations
from ._humanize import _INDEX, humanize

EPILOG = """examples:
  durospan parse 1h30m --dialect go              # 5400000000000 (nanoseconds)
  durospan parse "1 hour, 30 minutes" --unit s   # 5400
  durospan parse P1M --dialect iso8601 --reference 2024-01-31 --unit s
  durospan parse --dialect go -- -1.5h           # put "--" before a leading minus
  durospan convert 2h45m30.5s --from go --to iso8601    # PT2H45M30.5S
  durospan convert "2 h 30 min" --from systemd --to prometheus   # 2h30m
  durospan humanize 5400s --long                 # 1 hour, 30 minutes
  durospan humanize 3725s --precision 2          # 1h 2m
  echo "retry in 5 minutes" | durospan find      # 9  18  300000000000  5 minutes

dialects: human (default), go, iso8601, systemd, prometheus
errors are printed to stderr with a caret under the bad token; the exit status is 1."""

_SCALE = {"ns": 0, "us": -3, "ms": -6, "s": -9}


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def _reference(value: str) -> date:
    try:
        if len(value) == 10:
            return date.fromisoformat(value)
        cleaned = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
        return datetime.fromisoformat(cleaned.replace(" ", "T", 1))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not an ISO date: {value!r}") from exc


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (exposed for documentation and tests)."""
    parser = _Parser(
        prog="durospan",
        description="Convert durations between human text, exact numbers and real formats.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    from . import __version__

    parser.add_argument("--version", action="version", version=f"durospan {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)

    def command(name: str, summary: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=summary, description=summary, epilog=EPILOG)
        sub.formatter_class = argparse.RawDescriptionHelpFormatter
        return sub

    def dialect(
        sub: argparse.ArgumentParser,
        *flags: str,
        dest: str | None = None,
        required: bool = False,
    ) -> None:
        default = None if required else "human"
        sub.add_argument(
            *flags,
            choices=DIALECTS,
            metavar="DIALECT",
            dest=dest,
            required=required,
            default=default,
        )

    def reference(sub: argparse.ArgumentParser) -> None:
        sub.add_argument(
            "-r", "--reference", type=_reference, help="date that resolves ISO years and months"
        )

    parse = command("parse", "print the exact value of a duration")
    parse.add_argument("text", help="the duration text")
    dialect(parse, "-d", "--dialect")
    parse.add_argument("-u", "--unit", choices=list(_SCALE), default="ns", help="output unit")
    reference(parse)

    conv = command("convert", "re-spell a duration in another dialect")
    conv.add_argument("text", help="the duration text")
    dialect(conv, "-f", "--from", dest="source", required=True)
    dialect(conv, "-t", "--to", dest="target", required=True)
    reference(conv)

    human = command("humanize", "render a duration for people to read")
    human.add_argument("text", help="the duration text")
    dialect(human, "-d", "--dialect")
    human.add_argument("-l", "--long", action="store_true", help="spell units out")
    human.add_argument("-p", "--precision", type=int, help="keep this many units")
    human.add_argument("--smallest", choices=list(_INDEX), default="s")
    human.add_argument("--largest", choices=list(_INDEX), default="w")

    find = command("find", "list the durations found in a file or stdin")
    find.add_argument("file", nargs="?", default="-", help="file to scan, '-' for stdin")
    dialect(find, "-d", "--dialect")
    reference(find)
    return parser


def _run(args: argparse.Namespace) -> list[str]:
    if args.command == "parse":
        ns = parse_ns(args.text, dialect=args.dialect, reference=args.reference)
        if args.unit == "ns":
            return [str(ns)]
        return [format(Decimal(ns).scaleb(_SCALE[args.unit]).normalize(), "f")]
    if args.command == "convert":
        return [
            convert(args.text, source=args.source, target=args.target, reference=args.reference)
        ]
    if args.command == "humanize":
        ns = parse_ns(args.text, dialect=args.dialect)
        options = {"long": args.long, "precision": args.precision}
        return [humanize(ns, smallest=args.smallest, largest=args.largest, **options)]
    if args.file == "-":
        # Decode bytes ourselves: UTF-8 on every platform, never a crash on stray bytes.
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    else:
        with open(args.file, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    matches = find_durations(text, dialect=args.dialect, reference=args.reference)
    return [f"{m.start}\t{m.end}\t{m.ns}\t{m.text}" for m in matches]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the exit status."""
    for stream in (sys.stdout, sys.stderr):
        # A Windows console code page must not turn a stray character into a crash.
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace")
    args = build_parser().parse_args(argv)
    try:
        lines = _run(args)
    except DurationError as exc:
        print(f"durospan: error: {exc.explain()}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"durospan: error: {exc}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    return 0
