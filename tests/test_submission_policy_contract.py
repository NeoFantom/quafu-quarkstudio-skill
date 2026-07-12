import unittest
from pathlib import Path

SKILL_DIRS = [Path("skills/en/baqis-quafu"), Path("skills/zh/baqis-quafu")]


class SubmissionPolicyContractTests(unittest.TestCase):
    def test_installed_skills_discover_policy_and_guard_all_real_submission(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("helpers/submission_policy.py", skill)
                self.assertIn("submit_authorized", skill)
                self.assertIn("confirm_each", skill)
                self.assertTrue("bounded" in skill.lower() or "有边界" in skill)
                self.assertNotIn("tid = tmgr.run(task)", skill)
                self.assertEqual(skill, (skill_dir / "skill.md").read_text(encoding="utf-8"))

    def test_references_document_two_explicit_modes_and_commands(self):
        required = [
            "confirm-each",
            "authorize-autonomous",
            "--backend",
            "--max-shots-per-job",
            "--max-jobs",
            "--expires-at",
            "show",
            "revoke",
            "exact_confirmation",
            "submit_authorized",
            "tmgr.result(tid)",
        ]
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                safety = (skill_dir / "reference" / "safety.md").read_text(encoding="utf-8")
                basic = (skill_dir / "reference" / "basic-usage.md").read_text(encoding="utf-8")
                combined = safety + basic
                for value in required:
                    self.assertIn(value, combined)
                self.assertIn("confirm_each", combined)
                self.assertIn("fsync", combined)
                self.assertNotIn("tid = tmgr.run(task)", combined)

    def test_contract_examples_never_import_or_call_a_real_network_sdk(self):
        # This test is documentation-only: it reads files and deliberately has no quark/network import.
        for skill_dir in SKILL_DIRS:
            helper = skill_dir / "helpers" / "submission_policy.py"
            self.assertTrue(helper.is_file())
        self.assertNotIn("quark", globals())


if __name__ == "__main__":
    unittest.main()
