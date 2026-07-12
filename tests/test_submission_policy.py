import importlib.util
import json
import os
import stat
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = [ROOT / "skills" / "en" / "baqis-quafu", ROOT / "skills" / "zh" / "baqis-quafu"]


def load_policy_helper(skill_dir: Path):
    path = skill_dir / "helpers" / "submission_policy.py"
    spec = importlib.util.spec_from_file_location(f"submission_policy_{skill_dir.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class FakeTaskManager:
    def __init__(self):
        self.calls = []

    def run(self, task):
        self.calls.append(task)
        return "tid-fake-123"


class SubmissionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_policy_helper(SKILL_DIRS[0])
        self.tempdir = tempfile.TemporaryDirectory()
        base = Path(self.tempdir.name)
        self.policy_path = base / "submission-policy.json"
        self.log_path = base / "submitted-tasks.jsonl"
        self.task = {"chip": "ScQ-P10", "name": "bell", "shots": 1024, "circuit": "OPENQASM 2.0;"}

    def tearDown(self):
        self.tempdir.cleanup()

    def test_default_is_confirm_each_and_blocks_before_fake_sdk(self):
        tmgr = FakeTaskManager()
        self.assertEqual(self.helper.load_policy(self.policy_path)["mode"], self.helper.CONFIRM_EACH)
        with self.assertRaises(PermissionError):
            self.helper.submit_authorized(tmgr, self.task, policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(tmgr.calls, [])
        self.assertFalse(self.log_path.exists())

    def test_exact_confirmation_is_bound_to_complete_current_job(self):
        tmgr = FakeTaskManager()
        approval = self.helper.exact_confirmation(self.task)
        with self.assertRaises(PermissionError):
            self.helper.submit_authorized(tmgr, dict(self.task, shots=2048), exact_approval=approval,
                                          policy_path=self.policy_path, task_log_path=self.log_path)
        tid = self.helper.submit_authorized(tmgr, self.task, exact_approval=approval,
                                            policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(tid, "tid-fake-123")
        record = json.loads(self.log_path.read_text(encoding="utf-8"))
        self.assertEqual(record["task_id"], tid)
        self.assertEqual(record["job_fingerprint"], approval)

    def test_autonomous_policy_is_explicit_persisted_bounded_and_revocable(self):
        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        policy = self.helper.set_bounded_autonomous(backends=["ScQ-P10"], max_shots_per_job=1024,
                                                    max_jobs=1, expires_at=expiry, path=self.policy_path)
        self.assertEqual(policy["mode"], self.helper.AUTONOMOUS)
        tmgr = FakeTaskManager()
        self.helper.submit_authorized(tmgr, self.task, policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(self.helper.load_policy(self.policy_path)["authorization"]["submitted_jobs"], 1)
        with self.assertRaises(PermissionError):
            self.helper.submit_authorized(tmgr, self.task, policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(len(tmgr.calls), 1)
        revoked = self.helper.revoke(self.policy_path)
        self.assertEqual(revoked["mode"], self.helper.CONFIRM_EACH)
        self.assertIsNone(revoked["authorization"])

    def test_autonomous_scope_rejects_before_fake_sdk(self):
        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.helper.set_bounded_autonomous(backends=["ScQ-P10"], max_shots_per_job=1024,
                                           max_jobs=2, expires_at=expiry, path=self.policy_path)
        tmgr = FakeTaskManager()
        for task in [dict(self.task, chip="other"), dict(self.task, shots=2048)]:
            with self.subTest(task=task), self.assertRaises(PermissionError):
                self.helper.submit_authorized(tmgr, task, policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(tmgr.calls, [])

    def test_invalid_shots_are_blocked_before_fake_sdk_in_both_modes(self):
        for shots in [None, True, 0, -1024, 1, 100, 1025]:
            with self.subTest(mode="confirm_each", shots=shots):
                tmgr = FakeTaskManager()
                task = dict(self.task, shots=shots)
                with self.assertRaises(PermissionError):
                    self.helper.submit_authorized(
                        tmgr,
                        task,
                        exact_approval=self.helper.exact_confirmation(task),
                        policy_path=self.policy_path,
                        task_log_path=self.log_path,
                    )
                self.assertEqual(tmgr.calls, [])

        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.helper.set_bounded_autonomous(backends=["ScQ-P10"], max_shots_per_job=4096,
                                           max_jobs=10, expires_at=expiry, path=self.policy_path)
        for shots in [100, 1025]:
            with self.subTest(mode="autonomous", shots=shots):
                tmgr = FakeTaskManager()
                with self.assertRaises(PermissionError):
                    self.helper.submit_authorized(tmgr, dict(self.task, shots=shots),
                                                  policy_path=self.policy_path, task_log_path=self.log_path)
                self.assertEqual(tmgr.calls, [])

    def test_rejects_expired_and_naive_expiry(self):
        for expiry in [
            (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),
            (datetime.now() + timedelta(hours=1)).isoformat(),
        ]:
            with self.subTest(expiry=expiry), self.assertRaises(ValueError):
                self.helper.set_bounded_autonomous(backends=["ScQ-P10"], max_shots_per_job=1,
                                                   max_jobs=1, expires_at=expiry, path=self.policy_path)

    def test_policy_log_and_lock_are_owner_only_and_tid_is_persisted_immediately(self):
        self.helper.set_confirm_each(self.policy_path)
        events = []

        class OrderedFake:
            def run(_self, task):
                events.append("run")
                return "tid-ordered"

        original_append = self.helper._append_task_id

        def recording_append(path, tid, task):
            events.append("persist")
            original_append(path, tid, task)

        with mock.patch.object(self.helper, "_append_task_id", side_effect=recording_append):
            self.helper.submit_authorized(OrderedFake(), self.task,
                                          exact_approval=self.helper.exact_confirmation(self.task),
                                          policy_path=self.policy_path, task_log_path=self.log_path)
        self.assertEqual(events, ["run", "persist"])
        for path in [self.policy_path, self.log_path, self.policy_path.with_suffix(".json.lock")]:
            self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)

    def test_file_lock_prevents_concurrent_job_limit_overrun(self):
        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.helper.set_bounded_autonomous(backends=["ScQ-P10"], max_shots_per_job=1024,
                                           max_jobs=1, expires_at=expiry, path=self.policy_path)

        class SlowFake(FakeTaskManager):
            def run(self, task):
                time.sleep(0.05)
                return super().run(task)

        tmgr = SlowFake()
        outcomes = []

        def submit():
            try:
                outcomes.append(self.helper.submit_authorized(tmgr, self.task, policy_path=self.policy_path,
                                                              task_log_path=self.log_path))
            except PermissionError:
                outcomes.append("blocked")

        threads = [threading.Thread(target=submit) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertCountEqual(outcomes, ["tid-fake-123", "blocked"])
        self.assertEqual(len(tmgr.calls), 1)

    def test_windows_lock_adapter_uses_msvcrt_when_fcntl_is_unavailable(self):
        calls = []

        class FakeMsvcrt:
            LK_LOCK = 1
            LK_UNLCK = 2

            @staticmethod
            def locking(fd, operation, length):
                calls.append((operation, length))

        with mock.patch.object(self.helper, "_fcntl", None), mock.patch.object(self.helper, "_msvcrt", FakeMsvcrt):
            with self.helper._PolicyLock(self.policy_path):
                pass
        self.assertEqual(calls, [(FakeMsvcrt.LK_LOCK, 1), (FakeMsvcrt.LK_UNLCK, 1)])

    def test_bilingual_helpers_are_identical(self):
        english, chinese = [(skill / "helpers" / "submission_policy.py").read_bytes() for skill in SKILL_DIRS]
        self.assertEqual(english, chinese)


if __name__ == "__main__":
    unittest.main()
