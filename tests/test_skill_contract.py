import unittest
from pathlib import Path

SKILL_DIRS = [Path("baqis-quafu"), Path("skills/en/baqis-quafu"), Path("skills/zh/baqis-quafu")]


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} must start with YAML frontmatter"
    _, raw, _body = text.split("---\n", 2)
    meta: dict[str, str] = {}
    current_key = None
    current_lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("  ") and current_key:
            current_lines.append(line.strip())
            continue
        if current_key:
            meta[current_key] = " ".join(current_lines).strip()
            current_key = None
            current_lines = []
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.strip()
            if value in {">-", "|", ">"}:
                current_key = key.strip()
                current_lines = []
            else:
                meta[key.strip()] = value.strip().strip('"')
    if current_key:
        meta[current_key] = " ".join(current_lines).strip()
    return meta


class SkillContractTests(unittest.TestCase):
    def test_skill_frontmatter_descriptions_are_concise_and_trigger_qsteed(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                meta = read_frontmatter(skill_dir / "SKILL.md")
                self.assertEqual(meta["name"], "baqis-quafu")
                description = " ".join(meta["description"].split())
                self.assertLessEqual(len(description), 200, f"{skill_dir} description is too long for Claude trigger metadata")
                for trigger in ["Quafu", "QuarkStudio", "QSteed"]:
                    self.assertIn(trigger, description, f"{skill_dir} description should mention {trigger}")

    def test_lowercase_skill_md_exists_for_claude_and_matches_agent_skill_file(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                uppercase = skill_dir / "SKILL.md"
                lowercase = skill_dir / "skill.md"
                self.assertTrue(lowercase.exists(), f"{lowercase} required for Claude custom skill uploads")
                self.assertEqual(lowercase.read_text(encoding="utf-8"), uppercase.read_text(encoding="utf-8"))

    def test_qsteed_resources_are_declared_and_present(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                for rel in [
                    "reference/qsteed.md",
                    "helpers/qsteed_setup.py",
                    "helpers/qsteed_smoke.py",
                ]:
                    self.assertTrue((skill_dir / rel).exists(), f"{skill_dir} missing {rel}")
                    self.assertIn(rel, text, f"{skill_dir}/SKILL.md must route agents to {rel}")

    def test_openai_metadata_mentions_qsteed_and_invokes_skill(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                text = (skill_dir / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertIn("QSteed", text)
                self.assertIn("$baqis-quafu", text)


if __name__ == "__main__":
    unittest.main()
