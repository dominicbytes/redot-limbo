from pathlib import Path
import io
import base64
import gzip
import tarfile
import sys
import unittest
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import content_policy as policy


def rooted_samples():
    slash = chr(47)
    backslash = chr(92)
    return [chr(81) + ":" + backslash + "private" + backslash + "source.cpp",
            slash + slash.join(("home", "example", "source.cpp")),
            slash + slash.join(("Volumes", "disk", "source.cpp")),
            slash + slash.join(("mnt", "disk", "source.cpp")),
            slash + slash.join(("arbitrary", "checkout", "source.cpp")),
            backslash * 2 + backslash.join(("server", "share", "source.cpp"))]


def archive(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipped:
        for name, data in entries.items():
            zipped.writestr(name, data)
    return buffer.getvalue()


class ContentPolicyTests(unittest.TestCase):
    def test_generic_rooted_paths_in_all_encodings_and_alignments(self):
        for value in rooted_samples():
            for encoding in ("utf-8", "utf-16le", "utf-16be"):
                for prefix in (b"", b"\x00"):
                    with self.subTest(encoding=encoding, prefix=prefix):
                        hits = policy.scan_blob("library.bin", prefix + value.encode(encoding))
                        self.assertTrue(hits)
                        self.assertNotIn(value, str(hits))

    def test_private_key_header_variants_and_nested_archive_members(self):
        for kind in ("", "RSA ", "EC ", "OPENSSH ", "ENCRYPTED ", "DSA "):
            secret = "-----BEGIN " + kind + "PRIVATE KEY-----"
            for encoding in ("utf-8", "utf-16le", "utf-16be"):
                data = archive({"inner.docx": archive({"docProps/core.xml": secret.encode(encoding)})})
                hits = policy.scan_blob("outer.zip", data)
                self.assertIn(("outer.zip!inner.docx!docProps/core.xml", "private-key"), hits)
                self.assertNotIn(secret, str(hits))

    def test_embedded_base64_content_is_decoded_before_scanning(self):
        value = rooted_samples()[0].encode("utf-16le")
        data = b'<image href="data:application/octet-stream;base64,' + base64.b64encode(value) + b'"/>'
        hits = policy.scan_blob("image.svg", data)
        self.assertTrue(hits)
        self.assertNotIn(value.decode("utf-16le"), str(hits))

    def test_png_metadata_is_scanned_without_classifying_pixels_as_text(self):
        def chunk(kind, payload):
            return len(payload).to_bytes(4, "big") + kind + payload + b"CRC!"
        signature = b"\x89PNG\r\n\x1a\n"
        value = rooted_samples()[0].encode()
        image = signature + chunk(b"IDAT", value) + chunk(b"IEND", b"")
        self.assertEqual(policy.scan_blob("image.png", image), [])
        for kind, payload in ((b"tEXt", value), (b"zTXt", b"author\0\0" + zlib.compress(value)),
                              (b"iTXt", b"author\0\1\0en\0label\0" + zlib.compress(value))):
            image = signature + chunk(kind, payload) + chunk(b"IEND", b"")
            self.assertTrue(policy.scan_blob("image.png", image))

    def test_compressed_tar_members_and_secret_member_names_are_rejected(self):
        value = rooted_samples()[1]
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as tar:
            member = tarfile.TarInfo("metadata.xml")
            payload = value.encode("utf-16be")
            member.size = len(payload)
            tar.addfile(member, io.BytesIO(payload))
        compressed = bytearray(gzip.compress(b"safe content"))
        compressed[3] |= 8
        named = bytes(compressed[:10]) + value.encode() + b"\0" + bytes(compressed[10:])
        self.assertTrue(policy.scan_blob("metadata.gz", named))
        hits = policy.scan_blob("outer.tar.gz", gzip.compress(buffer.getvalue()))
        self.assertTrue(hits)
        self.assertNotIn(value, str(hits))
        secret = "-----BEGIN PGP PRIVATE KEY BLOCK-----"
        hits = policy.scan_blob("outer.zip", archive({secret: b"content"}))
        self.assertIn("private-key", {category for _, category in hits})
        self.assertNotIn(secret, str(hits))

    def test_archive_member_names_are_scanned_and_redacted(self):
        value = rooted_samples()[1]
        hits = policy.scan_blob("outer.zip", archive({value: b"content"}))
        self.assertTrue(hits)
        self.assertNotIn(value, str(hits))

    def test_paths_after_invalid_utf8_and_unicode_components_are_detected(self):
        value = rooted_samples()[0]
        self.assertTrue(policy.scan_blob("library.bin", b"invalid\xff" + value.encode()))
        value = chr(81) + ":" + chr(92) + chr(0x6D4B) + chr(0x8BD5)
        for encoding in ("utf-8", "utf-16le", "utf-16be"):
            self.assertTrue(policy.scan_blob("library.bin", value.encode(encoding)))

    def test_malformed_and_excessively_nested_archives_fail_closed(self):
        self.assertIn(("broken.zip", "invalid-archive"), policy.scan_blob("broken.zip", b"PK\x03\x04invalid"))
        data = archive({"content.txt": b"safe"})
        for _ in range(policy.MAX_ARCHIVE_DEPTH + 1):
            data = archive({"nested.zip": data})
        self.assertIn("archive-limit", {category for _, category in policy.scan_blob("outer.zip", data)})

    def test_resource_urls_and_system_dependencies_remain_valid(self):
        value = 'res://addons/limboai/icon.svg https://example.com/source/file -//W3C//DTD SVG 1.1//EN '
        value += chr(47) + 'usr/lib/libSystem.B.dylib ' + chr(47) + 'dev/urandom '
        value += chr(47) + 'System/Library/Frameworks/Foundation.framework/Foundation'
        self.assertEqual(policy.scan_blob("legal.txt", value.encode()), [])
        self.assertEqual(policy.sanitize_text(value), value)

    def test_relative_source_paths_and_opaque_code_bytes_are_not_rooted_paths(self):
        relative = chr(92) + "bt" + chr(92) + "../hsm/limbo_state.h"
        self.assertEqual(policy.scan_blob("library.bin", relative.encode()), [])
        self.assertEqual(policy.scan_blob("library.bin", b"/\xff\x01/\xff\x02"), [])
        slash = bytes((47,))
        noise = b"\0".join((b"%" + slash + b"p" + slash, b"=" + slash + b"f" + slash,
                             slash + b"aM" + slash, slash + b"s" + slash + b"+",
                             bytes((74, 58, 47, 49, 37, 82)), b"~$" + slash + b"." + slash + b"@S$ZBID1"))
        self.assertEqual(policy.scan_blob("image.bin", noise), [])

    def test_nested_evidence_and_logs_are_sanitized(self):
        for value in rooted_samples():
            document = policy.sanitize({"command": [value], "nested": {"error": "failed: " + value}})
            self.assertNotIn(value, str(document))
            self.assertIn("failed:", document["nested"]["error"])
        self.assertEqual(policy.display_path(Path(__file__)), "tests/test_content_policy.py")


if __name__ == "__main__":
    unittest.main()
