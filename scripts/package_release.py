#!/usr/bin/env python3
"""Create deterministic, rights-separated Redot LimboAI archives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable
import zipfile


VERSION = "1.8.0+redot.26.2.1"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
CORE_DOCS = (
    "README.md",
    "COMPATIBILITY.md",
    "LIMITATIONS.md",
    "MIGRATION.md",
    "THIRD_PARTY_NOTICES.md",
    "LICENSE.md",
)
FORBIDDEN_PARTS = {
    ".godot",
    "__pycache__",
    "godot-cpp",
    "tests",
    "reports",
}
FORBIDDEN_SUFFIXES = {".a", ".exp", ".lib", ".o", ".obj", ".pdb", ".pyc"}


class PackageError(RuntimeError):
    """Raised when a release input or archive violates the package contract."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise PackageError(f"Required package input is missing: {path}")
    return path.read_bytes()


def add(entries: dict[str, bytes], destination: str, data: bytes) -> None:
    normalized = destination.replace("\\", "/").lstrip("/")
    path = Path(normalized)
    if not normalized or ".." in path.parts:
        raise PackageError(f"Unsafe archive path: {destination}")
    lowered_parts = {part.casefold() for part in path.parts}
    if lowered_parts & FORBIDDEN_PARTS or path.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise PackageError(f"Forbidden release path: {normalized}")
    if normalized in entries:
        raise PackageError(f"Duplicate archive path: {normalized}")
    entries[normalized] = data


def checksums(entries: dict[str, bytes]) -> bytes:
    lines = [f"{sha256(entries[path])}  {path}" for path in sorted(entries)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def core_license(path: str) -> str:
    return "MIT"


def demo_license(path: str) -> str:
    lowered = path.casefold()
    if lowered == "logo_license.md" or lowered.startswith("branding/"):
        return "CC-BY-4.0"
    if "/fonts/" in lowered or lowered == "ofl-1.1.txt":
        return "OFL-1.1"
    if "/assets/" in lowered and Path(lowered).suffix in {".png", ".svg", ".import"}:
        return "CC-BY-4.0"
    return "MIT"


def collect_core(
    source_root: Path,
    windows_addon: Path,
    linux_addon: Path,
    macos_addon: Path,
) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    manifest_path = source_root / "gdextension" / "limboai.gdextension"
    manifest = manifest_path.read_text(encoding="utf-8")
    manifest, removed = re.subn(
        r'^LimboAI = "res://addons/limboai/icons/LimboAI\.svg"\r?\n?',
        "",
        manifest,
        count=1,
        flags=re.MULTILINE,
    )
    if removed != 1:
        raise PackageError("The core manifest must contain exactly one removable logo mapping")
    add(
        entries,
        "addons/limboai/bin/limboai.gdextension",
        manifest.replace("\r\n", "\n").encode("utf-8"),
    )

    binary_inputs = (
        (
            windows_addon / "bin" / "liblimboai.windows.editor.x86_64.dll",
            "addons/limboai/bin/liblimboai.windows.editor.x86_64.dll",
        ),
        (
            windows_addon / "bin" / "liblimboai.windows.template_release.x86_64.dll",
            "addons/limboai/bin/liblimboai.windows.template_release.x86_64.dll",
        ),
        (
            linux_addon / "bin" / "liblimboai.linux.editor.x86_64.so",
            "addons/limboai/bin/liblimboai.linux.editor.x86_64.so",
        ),
        (
            linux_addon / "bin" / "liblimboai.linux.template_release.x86_64.so",
            "addons/limboai/bin/liblimboai.linux.template_release.x86_64.so",
        ),
        (
            macos_addon
            / "bin"
            / "liblimboai.macos.editor.framework"
            / "liblimboai.macos.editor",
            "addons/limboai/bin/liblimboai.macos.editor.framework/liblimboai.macos.editor",
        ),
        (
            macos_addon
            / "bin"
            / "liblimboai.macos.template_release.framework"
            / "liblimboai.macos.template_release",
            "addons/limboai/bin/liblimboai.macos.template_release.framework/liblimboai.macos.template_release",
        ),
    )
    for source, destination in binary_inputs:
        add(entries, destination, file_bytes(source))

    for icon in sorted((source_root / "icons").glob("*.svg")):
        if icon.name == "LimboAI.svg":
            continue
        add(entries, f"addons/limboai/icons/{icon.name}", file_bytes(icon))
    for name in CORE_DOCS:
        add(entries, f"addons/limboai/{name}", file_bytes(source_root / name))
    add(entries, "addons/limboai/version.txt", (VERSION + "\n").encode("utf-8"))
    add(entries, "addons/limboai/SHA256SUMS.txt", checksums(entries))
    return entries


def collect_demo(source_root: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    demo_root = source_root / "demo"
    for source in sorted((demo_root / "demo").rglob("*")):
        if source.is_file():
            relative = source.relative_to(demo_root).as_posix()
            add(entries, relative, file_bytes(source))
    for name in (
        "project.godot",
        "LICENSE_ASSETS.md",
        "README_REDOT.md",
        "THIRD_PARTY_FONTS.md",
        "OFL-1.1.txt",
    ):
        add(entries, name, file_bytes(demo_root / name))
    add(entries, "LICENSE.md", file_bytes(source_root / "LICENSE.md"))
    add(entries, "LOGO_LICENSE.md", file_bytes(source_root / "LOGO_LICENSE.md"))
    add(entries, "branding/limboai-logo.svg", file_bytes(source_root / "doc" / "images" / "logo.svg"))
    add(entries, "version.txt", (VERSION + "\n").encode("utf-8"))
    add(entries, "SHA256SUMS.txt", checksums(entries))
    return entries


def scan_entries(entries: dict[str, bytes], source_root: Path) -> None:
    forbidden_tokens = (
        str(source_root.resolve()).encode("utf-8"),
        str(source_root.resolve()).replace("\\", "/").encode("utf-8"),
        b"/workspace/plugins/redot-limboai",
        b"BEGIN PRIVATE KEY",
        b"fixture-result.json",
    )
    for path, data in entries.items():
        for token in forbidden_tokens:
            if token and token in data:
                raise PackageError(f"Forbidden content token in {path}: {token!r}")


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True
    ) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, entries[name], compresslevel=9)


