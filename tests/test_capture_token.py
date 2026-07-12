import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HELPERS = [
    Path("skills/en/baqis-quafu/helpers/capture_token.py"),
    Path("skills/zh/baqis-quafu/helpers/capture_token.py"),
]


class CaptureTokenTests(unittest.TestCase):
    def test_bilingual_helpers_are_identical(self):
        self.assertEqual(HELPERS[0].read_bytes(), HELPERS[1].read_bytes())

    def test_skill_mirrors_route_to_private_capture_and_warn_about_chat(self):
        for language in ["en", "zh"]:
            with self.subTest(language=language):
                root = Path("skills") / language / "baqis-quafu"
                canonical = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(canonical, (root / "skill.md").read_text(encoding="utf-8"))
                self.assertIn("helpers/capture_token.py", canonical)
                self.assertIn("request_user_input", canonical)
                self.assertIn("AskUserQuestion", canonical)
                self.assertIn("transcript", canonical)
                self.assertIn("model", canonical)

    def test_auth_references_cite_normative_secret_input_boundary(self):
        for language in ["en", "zh"]:
            with self.subTest(language=language):
                text = (Path("skills") / language / "baqis-quafu/reference/auth.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("https://agentskills.io/specification", text)
                self.assertIn("https://modelcontextprotocol.io/specification/draft/client/elicitation", text)
                self.assertIn("form elicitation", text)

    def test_existing_environment_token_is_not_printed(self):
        secret = "test-secret-never-print"
        for helper in HELPERS:
            with self.subTest(helper=helper), tempfile.TemporaryDirectory() as home:
                env = os.environ.copy()
                env.update({"HOME": home, "QUAFU_API_TOKEN": secret})
                proc = subprocess.run(
                    [sys.executable, str(helper)], capture_output=True, text=True, env=env, check=False
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertNotIn(secret, proc.stdout + proc.stderr)
                self.assertIn("Token value redacted", proc.stdout)

    def test_noninteractive_capture_fails_closed_without_revealing_stdin(self):
        secret = "stdin-secret-must-not-appear"
        for helper in HELPERS:
            with self.subTest(helper=helper), tempfile.TemporaryDirectory() as home:
                env = os.environ.copy()
                env.pop("QUAFU_API_TOKEN", None)
                env.update({"HOME": home, "XDG_CONFIG_HOME": str(Path(home) / "config")})
                proc = subprocess.run(
                    [sys.executable, str(helper)],
                    input=secret,
                    capture_output=True,
                    text=True,
                    env=env,
                    start_new_session=True,
                    check=False,
                )
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn("controlling, user-visible terminal", proc.stderr)
                self.assertNotIn(secret, proc.stdout + proc.stderr)

    def test_private_capture_dispatches_to_platform_specific_console(self):
        helper = HELPERS[0].resolve()
        spec = importlib.util.spec_from_file_location("capture_token_dispatch", helper)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        sys.path.insert(0, str(helper.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)

        with mock.patch.object(module.os, "name", "nt"), mock.patch.object(
            module, "_read_windows_console_token", return_value="windows-token"
        ) as windows, mock.patch.object(module, "_read_posix_tty_token") as posix:
            self.assertEqual(module._read_private_token(), "windows-token")
            windows.assert_called_once_with()
            posix.assert_not_called()

        with mock.patch.object(module.os, "name", "posix"), mock.patch.object(
            module, "_read_windows_console_token"
        ) as windows, mock.patch.object(
            module, "_read_posix_tty_token", return_value="posix-token"
        ) as posix:
            self.assertEqual(module._read_private_token(), "posix-token")
            posix.assert_called_once_with()
            windows.assert_not_called()

    def test_private_capture_stores_mode_0600_without_echo(self):
        helper = HELPERS[0].resolve()
        spec = importlib.util.spec_from_file_location("capture_token", helper)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        sys.path.insert(0, str(helper.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)

        secret = "private-test-token"
        with tempfile.TemporaryDirectory() as config, mock.patch.dict(
            os.environ, {"XDG_CONFIG_HOME": config}, clear=False
        ), mock.patch.object(module, "DEFAULT_ENV_PATH", Path(config) / "baqis-quafu" / "credentials.env"), mock.patch.object(
            module, "_read_private_token", return_value=secret
        ), mock.patch.object(sys, "argv", [str(helper)]):
            self.assertEqual(module.main(), 0)
            path = Path(config) / "baqis-quafu" / "credentials.env"
            self.assertEqual(path.read_text(encoding="utf-8"), f"QUAFU_API_TOKEN={secret}\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
