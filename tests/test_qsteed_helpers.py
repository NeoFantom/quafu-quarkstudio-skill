import builtins
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = [ROOT / "skills" / "en" / "baqis-quafu", ROOT / "skills" / "zh" / "baqis-quafu"]


def load_helper(skill_dir: Path, rel: str):
    path = skill_dir / "helpers" / rel
    spec = importlib.util.spec_from_file_location(rel.replace(".", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class QSteedHelperTests(unittest.TestCase):
    def test_qsteed_setup_uses_locally_validated_dependency_pins(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                setup = load_helper(skill_dir, "qsteed_setup.py")
                self.assertEqual(setup.QSTEED_PIN, "qsteed==0.2.2")
                self.assertEqual(setup.PYQUAFU_PIN, "pyquafu==0.4.1")
                commands = setup.build_install_commands(Path("/tmp/qsteed-venv"), Path("/usr/bin/python3.10"))
                rendered = [" ".join(map(str, cmd)) for cmd in commands]
                self.assertTrue(any("pyquafu==0.4.1" in cmd and "qsteed==0.2.2" in cmd for cmd in rendered))

    def test_qsteed_smoke_installs_and_cleans_typing_shim(self):
        for skill_dir in SKILL_DIRS:
            with self.subTest(skill_dir=skill_dir):
                smoke = load_helper(skill_dir, "qsteed_smoke.py")
                for name in smoke.TYPING_SHIM_NAMES:
                    if hasattr(builtins, name):
                        delattr(builtins, name)
                added = smoke.install_typing_shim()
                self.assertTrue({"List", "Dict", "Tuple", "Union", "Optional"}.issubset(set(added)))
                self.assertTrue(hasattr(builtins, "List"))
                smoke.cleanup_typing_shim(added)
                self.assertFalse(hasattr(builtins, "List"))


if __name__ == "__main__":
    unittest.main()
