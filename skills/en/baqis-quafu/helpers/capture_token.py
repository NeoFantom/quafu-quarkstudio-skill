#!/usr/bin/env python3
"""Detect or privately capture a Quafu token without exposing token bytes to the agent."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from store_token import DEFAULT_ENV_PATH, store_project_env, store_user_env


def _env_file_has_token(path: Path) -> bool:
    try:
        lines = path.expanduser().read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, OSError, UnicodeError):
        return False
    return any(line.startswith("QUAFU_API_TOKEN=") and line.partition("=")[2].strip() for line in lines)


def _available_source(destination: str, project_root: Path) -> str | None:
    if os.environ.get("QUAFU_API_TOKEN", "").strip():
        return "QUAFU_API_TOKEN environment variable"
    if _env_file_has_token(DEFAULT_ENV_PATH):
        return str(DEFAULT_ENV_PATH.expanduser())
    project_path = project_root.expanduser() / ".env.local"
    if destination == "project-env" and _env_file_has_token(project_path):
        return str(project_path)
    return None


def _read_posix_tty_token() -> str:
    import termios

    try:
        tty = open("/dev/tty", "r+", encoding="utf-8", buffering=1)
    except OSError as exc:
        raise SystemExit(
            "Private token capture requires a controlling, user-visible terminal. No token was stored."
        ) from exc
    with tty:
        if not tty.isatty():
            raise SystemExit(
                "Private token capture requires a controlling, user-visible terminal. No token was stored."
            )
        original = termios.tcgetattr(tty.fileno())
        hidden = original.copy()
        hidden[3] &= ~termios.ECHO
        try:
            tty.write("Quafu API token (hidden): ")
            termios.tcsetattr(tty.fileno(), termios.TCSAFLUSH, hidden)
            token = tty.readline().strip()
        finally:
            termios.tcsetattr(tty.fileno(), termios.TCSAFLUSH, original)
            tty.write("\n")
    return token


def _read_windows_console_token() -> str:
    import msvcrt

    try:
        console_in = open("CONIN$", "r", encoding="utf-8")
        console_out = open("CONOUT$", "w", encoding="utf-8", buffering=1)
    except OSError as exc:
        raise SystemExit(
            "Private token capture requires a controlling, user-visible console. No token was stored."
        ) from exc
    chars: list[str] = []
    with console_in, console_out:
        if not console_in.isatty() or not console_out.isatty():
            raise SystemExit(
                "Private token capture requires a controlling, user-visible console. No token was stored."
            )
        console_out.write("Quafu API token (hidden): ")
        while True:
            char = msvcrt.getwch()
            if char in {"\r", "\n"}:
                console_out.write("\n")
                break
            if char == "\x03":
                raise KeyboardInterrupt
            if char in {"\b", "\x7f"}:
                if chars:
                    chars.pop()
                continue
            if char in {"\x00", "\xe0"}:
                msvcrt.getwch()
                continue
            chars.append(char)
    return "".join(chars).strip()


def _read_private_token() -> str:
    token = _read_windows_console_token() if os.name == "nt" else _read_posix_tty_token()
    if not token:
        raise SystemExit("No token entered. No token was stored.")
    if any(ch.isspace() for ch in token):
        raise SystemExit("Refusing to store a token containing whitespace. No token was stored.")
    return token


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Use an existing Quafu token or capture one privately from the local terminal."
    )
    parser.add_argument("--destination", choices=["user-env", "project-env"], default="user-env")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--allow-unignored-project-env", action="store_true")
    args = parser.parse_args()

    source = _available_source(args.destination, args.project_root)
    if source:
        print(f"Quafu credentials are already available from {source}. Token value redacted.")
        return 0

    token = _read_private_token()
    if args.destination == "user-env":
        store_user_env(token, DEFAULT_ENV_PATH)
    else:
        store_project_env(
            token,
            args.project_root / ".env.local",
            allow_unignored=args.allow_unignored_project_env,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
