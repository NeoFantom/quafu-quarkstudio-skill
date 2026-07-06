#!/usr/bin/env python3
"""QuarkStudio smoke checks that never print the API token."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

DEFAULT_ENV_PATH = Path.home() / ".config" / "quarkstudio" / "credentials.env"


def load_env_token(path: Path = DEFAULT_ENV_PATH) -> str:
    if os.environ.get("QUAFU_API_TOKEN"):
        return os.environ["QUAFU_API_TOKEN"].strip()
    path = path.expanduser()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("QUAFU_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    return ""


def load_project_token(project_root: Path, secret_key: str) -> str:
    secrets_path = project_root / "secrets.yaml"
    if not secrets_path.exists():
        return ""
    try:
        import yaml  # type: ignore
    except Exception:
        return ""
    data = yaml.safe_load(secrets_path.read_text(encoding="utf-8")) or {}
    entry = data.get(secret_key) or {}
    if isinstance(entry, dict):
        return str(entry.get("key") or "").strip()
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
    parser.add_argument("--env-path", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--secret-key", default="baqis-quafu")
    args = parser.parse_args()

    if not args.check_import and not args.status:
        args.check_import = True

    Task = import_task()
    if args.status:
        token = load_env_token(args.env_path)
        if not token and args.project_root:
            token = load_project_token(args.project_root, args.secret_key)
        if not token:
            raise SystemExit("FAIL status: no token found in QUAFU_API_TOKEN, user env file, or supplied project secrets. Token value not printed.")
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
