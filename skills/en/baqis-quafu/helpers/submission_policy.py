#!/usr/bin/env python3
"""Persist and enforce explicit Quafu cloud-submission authorization.

This module has no SDK dependency. Call ``submit_authorized`` with a Task-like
manager only after constructing the exact job dictionary. Tests can therefore
use a fake manager and never touch the network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:  # POSIX
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - exercised through the Windows adapter test
    _fcntl = None

try:  # Windows
    import msvcrt as _msvcrt
except ImportError:  # pragma: no cover - normal on POSIX
    _msvcrt = None

SCHEMA_VERSION = 1
CONFIRM_EACH = "confirm_each"
AUTONOMOUS = "bounded_autonomous"
AUTONOMOUS_OPERATIONS = ("design", "submit", "poll", "analyze")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def default_state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME")
    return (Path(base).expanduser() if base else Path.home() / ".local" / "state") / "baqis-quafu"


def default_policy_path() -> Path:
    return default_state_dir() / "submission-policy.json"


def default_task_log_path() -> Path:
    return default_state_dir() / "submitted-tasks.jsonl"


def _atomic_json_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def confirm_each_policy() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": CONFIRM_EACH,
        "updated_at": _utc_now().isoformat(),
        "authorization": None,
    }


def load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or default_policy_path()
    if not policy_path.exists():
        return confirm_each_policy()
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION or data.get("mode") not in {CONFIRM_EACH, AUTONOMOUS}:
        raise ValueError(f"unsupported submission policy: {policy_path}")
    return data


def set_confirm_each(path: Path | None = None) -> dict[str, Any]:
    policy = confirm_each_policy()
    _atomic_json_write(path or default_policy_path(), policy)
    return policy


def set_bounded_autonomous(
    *,
    backends: list[str],
    max_shots_per_job: int,
    max_jobs: int,
    expires_at: str,
    path: Path | None = None,
) -> dict[str, Any]:
    if not backends or any(not item.strip() for item in backends):
        raise ValueError("at least one explicit backend is required")
    if max_shots_per_job < 1 or max_jobs < 1:
        raise ValueError("max shots and max jobs must be positive")
    expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expiry.tzinfo is None or expiry <= _utc_now():
        raise ValueError("expiry must be a future timezone-aware timestamp")
    policy = {
        "schema_version": SCHEMA_VERSION,
        "mode": AUTONOMOUS,
        "updated_at": _utc_now().isoformat(),
        "authorization": {
            "backends": sorted(set(backends)),
            "max_shots_per_job": max_shots_per_job,
            "max_jobs": max_jobs,
            "submitted_jobs": 0,
            "expires_at": expiry.isoformat(),
            "operations": list(AUTONOMOUS_OPERATIONS),
        },
    }
    _atomic_json_write(path or default_policy_path(), policy)
    return policy


def revoke(path: Path | None = None) -> dict[str, Any]:
    return set_confirm_each(path)


def job_fingerprint(task: Mapping[str, Any]) -> str:
    encoded = json.dumps(task, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def exact_confirmation(task: Mapping[str, Any]) -> str:
    """Return the confirmation value the user must explicitly echo/approve."""
    return job_fingerprint(task)


def _authorize(task: Mapping[str, Any], policy: dict[str, Any], exact_approval: str | None) -> None:
    shots = task.get("shots")
    if not isinstance(shots, int) or isinstance(shots, bool) or shots < 1 or shots % 1024 != 0:
        raise PermissionError("shots must be a positive multiple of 1024")
    if policy["mode"] == CONFIRM_EACH:
        if exact_approval != job_fingerprint(task):
            raise PermissionError("exact current job confirmation is required")
        return
    auth = policy["authorization"]
    if auth is None:
        raise PermissionError("autonomous authorization is missing")
    if datetime.fromisoformat(auth["expires_at"]) <= _utc_now():
        raise PermissionError("autonomous authorization has expired")
    backend = task.get("chip") or task.get("backend")
    if backend not in auth["backends"]:
        raise PermissionError("backend is outside the autonomous scope")
    if shots > auth["max_shots_per_job"]:
        raise PermissionError("shots are outside the autonomous scope")
    if auth["submitted_jobs"] >= auth["max_jobs"]:
        raise PermissionError("autonomous job limit is exhausted")


def _append_task_id(path: Path, tid: Any, task: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    record = {
        "task_id": str(tid),
        "submitted_at": _utc_now().isoformat(),
        "job_fingerprint": job_fingerprint(task),
        "backend": task.get("chip") or task.get("backend"),
    }
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


class _PolicyLock:
    def __init__(self, policy_path: Path):
        self.path = policy_path.with_suffix(policy_path.suffix + ".lock")
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.path.parent, 0o700)
        self.handle = self.path.open("a+b")
        os.chmod(self.path, 0o600)
        if _fcntl is not None:
            _fcntl.flock(self.handle.fileno(), _fcntl.LOCK_EX)
        elif _msvcrt is not None:
            self.handle.seek(0)
            if self.handle.read(1) == b"":
                self.handle.write(b"0")
                self.handle.flush()
            self.handle.seek(0)
            _msvcrt.locking(self.handle.fileno(), _msvcrt.LK_LOCK, 1)
        else:  # defensive: supported platforms provide one of the two modules
            raise RuntimeError("no supported file-lock implementation")
        return self

    def __exit__(self, exc_type, exc, traceback):
        assert self.handle is not None
        if _fcntl is not None:
            _fcntl.flock(self.handle.fileno(), _fcntl.LOCK_UN)
        else:
            assert _msvcrt is not None
            self.handle.seek(0)
            _msvcrt.locking(self.handle.fileno(), _msvcrt.LK_UNLCK, 1)
        self.handle.close()


def submit_authorized(
    tmgr: Any,
    task: Mapping[str, Any],
    *,
    exact_approval: str | None = None,
    policy_path: Path | None = None,
    task_log_path: Path | None = None,
) -> Any:
    """Authorize, submit once, and durably record the returned task id."""
    resolved_policy_path = policy_path or default_policy_path()
    # Serialize authorization, submission, task-id persistence, and counter
    # consumption so concurrent local workers cannot exceed an autonomous cap.
    with _PolicyLock(resolved_policy_path):
        policy = load_policy(resolved_policy_path)
        _authorize(task, policy, exact_approval)
        tid = tmgr.run(dict(task))
        _append_task_id(task_log_path or default_task_log_path(), tid, task)
        if policy["mode"] == AUTONOMOUS:
            policy["authorization"]["submitted_jobs"] += 1
            policy["updated_at"] = _utc_now().isoformat()
            _atomic_json_write(resolved_policy_path, policy)
        return tid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=default_policy_path())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show")
    sub.add_parser("confirm-each")
    sub.add_parser("revoke")
    auto = sub.add_parser("authorize-autonomous")
    auto.add_argument("--backend", action="append", required=True)
    auto.add_argument("--max-shots-per-job", type=int, required=True)
    auto.add_argument("--max-jobs", type=int, required=True)
    auto.add_argument("--expires-at", required=True)
    args = parser.parse_args()
    if args.command == "show":
        value = load_policy(args.policy)
    elif args.command in {"confirm-each", "revoke"}:
        value = set_confirm_each(args.policy)
    else:
        value = set_bounded_autonomous(
            backends=args.backend,
            max_shots_per_job=args.max_shots_per_job,
            max_jobs=args.max_jobs,
            expires_at=args.expires_at,
            path=args.policy,
        )
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
