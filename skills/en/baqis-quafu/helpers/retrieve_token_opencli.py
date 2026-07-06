#!/usr/bin/env python3
"""Retrieve a Quafu token from a logged-in opencli browser session without printing it."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
STORE_HELPER = THIS_DIR / "store_token.py"

JS = r"""
(async () => {
  const tokenResp = await fetch('/api/api-token', {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include'
  });
  if (!tokenResp.ok) {
    return {ok: false, status: tokenResp.status, detail: await tokenResp.text()};
  }
  const tokenData = await tokenResp.json();
  let exp = null;
  try {
    const expResp = await fetch('/api/api-token-expiration', {
      method: 'GET',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include'
    });
    if (expResp.ok) {
      const expData = await expResp.json();
      exp = expData.api_token_exp || null;
    }
  } catch (err) {}
  return {ok: true, api_token: tokenData.api_token || '', api_token_exp: exp};
})()
""".strip()


def run_opencli_eval(session: str) -> dict:
    cmd = ["opencli", "browser", session, "eval", JS]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"opencli eval failed with exit {proc.returncode}. Make sure the session is logged in and bound/open.")
    text = proc.stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.rfind("{")
        if start >= 0:
            try:
                return json.loads(text[start:])
            except json.JSONDecodeError:
                pass
        raise SystemExit("Could not parse opencli eval response. Token was not stored or printed.")


def store_token(token: str, args: argparse.Namespace) -> None:
    cmd = [sys.executable, str(STORE_HELPER), "--destination", args.store, "--token-stdin"]
    if args.store == "project-env":
        cmd += ["--project-root", str(args.project_root)]
        if args.allow_unignored_project_env:
            cmd += ["--allow-unignored-project-env"]
    if args.path:
        cmd += ["--path", str(args.path)]
    proc = subprocess.run(cmd, input=token, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip() or "Token storage failed.")
    print(proc.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve Quafu API token from logged-in browser and store it redacted.")
    parser.add_argument("--session", default="quafu-token", help="opencli browser session name.")
    parser.add_argument("--store", choices=["user-env", "project-env"], default="user-env")
    parser.add_argument("--path", type=Path, help="Optional destination path.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--allow-unignored-project-env", action="store_true")
    args = parser.parse_args()

    data = run_opencli_eval(args.session)
    if not data.get("ok"):
        status = data.get("status", "unknown")
        raise SystemExit(f"Browser session is not authenticated or token endpoint failed (status {status}). Token was not printed.")
    token = str(data.get("api_token") or "").strip()
    if not token:
        raise SystemExit("Authenticated endpoint returned no api_token. Token was not stored or printed.")
    store_token(token, args)
    if data.get("api_token_exp"):
        print(f"Token expiration reported by browser API: {data['api_token_exp']} (token value redacted).")
    else:
        print("Token retrieved and stored. Expiration was not available. Token value redacted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
