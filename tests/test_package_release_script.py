from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
import struct


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

    def test_empty_and_truncated_libraries_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            for name in ("library.dll", "library.so", "liblimboai.macos.editor"):
                path = Path(temporary) / name
                for data in (b"", b"MZ", b"invalid"):
                    path.write_bytes(data)
                    with self.assertRaises(PACKAGE_RELEASE.PackageError):
                        PACKAGE_RELEASE.library_bytes(path)

    def test_core_requires_each_library_and_preserves_svg_options(self):
        from test_macos_audit import universal
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "gdextension").mkdir()
            (root / "gdextension/limboai.gdextension").write_text('[icons]' + chr(10) + 'LimboAI = "res://addons/limboai/icons/LimboAI.svg"' + chr(10))
            (root / "icons").mkdir()
            (root / "icons/Task.svg").write_bytes(b"<svg/>")
            (root / "icons/LimboAI.svg").write_bytes(b"<svg/>")
            for name in PACKAGE_RELEASE.CORE_DOCS:
                (root / name).write_bytes(b"notice")
            windows = root / "windows/bin"
            linux = root / "linux/bin"
            macos = root / "macos/bin"
            windows.mkdir(parents=True)
            linux.mkdir(parents=True)
            binaries = []
            for target in ("editor", "template_release"):
                dll = bytearray(240)
                dll[:2] = b"MZ"
                struct.pack_into("<I", dll, 60, 64)
                dll[64:68] = b"PE\0\0"
                struct.pack_into("<HHIIIHH", dll, 68, 0x8664, 1, 0, 0, 0, 112, 0x2000)
                struct.pack_into("<H", dll, 88, 0x20B)
                pe = windows / f"liblimboai.windows.{target}.x86_64.dll"
                pe.write_bytes(dll)
                elf = bytearray(64)
                elf[:6] = b"\x7fELF\x02\x01"
                struct.pack_into("<HH", elf, 16, 3, 62)
                so = linux / f"liblimboai.linux.{target}.x86_64.so"
                so.write_bytes(elf)
                framework = macos / f"liblimboai.macos.{target}.framework"
                framework.mkdir(parents=True)
                binary = framework / f"liblimboai.macos.{target}"
                binary.write_bytes(universal(library_name=f"liblimboai.macos.{target}"))
                binaries.extend((pe, so, binary))
            entries = PACKAGE_RELEASE.collect_core(root, windows.parent, linux.parent, macos.parent)
            sidecar = entries["addons/limboai/icons/Task.svg.import"].decode()
            self.assertIn("editor/scale_with_editor_scale=true", sidecar)
            self.assertIn("editor/convert_colors_with_editor_theme=true", sidecar)
            self.assertNotIn("addons/limboai/icons/LimboAI.svg.import", entries)
            PACKAGE_RELEASE.scan_entries(entries, root)
            for binary in binaries:
                original = binary.read_bytes()
                binary.write_bytes(b"")
                with self.assertRaises(PACKAGE_RELEASE.PackageError):
                    PACKAGE_RELEASE.collect_core(root, windows.parent, linux.parent, macos.parent)
                binary.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
