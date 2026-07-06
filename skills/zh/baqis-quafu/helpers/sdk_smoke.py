#!/usr/bin/env python3
"""QuarkStudio smoke checks that never print the API token."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def default_user_env_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base).expanduser() / "baqis-quafu" / "credentials.env"
    return Path.home() / ".config" / "baqis-quafu" / "credentials.env"


DEFAULT_ENV_PATH = default_user_env_path()


def load_env_token(path: Path) -> str:
    path = path.expanduser()
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("QUAFU_API_TOKEN="):
            return line.split("=", 1)[1].strip()
    return ""


def load_token(args: argparse.Namespace) -> str:
    if os.environ.get("QUAFU_API_TOKEN"):
        return os.environ["QUAFU_API_TOKEN"].strip()
    token = load_env_token(args.env_path)
    if token:
        return token
    project_env_path = args.project_env_path
    if not project_env_path and args.project_root:
        project_env_path = args.project_root / ".env.local"
    if project_env_path:
        return load_env_token(project_env_path)
    return ""


def import_task():
    try:
        from quark import Task  # type: ignore
    except Exception as exc:
        raise SystemExit(f"FAIL import: could not import 'Task' from quark. Install with: python -m pip install quarkstudio. Error type: {type(exc).__name__}") from exc
    print("PASS import: from quark import Task")
    return Task


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe QuarkStudio smoke checks.")
    parser.add_argument("--check-import", action="store_true", help="Import quark.Task only; no token/network.")
    parser.add_argument("--status", action="store_true", help="Call tmgr.status() using an approved stored token.")
    parser.add_argument("--env-path", type=Path, default=DEFAULT_ENV_PATH, help="User-level credentials.env path.")
    parser.add_argument("--project-root", type=Path, help="Optional root containing a .env.local project token file.")
    parser.add_argument("--project-env-path", type=Path, help="Optional explicit project dotenv path.")
    args = parser.parse_args()

    if not args.check_import and not args.status:
        args.check_import = True

    Task = import_task()
    if args.status:
        token = load_token(args)
        if not token:
            raise SystemExit("FAIL status: no token found in QUAFU_API_TOKEN, user env file, or supplied project .env.local. Token value not printed.")
        try:
            tmgr = Task(token)
            status = tmgr.status()
        except Exception as exc:
            raise SystemExit(f"FAIL status: QuarkStudio status check failed ({type(exc).__name__}). Token value not printed.") from None
        print("PASS status: tmgr.status() returned current backend status/queue data:")
        print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
