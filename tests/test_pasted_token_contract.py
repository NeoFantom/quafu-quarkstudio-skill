import unittest
from pathlib import Path

SKILL_DIRS = [Path("skills/en/baqis-quafu"), Path("skills/zh/baqis-quafu")]


class PastedTokenContractTests(unittest.TestCase):
    def test_pasted_token_may_continue_only_through_non_replaying_stdin_path(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                auth = (skill_dir / "reference" / "auth.md").read_text(encoding="utf-8")
                combined = skill + auth
                self.assertIn("helpers/store_token.py --token-stdin", combined)
                self.assertIn("transcript", combined)
                self.assertIn("model", combined)
                self.assertIn("stdin", combined)
                self.assertIn("helpers/capture_token.py", combined)
                self.assertTrue("cannot undo" in combined or "不能撤销" in combined)
                self.assertTrue("cannot avoid" in combined or "无法避免" in combined)
                self.assertTrue("never echo" in combined or "绝不复述" in combined)
                self.assertTrue("may continue" in combined or "可以继续" in combined)
                self.assertNotIn("--token VALUE", combined)
                self.assertEqual(skill, (skill_dir / "skill.md").read_text(encoding="utf-8"))

    def test_capture_helper_remains_unchanged_by_this_contract(self):
        # Contract-level guard: pasted-token continuation routes to store_token, while
        # replacement collection still routes to the existing capture helper.
        for skill_dir in SKILL_DIRS:
            self.assertTrue((skill_dir / "helpers" / "capture_token.py").is_file())
            self.assertTrue((skill_dir / "helpers" / "store_token.py").is_file())


if __name__ == "__main__":
    unittest.main()
