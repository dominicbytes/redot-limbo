from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"
SPEC = importlib.util.spec_from_file_location("package_release", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
PACKAGE_RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE_RELEASE)


class DeterministicPackageTests(unittest.TestCase):
    def test_version_matches_the_redot_1_8_port(self) -> None:
        self.assertEqual(PACKAGE_RELEASE.VERSION, "1.8.0+redot.26.2.1")

    def test_zip_bytes_are_reproducible(self) -> None:
        entries = {"b.txt": b"two\n", "a.txt": b"one\n"}
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first.zip"
            second = root / "second.zip"
            PACKAGE_RELEASE.write_zip(first, entries)
            PACKAGE_RELEASE.write_zip(second, entries)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_forbidden_cache_path_is_rejected(self) -> None:
        with self.assertRaises(PACKAGE_RELEASE.PackageError):
            PACKAGE_RELEASE.add({}, ".godot/extension_list.cfg", b"cache")

    def test_demo_asset_licenses_are_classified(self) -> None:
        self.assertEqual(
            PACKAGE_RELEASE.demo_license("demo/assets/agent.png"), "CC-BY-4.0"
        )
        self.assertEqual(
            PACKAGE_RELEASE.demo_license("demo/assets/fonts/knewave_regular.ttf"),
            "OFL-1.1",
        )
        self.assertEqual(PACKAGE_RELEASE.demo_license("demo/ai/task.gd"), "MIT")


if __name__ == "__main__":
    unittest.main()
