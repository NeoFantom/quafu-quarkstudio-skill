#!/usr/bin/env python3
"""Store a Quafu API token without printing it.

Default destination is $XDG_CONFIG_HOME/quarkstudio/credentials.env, falling back to
~/.config/quarkstudio/credentials.env, with 0600 file mode. Optional project-local
storage writes a .env.local file only when explicitly requested.
"""
from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path


def default_user_env_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base).expanduser() / "quarkstudio" / "credentials.env"
    return Path.home() / ".config" / "quarkstudio" / "credentials.env"


DEFAULT_ENV_PATH = default_user_env_path()


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


def _write_env_token(path: Path, token: str, *, private_parent: bool) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if private_parent:
        path.parent.chmod(stat.S_IRWXU)

    lines: list[str] = []
    replaced = False
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("QUAFU_API_TOKEN="):
                lines.append(f"QUAFU_API_TOKEN={token}")
                replaced = True
            else:
                lines.append(line)
    if not replaced:
        lines.append(f"QUAFU_API_TOKEN={token}")

    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    _chmod_private_file(tmp)
    tmp.replace(path)
    _chmod_private_file(path)


def _git_root(path: Path) -> Path | None:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip())


def _is_git_ignored(path: Path) -> bool:
    root = _git_root(path.parent)
    if root is None:
        return True
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    proc = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", str(rel)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def store_user_env(token: str, path: Path) -> None:
    _write_env_token(path, token, private_parent=True)
    print(f"Stored Quafu token in {path.expanduser()} with mode 0600. Token value redacted.")


def store_project_env(token: str, path: Path, *, allow_unignored: bool) -> None:
    path = path.expanduser()
    if not allow_unignored and not _is_git_ignored(path):
        raise SystemExit(
            f"Refusing to write {path} because it is inside a git repository and is not ignored. "
            "Add .env.local to .gitignore, choose --destination user-env, or rerun with --allow-unignored-project-env. Token was not stored."
        )
    _write_env_token(path, token, private_parent=False)
    print(f"Stored Quafu token in {path} with mode 0600. Token value redacted.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Store a Quafu API token without printing it.")
    parser.add_argument("--destination", choices=["user-env", "project-env"], default="user-env")
    parser.add_argument("--token-stdin", action="store_true", help="Read token from stdin.")
    parser.add_argument("--token-env", help="Read token from an environment variable.")
    parser.add_argument("--path", type=Path, help="Destination path. Defaults to user credentials.env or project .env.local.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Root used for the project-env .env.local default.")
    parser.add_argument("--allow-unignored-project-env", action="store_true", help="Allow writing a project .env.local even if git does not ignore it.")
    args = parser.parse_args()

    token = _read_token(args)
    if args.destination == "user-env":
        store_user_env(token, args.path or DEFAULT_ENV_PATH)
    else:
        store_project_env(token, args.path or (args.project_root / ".env.local"), allow_unignored=args.allow_unignored_project_env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
