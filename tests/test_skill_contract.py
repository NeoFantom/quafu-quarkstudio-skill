import unittest
from pathlib import Path

ROOT_SKILL_DIR = Path("baqis-quafu")
SKILL_DIRS = [Path("skills/en/baqis-quafu"), Path("skills/zh/baqis-quafu")]
INSTALL_PROMPT = """Please install the BAQIS Quafu skill for me. I must choose one language before installation: English | 中文. No default language is allowed.
If I choose English, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/en/baqis-quafu
If I choose 中文, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/zh/baqis-quafu
If I do not choose a language, stop and ask again; do not install a top-level/root baqis-quafu folder.
If a baqis-quafu skill or legacy quarkstudio skill is already installed locally, ask me before replacing it; do not overwrite silently.
After installation, run the skill's first-run workflow: ask whether I have registered Quafu-SQC, configure/store my token only through the skill's safe helper, then ask whether I want optional BAQIS QSteed compiler/transpiler support. If I say yes to QSteed, show the helper dry run first and proceed only after I approve package installation and local QSteed config creation.
After installation, remind me to restart the agent/client if required for skill discovery."""


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
    def test_root_skill_is_not_installable_language_must_be_selected(self):
        for rel in ["SKILL.md", "skill.md", "agents/openai.yaml"]:
            with self.subTest(rel=rel):
                self.assertFalse(
                    (ROOT_SKILL_DIR / rel).exists(),
                    f"{ROOT_SKILL_DIR / rel} must not exist; install must route through skills/en or skills/zh",
                )

    def test_readmes_use_english_default_with_chinese_translation_link(self):
        english = Path("README.md").read_text(encoding="utf-8")
        chinese = Path("README.zh.md").read_text(encoding="utf-8")
        self.assertEqual(english.splitlines()[0], "[中文说明](README.zh.md)")
        self.assertEqual(chinese.splitlines()[0], "[English](README.md)")

    def test_readmes_require_explicit_language_choice_and_share_english_prompt(self):
        for path in [Path("README.md"), Path("README.zh.md")]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("No default language", text)
                self.assertIn("skills/en/baqis-quafu", text)
                self.assertIn("skills/zh/baqis-quafu", text)
                self.assertEqual(text.count(INSTALL_PROMPT), 1)
                self.assertNotIn("中文安装提示", text)
                self.assertNotIn("请帮我安装 BAQIS Quafu skill", text)
                self.assertNotIn("compatibility alias", text)
                self.assertNotIn("tree/main/baqis-quafu", text)

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
