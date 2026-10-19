#!/usr/bin/env python3
"""Test the existing 26.2-built desktop libraries against pinned Redot 26.3."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

from content_policy import sanitize_text
from prepare_binding import dependency_lock


def run(*arguments):
    subprocess.run([sys.executable, *map(str, arguments)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("windows", "linux", "macos"), required=True)
    parser.add_argument("--addon-project", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--engine-cache", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    lock = dependency_lock(root)
    suffix = {"windows": "windows_win64", "linux": "linux_x64", "macos": "macos_universal"}[args.platform]
    name = "Redot_v26.3-stable_" + suffix + ".zip"
    args.engine_cache.mkdir(parents=True, exist_ok=True)
    archive = args.engine_cache / name
    urllib.request.urlretrieve("https://github.com/Redot-Engine/redot-engine/releases/download/"
                               "redot-26.3-stable/" + name, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest().upper()
    if digest != lock["REDOT_RUNTIME_263_" + args.platform.upper() + "_SHA256"]:
        raise ValueError("Redot 26.3 release archive hash mismatch")
    extracted = args.engine_cache / "editor"
    with zipfile.ZipFile(archive) as package:
        package.extractall(extracted)
    patterns = {"windows": "*console.exe", "linux": "redot.linuxbsd.editor.x86_64*", "macos": "*.app/Contents/MacOS/*"}
    engines = [p for p in extracted.glob("**/" + patterns[args.platform]) if p.is_file()]
    if len(engines) != 1:
        raise ValueError("Expected exactly one Redot 26.3 desktop engine")
    engine = engines[0].resolve()
    if args.platform != "windows":
        engine.chmod(engine.stat().st_mode | 0o111)
    version = subprocess.check_output([str(engine), "--version"], text=True, timeout=30).strip()
    if version != lock["REDOT_RUNTIME_263_VERSION"]:
        raise ValueError("Unexpected Redot 26.3 engine identity")
    addon = args.addon_project / "addons/limboai"
    binaries = {p.relative_to(addon): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (addon / "bin").rglob("*") if p.is_file()}
    for profile in ("editor", "release"):
        label = args.platform + "-263-" + profile
        arguments = [root / "scripts/run_fixture.py", "--engine", engine, "--addon-project", args.addon_project,
                     "--output", args.output_root / label, "--label", "ci-" + label]
        if profile == "release":
            arguments.append("--force-" + args.platform + "-release-library")
        else:
            arguments.append("--editor-regression")
        run(*arguments)
        run(root / "scripts/compare_fixture_results.py",
            args.output_root / (args.platform + "-" + profile) / "run-summary.json",
            args.output_root / label / "run-summary.json", "--output",
            args.output_root / (args.platform + "-263-comparison-" + profile + ".json"))
    if any(hashlib.sha256((addon / path).read_bytes()).hexdigest() != digest
           for path, digest in binaries.items()):
        raise ValueError("Runtime testing modified the built libraries")
    print("Both runtimes passed with identical built library bytes")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("FAIL: " + sanitize_text(str(error)), file=sys.stderr)
        sys.exit(1)