def git_value(source_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=source_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise PackageError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def archive_record(
    path: Path, entries: dict[str, bytes], license_for: Callable[[str], str]
) -> dict[str, object]:
    return {
        "filename": path.name,
        "sha256": sha256(path.read_bytes()),
        "size": path.stat().st_size,
        "entry_count": len(entries),
        "entries": [
            {
                "path": name,
                "sha256": sha256(entries[name]),
                "size": len(entries[name]),
                "license": license_for(name),
            }
            for name in sorted(entries)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows-addon", type=Path, required=True)
    parser.add_argument("--linux-addon", type=Path, required=True)
    parser.add_argument("--macos-addon", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--permit-dirty", action="store_true")
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1]
    status = git_value(source_root, "status", "--porcelain", "--untracked-files=all")
    if status and not args.permit_dirty:
        raise PackageError("Refusing to package a dirty source tree without --permit-dirty")

    core = collect_core(
        source_root,
        args.windows_addon.resolve(),
        args.linux_addon.resolve(),
        args.macos_addon.resolve(),
    )
    demo = collect_demo(source_root)
    scan_entries(core, source_root)
    scan_entries(demo, source_root)

    output = args.output.resolve()
    core_zip = output / f"redot-limboai-{VERSION}-core.zip"
    demo_zip = output / f"redot-limboai-{VERSION}-demo.zip"
    write_zip(core_zip, core)
    write_zip(demo_zip, demo)

    report = {
        "schema_version": 1,
        "status": "EVIDENCE_ONLY_DIRTY" if status else "PACKAGED_CLEAN_SOURCE",
        "version": VERSION,
        "source_commit": git_value(source_root, "rev-parse", "HEAD"),
        "working_tree_clean": not bool(status),
        "archives": {
            "core": archive_record(core_zip, core, core_license),
            "demo": archive_record(demo_zip, demo, demo_license),
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "release-manifest.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "SHA256SUMS.txt").write_text(
        f"{report['archives']['core']['sha256']}  {core_zip.name}\n"
        f"{report['archives']['demo']['sha256']}  {demo_zip.name}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "report": str(report_path)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PackageError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(2)
