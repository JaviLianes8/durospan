"""Optional: compare the go dialect with a real Go toolchain, when one is installed."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import golden_go
import pytest

import durospan

GO = shutil.which("go")

PROGRAM = """package main

import (
\t"bufio"
\t"fmt"
\t"os"
\t"time"
)

func main() {
\tscanner := bufio.NewScanner(os.Stdin)
\tfor scanner.Scan() {
\t\td, err := time.ParseDuration(scanner.Text())
\t\tif err != nil {
\t\t\tfmt.Println("error")
\t\t} else {
\t\t\tfmt.Printf("%d %s\\n", int64(d), d.String())
\t\t}
\t}
}
"""

EXTRA = ["1h1h", "1h 30m", "1.5e3s", "+-1s", "00001s", "1.h", "0.0000000005s", "3h-1m"]


@pytest.mark.skipif(GO is None, reason="the go toolchain is not installed")
def test_go_dialect_agrees_with_time_parse_duration(tmp_path: Path) -> None:
    source = tmp_path / "main.go"
    source.write_text(PROGRAM, encoding="utf-8")
    inputs = [text for text, _ in golden_go.PARSE] + golden_go.ERRORS + EXTRA
    inputs = [text for text in inputs if text and "\n" not in text]
    result = subprocess.run(
        [str(GO), "run", str(source)],
        input="\n".join(inputs) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=300,
    )
    for text, line in zip(inputs, result.stdout.splitlines(), strict=True):
        try:
            ns = durospan.parse_ns(text, dialect="go")
        except durospan.DurationError:
            assert line == "error", text
            continue
        assert line == f"{ns} {durospan.format_duration(ns, dialect='go')}", text
