#!/usr/bin/env python3
"""Create deterministic, rights-separated Redot LimboAI archives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
import sys
from typing import Callable
import zipfile

from content_policy import display_path, scan_blob, sanitize_text
from audit_macos_binary import audit_library_data


VERSION = "1.8.0+redot.26.2.1"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
CORE_DOCS = (
    "README.md",
    "COMPATIBILITY.md",
    "UPSTREAM_LOCK.md",
    "LIMITATIONS.md",
    "MIGRATION.md",
    "THIRD_PARTY_NOTICES.md",
    "LICENSE.md",
    "LICENSE_REDOT_CPP.md",
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
        raise PackageError(f"Required package input is missing: {display_path(path)}")
    return path.read_bytes()


def valid_pe(data: bytes) -> bool:
    if len(data) < 64 or data[:2] != b"MZ":
        return False
    offset = struct.unpack_from("<I", data, 60)[0]
    if offset < 64 or offset + 24 > len(data) or data[offset:offset + 4] != b"PE\0\0":
        return False
    machine, count, _stamp, symbols, symbol_count, optional_size, flags = struct.unpack_from("<HHIIIHH", data, offset + 4)
    optional = offset + 24
    table = optional + optional_size
    if (machine != 0x8664 or not flags & 0x2000 or not count or optional_size < 112
            or table + count * 40 > len(data) or struct.unpack_from("<H", data, optional)[0] != 0x20B):
        return False
    image_size, headers_size = struct.unpack_from("<II", data, optional + 56)
    directories = struct.unpack_from("<I", data, optional + 108)[0]
    if not table + count * 40 <= headers_size <= len(data) or directories * 8 > optional_size - 112:
        return False
    if symbols or symbol_count:
        strings = symbols + symbol_count * 18
        if not symbols or strings + 4 > len(data):
            return False
        strings_size = struct.unpack_from("<I", data, strings)[0]
        if strings_size < 4 or strings + strings_size > len(data):
            return False
    executable_payload = False
    for index in range(count):
        section = table + index * 40
        virtual_size, address, size, start = struct.unpack_from("<IIII", data, section + 8)
        attributes = struct.unpack_from("<I", data, section + 36)[0]
        if address + max(virtual_size, size) > image_size:
            return False
        if size and (start < headers_size or start + size > len(data)):
            return False
        executable_payload |= bool(size and attributes & 0x20000000)
    return executable_payload


def valid_elf(data: bytes) -> bool:
    if len(data) < 64 or data[:7] != b"\x7fELF\x02\x01\x01":
        return False
    kind, machine, version, _entry, programs, sections, _flags, header_size, program_size, program_count, section_size, section_count, names = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
    if (kind != 3 or machine != 62 or version != 1 or header_size != 64
            or program_size != 56 or not program_count or program_count == 0xFFFF
            or programs < 64 or programs + program_size * program_count > len(data)):
        return False
    if sections or section_count:
        if (sections < 64 or not section_count or section_size != 64
                or sections + section_size * section_count > len(data) or names >= section_count):
            return False
    elif names:
        return False
    executable_payload = False
    for index in range(program_count):
        kind, flags, start, _address, _physical, size, memory_size, _alignment = struct.unpack_from("<IIQQQQQQ", data, programs + index * 56)
        if start + size > len(data) or (kind == 1 and memory_size < size):
            return False
        executable_payload |= bool(kind == 1 and flags & 1 and size)
    for index in range(section_count):
        _name, kind, _flags, _address, start, size, link, _info, _alignment, entry_size = struct.unpack_from("<IIQQQQIIQQ", data, sections + index * 64)
        if (kind not in (0, 8) and start + size > len(data)) or link >= section_count:
            return False
        if entry_size and size % entry_size:
            return False
    return executable_payload


def library_bytes(path: Path) -> bytes:
    data = file_bytes(path)
    if path.suffix == ".dll":
        valid = valid_pe(data)
    elif path.suffix == ".so":
        valid = valid_elf(data)
    else:
        try:
            audit_library_data(data, path.name)
        except ValueError as error:
            raise PackageError(f"Invalid library {display_path(path)}: Mach-O audit failed") from error
        valid = True
    if not valid:
        raise PackageError(f"Invalid or truncated library: {display_path(path)}")
    return data


def icon_import(resource: str) -> bytes:
    return (f'[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n'
            f'[deps]\n\nsource_file="res://{resource}"\n\n[params]\n\n'
            'editor/scale_with_editor_scale=true\n'
            'editor/convert_colors_with_editor_theme=true\n').encode("utf-8")


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
        add(entries, destination, library_bytes(source))

    for icon in sorted((source_root / "icons").glob("*.svg")):
        if icon.name == "LimboAI.svg":
            continue
        resource = f"addons/limboai/icons/{icon.name}"
        add(entries, resource, file_bytes(icon))
        add(entries, resource + ".import", icon_import(resource))
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
    for path, data in entries.items():
        hits = scan_blob(path, data)
        if hits:
            file, category = hits[0]
            raise PackageError(f"Forbidden content in {file}: {category}")


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
        raise PackageError("Git command failed")
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
    print(json.dumps({"status": report["status"], "report": report_path.name}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PackageError, subprocess.SubprocessError) as error:
        print("FAIL: " + sanitize_text(str(error)), file=sys.stderr)
        raise SystemExit(2)
