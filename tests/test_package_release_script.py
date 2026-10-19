from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
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

    def test_encoded_private_content_is_rejected_without_echoing_tokens(self):
        from test_content_policy import rooted_samples, archive
        for value in rooted_samples() + ["-----BEGIN RSA PRIVATE KEY-----"]:
            for encoding in ("utf-8", "utf-16le", "utf-16be"):
                data = archive({"nested.xml": value.encode(encoding)})
                with self.assertRaises(PACKAGE_RELEASE.PackageError) as raised:
                    PACKAGE_RELEASE.scan_entries({"addons/limboai/nested.zip": data}, Path("."))
                self.assertNotIn(value, str(raised.exception))
                self.assertIn("addons/limboai/nested.zip", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
