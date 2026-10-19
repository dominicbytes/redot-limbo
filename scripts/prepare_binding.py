#!/usr/bin/env python3
"""Apply or verify the reviewed patch to the locked Redot C++ binding."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys


def dependency_lock(root):
    return dict(line.split("=", 1) for line in (root / "deps.env").read_text().splitlines()
                if line and not line.startswith("#"))


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def verify_binding_patch(root, apply=False):
    lock = dependency_lock(root)
    binding = root / "godot-cpp"
    patch = root / lock["REDOT_CPP_PATCH"]
    source = binding / "src/variant/variant.cpp"
    if digest(patch.read_bytes()) != lock["REDOT_CPP_PATCH_SHA256"]:
        raise ValueError("Reviewed binding patch hash mismatch")
    def git(*args):
        result = subprocess.run(["git", "-c", "safe.directory=" + str(binding.resolve()),
                                 "-C", str(binding), *args], capture_output=True, check=True)
        return result.stdout
    if git("rev-parse", "HEAD").decode().strip() != lock["REDOT_CPP_REF"]:
        raise ValueError("Binding revision mismatch")
    preimage = git("show", "HEAD:src/variant/variant.cpp")
    if digest(preimage) != lock["REDOT_CPP_VARIANT_PRE_SHA256"]:
        raise ValueError("Binding patch preimage mismatch")
    current = source.read_bytes().replace(b"\r\n", b"\n")
    if apply and digest(current) == lock["REDOT_CPP_VARIANT_PRE_SHA256"]:
        # Normalize only the verified preimage for identical patching on every OS.
        source.write_bytes(current)
        git("apply", "--check", str(patch.resolve()))
        git("apply", str(patch.resolve()))
    current = source.read_bytes().replace(b"\r\n", b"\n")
    if digest(current) != lock["REDOT_CPP_VARIANT_POST_SHA256"]:
        raise ValueError("Binding patched-source mismatch; run scripts/prepare_binding.py --apply")
    changes = set(git("diff", "HEAD", "--name-only").decode().splitlines())
    if changes - {"src/variant/variant.cpp", "gdextension/extension_api.json"}:
        raise ValueError("Unexpected changes in locked binding checkout")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        verify_binding_patch(Path(__file__).resolve().parents[1], args.apply)
    except (OSError, ValueError, subprocess.CalledProcessError):
        print("FAIL: binding patch verification failed", file=sys.stderr)
        return 1
    print("Verified reviewed binding patch and effective source hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
