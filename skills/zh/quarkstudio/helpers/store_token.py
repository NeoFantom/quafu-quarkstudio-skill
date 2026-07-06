#!/usr/bin/env python3
"""Store a Quafu API token without printing it.

Default destination is ~/.config/quarkstudio/credentials.env with 0600 file mode.
Project secrets.yaml writes require explicit --destination project-secrets.
"""
from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

DEFAULT_ENV_PATH = Path.home() / ".config" / "quarkstudio" / "credentials.env"
DEFAULT_SECRET_KEY = "baqis-quafu"


def _read_token(args: argparse.Namespace) -> str:
    token = ""
    if args.token_stdin:
        token = sys.stdin.read().strip()
    elif args.token_env:
        token = os.environ.get(args.token_env, "").strip()
    if not token:
        raise SystemExit("No token provided. Use --token-stdin or --token-env NAME. Token was not stored.")
    if any(ch.isspace() for ch in token):
        raise SystemExit("Refusing to store token containing whitespace. Token was not stored.")
    return token


def _chmod_private_file(path: Path) -> None:
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except PermissionError as exc:
        raise SystemExit(f"Failed to set restrictive permissions on {path}: {exc}") from exc


def store_user_env(token: str, path: Path) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(stat.S_IRWXU)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(f"QUAFU_API_TOKEN={token}\n", encoding="utf-8")
    _chmod_private_file(tmp)
    tmp.replace(path)
    _chmod_private_file(path)
    print(f"Stored Quafu token in {path} with mode 0600. Token value redacted.")


def store_project_secrets(token: str, project_root: Path, key: str) -> None:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on environment
        raise SystemExit("PyYAML is required for --destination project-secrets; install pyyaml or use user-env.") from exc

    secrets_path = project_root.expanduser().resolve() / "secrets.yaml"
    if secrets_path.exists():
        existing = yaml.safe_load(secrets_path.read_text(encoding="utf-8")) or {}
        if not isinstance(existing, dict):
            raise SystemExit(f"Refusing to overwrite non-mapping YAML in {secrets_path}.")
    else:
        existing = {}
    entry = existing.get(key) or {}
    if not isinstance(entry, dict):
        raise SystemExit(f"Refusing to overwrite non-mapping key {key!r} in {secrets_path}.")
    entry["key"] = token
    existing[key] = entry
    tmp = secrets_path.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.safe_dump(existing, allow_unicode=True, sort_keys=True), encoding="utf-8")
    _chmod_private_file(tmp)
    tmp.replace(secrets_path)
    _chmod_private_file(secrets_path)
    print(f"Stored Quafu token in {secrets_path} under {key}.key with mode 0600. Token value redacted.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Store a Quafu API token without printing it.")
    parser.add_argument("--destination", choices=["user-env", "project-secrets"], default="user-env")
    parser.add_argument("--token-stdin", action="store_true", help="Read token from stdin.")
    parser.add_argument("--token-env", help="Read token from an environment variable.")
    parser.add_argument("--path", type=Path, default=DEFAULT_ENV_PATH, help="user-env destination path.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Root containing secrets.yaml.")
    parser.add_argument("--secret-key", default=DEFAULT_SECRET_KEY, help="Top-level secrets.yaml key.")
    args = parser.parse_args()

    token = _read_token(args)
    if args.destination == "user-env":
        store_user_env(token, args.path)
    else:
        store_project_secrets(token, args.project_root, args.secret_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
