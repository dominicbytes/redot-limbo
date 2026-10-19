import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_binding import verify_binding_patch


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


class BindingPatchTests(unittest.TestCase):
    def test_apply_is_idempotent_and_rejects_modified_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binding = root / "godot-cpp"
            source = binding / "src/variant/variant.cpp"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"before\n")
            def git(*args):
                return subprocess.check_output(["git", "-C", str(binding), *args], stderr=subprocess.DEVNULL)
            git("init", "-q")
            git("add", "src/variant/variant.cpp")
            git("-c", "user.name=dominicbytes", "-c", "user.email=dominicbytes@users.noreply.github.com", "commit", "-qm", "Test binding input")
            patch = root / "change.patch"
            patch.write_bytes(b"--- a/src/variant/variant.cpp\n+++ b/src/variant/variant.cpp\n@@ -1 +1 @@\n-before\n+after\n")
            (root / "deps.env").write_text("\n".join([
                "REDOT_CPP_REF=" + git("rev-parse", "HEAD").decode().strip(),
                "REDOT_CPP_PATCH=change.patch", "REDOT_CPP_PATCH_SHA256=" + digest(patch.read_bytes()),
                "REDOT_CPP_VARIANT_PRE_SHA256=" + digest(b"before\n"),
                "REDOT_CPP_VARIANT_POST_SHA256=" + digest(b"after\n")]))
            with self.assertRaisesRegex(ValueError, "patched-source"):
                verify_binding_patch(root)
            verify_binding_patch(root, apply=True)
            verify_binding_patch(root, apply=True)
            self.assertEqual(source.read_bytes().replace(b"\r\n", b"\n"), b"after\n")
            patch.write_bytes(patch.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "patch hash"):
                verify_binding_patch(root)
            patch.write_bytes(patch.read_bytes()[:-1])
            source.write_bytes(b"changed\n")
            with self.assertRaisesRegex(ValueError, "patched-source"):
                verify_binding_patch(root, apply=True)


if __name__ == "__main__":
    unittest.main()
