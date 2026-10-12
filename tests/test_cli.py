from __future__ import annotations

import io
from pathlib import Path

import pytest

from durospan._cli import EPILOG, build_parser, main


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


def test_parse_prints_nanoseconds(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "parse", "1h30m", "--dialect", "go") == (0, "5400000000000\n", "")


def test_parse_in_seconds_is_exact(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "parse", "1 hour, 30 minutes", "--unit", "s")[1] == "5400\n"
    assert _run(capsys, "parse", "300ms", "-d", "go", "-u", "s")[1] == "0.3\n"


def test_parse_accepts_a_reference(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "parse", "P1M", "-d", "iso8601", "-r", "2024-01-31", "-u", "s")
    assert (code, out) == (0, "2505600\n")


def test_leading_minus_after_double_dash(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "parse", "-d", "go", "--", "-1.5h")[1] == "-5400000000000\n"


def test_convert(capsys: pytest.CaptureFixture[str]) -> None:
    out = _run(capsys, "convert", "2h45m30.5s", "--from", "go", "--to", "iso8601")[1]
    assert out == "PT2H45M30.5S\n"


def test_humanize(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "humanize", "5400s", "--long")[1] == "1 hour, 30 minutes\n"
    assert _run(capsys, "humanize", "3725s", "-p", "2")[1] == "1h 2m\n"


def test_find_reads_stdin(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    stdin = io.TextIOWrapper(io.BytesIO(b"retry in 5 minutes"), encoding="utf-8")
    monkeypatch.setattr("sys.stdin", stdin)
    assert _run(capsys, "find")[1] == "9\t18\t300000000000\t5 minutes\n"


def test_find_reads_a_file(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("took 1.5s then 300ms\n", encoding="utf-8")
    out = _run(capsys, "find", str(log), "-d", "go")[1]
    assert [line.split("\t")[3] for line in out.splitlines()] == ["1.5s", "300ms"]


def test_bad_duration_goes_to_stderr_with_a_caret(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = _run(capsys, "parse", "1h 30x")
    assert (code, out) == (1, "")
    assert "unknown unit 'x'" in err
    assert err.rstrip().endswith("^")


def test_missing_file_is_an_error(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    code, _, err = _run(capsys, "find", str(tmp_path / "missing.log"))
    assert code == 1
    assert err.startswith("durospan: error:")


def test_usage_errors_exit_with_status_one(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as info:
        main(["parse", "1s", "--dialect", "java"])
    assert info.value.code == 1
    assert "invalid choice" in capsys.readouterr().err


def test_bad_reference_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as info:
        main(["parse", "P1M", "-d", "iso8601", "-r", "someday"])
    assert info.value.code == 1


def test_help_lists_runnable_examples() -> None:
    text = build_parser().format_help()
    assert "durospan convert 2h45m30.5s --from go --to iso8601" in text
    assert EPILOG.splitlines()[0] in text


def test_find_survives_bytes_that_are_not_utf8(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    log = tmp_path / "binary.log"
    log.write_bytes(b"\xff\xfe took 2s")
    code, out, _ = _run(capsys, "find", str(log), "-d", "go")
    assert code == 0
    assert out.endswith("\t2000000000\t2s\n")


def test_reference_accepts_a_utc_timestamp(capsys: pytest.CaptureFixture[str]) -> None:
    argv = ["parse", "P1M", "-d", "iso8601", "-r", "2024-01-31 10:00:00Z", "-u", "s"]
    assert _run(capsys, *argv)[1] == "2505600\n"
