#!/usr/bin/env python3
"""Create an isolated, locally validated QSteed environment after user consent."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

QSTEED_PIN = "qsteed==0.2.2"
PYQUAFU_PIN = "pyquafu==0.4.1"
SUPPORTED_PYTHON_MINORS = {(3, 10), (3, 11)}
THIS_DIR = Path(__file__).resolve().parent
SMOKE = THIS_DIR / "qsteed_smoke.py"


def default_data_home() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base).expanduser()
    return Path.home() / ".local" / "share"


def default_venv_path() -> Path:
    return default_data_home() / "baqis-quafu" / "qsteed-venv"


def venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def python_version(python: Path) -> tuple[int, int, int]:
    proc = subprocess.run(
        [str(python), "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"Could not run {python}: {proc.stderr.strip() or proc.stdout.strip()}")
    return tuple(int(part) for part in proc.stdout.strip().split("."))  # type: ignore[return-value]


def validate_python(python: Path) -> Path:
    version = python_version(python)
    if version[:2] not in SUPPORTED_PYTHON_MINORS:
        raise SystemExit(
            f"QSteed setup needs Python 3.10 or 3.11; {python} is {version[0]}.{version[1]}.{version[2]}. "
            "Install Python 3.10/3.11 or pass --python /path/to/python3.10."
        )
    return python


def find_python(explicit: str | None) -> Path:
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("QSTEED_PYTHON"):
        candidates.append(os.environ["QSTEED_PYTHON"])
    candidates.extend(["python3.11", "python3.10"])
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        resolved = shutil.which(candidate) if not Path(candidate).exists() else candidate
        if not resolved:
            continue
        try:
            return validate_python(Path(resolved))
        except SystemExit:
            if explicit or candidate == os.environ.get("QSTEED_PYTHON"):
                raise
            continue
    raise SystemExit("Could not find Python 3.10 or 3.11 for QSteed. Pass --python /path/to/python3.10.")


def build_install_commands(venv: Path, python: Path) -> list[list[object]]:
    py = venv_python(venv)
    return [
        [python, "-m", "venv", venv],
        [py, "-m", "ensurepip", "--upgrade"],
        [py, "-m", "pip", "install", "--upgrade", "pip"],
        [py, "-m", "pip", "install", PYQUAFU_PIN, QSTEED_PIN],
        [py, str(SMOKE), "--check-import", "--transpile-demo"],
    ]


def run(cmd: list[object]) -> None:
    printable = " ".join(str(part) for part in cmd)
    print(f"$ {printable}", flush=True)
    subprocess.run([str(part) for part in cmd], check=True)


def run_qsteed_config(py: Path) -> None:
    code = "from qsteed.qsteed_config import copy_config; copy_config()"
    run([py, "-c", code])


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up optional BAQIS QSteed support in an isolated venv.")
    parser.add_argument("--yes", action="store_true", help="Actually create the venv and install packages. Without this, print a dry-run plan.")
    parser.add_argument("--python", help="Python 3.10/3.11 executable to use.")
    parser.add_argument("--venv", type=Path, default=default_venv_path(), help="Destination virtual environment path.")
    parser.add_argument("--skip-config", action="store_true", help="Do not run qsteed-config after installing.")
    args = parser.parse_args()

    python = find_python(args.python)
    venv = args.venv.expanduser().resolve(strict=False)
    commands = build_install_commands(venv, python)

    print("QSteed optional setup plan", flush=True)
    print(f"Python: {python}", flush=True)
    print(f"Venv: {venv}", flush=True)
    print(f"Pins: {PYQUAFU_PIN}, {QSTEED_PIN}", flush=True)
    for cmd in commands:
        print("DRY-RUN $ " + " ".join(str(part) for part in cmd), flush=True)
    if not args.skip_config:
        print(f"DRY-RUN $ {venv_python(venv)} -c 'from qsteed.qsteed_config import copy_config; copy_config()'", flush=True)
    if not args.yes:
        print("Dry run only. Re-run with --yes after the user approves package installation and local QSteed config creation.")
        return 0

    for cmd in commands:
        run(cmd)
    if not args.skip_config:
        run_qsteed_config(venv_python(venv))
    print("PASS qsteed setup: optional QSteed environment is ready. Use the venv python shown above for QSteed code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
