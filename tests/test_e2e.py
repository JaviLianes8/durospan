"""Build the wheel, install it into a fresh venv and drive the real ``durospan`` script."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def installed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    work = tmp_path_factory.mktemp("e2e")
    wheels = work / "wheels"
    build = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(wheels), str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    if build.returncode != 0:
        pytest.fail(f"wheel build failed:\n{build.stdout}\n{build.stderr}")
    wheel = next(wheels.glob("durospan-*.whl"))
    env_dir = work / "venv"
    venv.EnvBuilder(with_pip=True).create(env_dir)
    bin_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        capture_output=True,
        check=True,
    )
    return bin_dir


def _script(bin_dir: Path) -> str:
    return str(bin_dir / ("durospan.exe" if os.name == "nt" else "durospan"))


def _run(bin_dir: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": ""}
    return subprocess.run(
        [_script(bin_dir), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=bin_dir,
        check=False,
    )


def test_the_installed_script_parses(installed: Path) -> None:
    result = _run(installed, "parse", "1h30m", "--dialect", "go")
    assert (result.returncode, result.stdout, result.stderr) == (0, "5400000000000\n", "")


def test_the_installed_script_converts_and_humanizes(installed: Path) -> None:
    converted = _run(installed, "convert", "2h45m30.5s", "--from", "go", "--to", "iso8601")
    assert converted.stdout == "PT2H45M30.5S\n"
    human = _run(installed, "humanize", "PT1H30M", "-d", "iso8601", "--long")
    assert human.stdout == "1 hour, 30 minutes\n"


def test_the_installed_script_finds_in_stdin(installed: Path) -> None:
    result = _run(installed, "find", "-d", "systemd", stdin="RestartSec=5min 20s\n")
    assert result.stdout == "11\t19\t320000000000\t5min 20s\n"


def test_the_installed_script_reports_errors_on_stderr(installed: Path) -> None:
    result = _run(installed, "parse", "P1M", "-d", "iso8601")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "reference" in result.stderr


def test_the_installed_script_has_help_and_version(installed: Path) -> None:
    assert "examples:" in _run(installed, "--help").stdout
    assert _run(installed, "--version").stdout.startswith("durospan 0.")


def test_the_installed_package_is_the_wheel_not_the_checkout(installed: Path) -> None:
    python = installed / ("python.exe" if os.name == "nt" else "python")
    probe = subprocess.run(
        [str(python), "-c", "import durospan; print(durospan.__file__)"],
        capture_output=True,
        text=True,
        cwd=installed,
        env={**os.environ, "PYTHONPATH": ""},
        check=True,
    )
    assert "site-packages" in probe.stdout
