#!/usr/bin/env python3
"""Audit universal LimboAI Mach-O libraries without requiring macOS tools."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


FAT_MAGIC = 0xCAFEBABE
MACHO_64_LE = 0xFEEDFACF
MH_DYLIB = 0x6
CPU_NAMES = {
    0x01000007: "x86_64",
    0x0100000C: "arm64",
}
LC_SYMTAB = 0x2
LC_LOAD_DYLIB = 0xC
LC_ID_DYLIB = 0xD
LC_LOAD_WEAK_DYLIB = 0x80000018
LC_REEXPORT_DYLIB = 0x8000001F
LC_LAZY_LOAD_DYLIB = 0x20
LC_LOAD_UPWARD_DYLIB = 0x80000023
LC_VERSION_MIN_MACOSX = 0x24
LC_CODE_SIGNATURE = 0x1D
LC_BUILD_VERSION = 0x32
PLATFORM_MACOS = 1
EXPECTED_ARCHES = {"x86_64", "arm64"}
EXPECTED_MIN_OS = "11.0.0"
FORBIDDEN = (
    b"D:\\",
    b"/workspace",
    b"Claude Vault",
    b"LIMBOAI_FIXTURE",
    b"ghp_",
    b"BEGIN RSA PRIVATE",
    b"BEGIN OPENSSH PRIVATE",
    b"BEGIN EC PRIVATE",
)
DYLIB_COMMANDS = {
    LC_LOAD_DYLIB,
    LC_LOAD_WEAK_DYLIB,
    LC_REEXPORT_DYLIB,
    LC_LAZY_LOAD_DYLIB,
    LC_LOAD_UPWARD_DYLIB,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def packed_version(value: int) -> str:
    return f"{value >> 16}.{(value >> 8) & 0xFF}.{value & 0xFF}"


def c_string(data: bytes, offset: int, limit: int) -> str:
    if offset < 0 or offset >= limit:
        raise ValueError(f"String offset {offset} is outside command bounds")
    end = data.find(b"\0", offset, limit)
    if end < 0:
        raise ValueError("Unterminated Mach-O string")
    return data[offset:end].decode("utf-8", errors="strict")


def audit_thin(data: bytes, expected_cpu: int) -> dict[str, object]:
    if len(data) < 32:
        raise ValueError("Truncated Mach-O header")
    magic, cpu, subtype, filetype, ncmds, sizeofcmds, flags, _reserved = struct.unpack_from(
        "<IiiIIIII", data, 0
    )
    if magic != MACHO_64_LE:
        raise ValueError(f"Unexpected Mach-O magic 0x{magic:08X}")
    if cpu & 0xFFFFFFFF != expected_cpu:
        raise ValueError(
            f"CPU mismatch: expected 0x{expected_cpu:08X}, got 0x{cpu & 0xFFFFFFFF:08X}"
        )
    if filetype != MH_DYLIB:
        raise ValueError(f"Expected MH_DYLIB, got file type {filetype}")
    command_end = 32 + sizeofcmds
    if command_end > len(data):
        raise ValueError("Mach-O load commands exceed slice bounds")

    dependencies: list[str] = []
    install_id: str | None = None
    minimum_os: list[str] = []
    signed = False
    symtab: tuple[int, int, int, int] | None = None
    cursor = 32
    for _ in range(ncmds):
        if cursor + 8 > command_end:
            raise ValueError("Truncated Mach-O load command")
        command, size = struct.unpack_from("<II", data, cursor)
        if size < 8 or cursor + size > command_end:
            raise ValueError(f"Invalid Mach-O load command size {size}")
        if command in DYLIB_COMMANDS or command == LC_ID_DYLIB:
            if size < 24:
                raise ValueError("Truncated dylib load command")
            name_offset = struct.unpack_from("<I", data, cursor + 8)[0]
            name = c_string(data, cursor + name_offset, cursor + size)
            if command in DYLIB_COMMANDS:
                dependencies.append(name)
            else:
                if install_id is not None:
                    raise ValueError("Mach-O contains multiple LC_ID_DYLIB commands")
                install_id = name
        elif command == LC_BUILD_VERSION:
            if size < 24:
                raise ValueError("Truncated build-version command")
            platform, minos = struct.unpack_from("<II", data, cursor + 8)
            if platform != PLATFORM_MACOS:
                raise ValueError(f"Unexpected Mach-O platform {platform}")
            minimum_os.append(packed_version(minos))
        elif command == LC_VERSION_MIN_MACOSX:
            if size < 16:
                raise ValueError("Truncated minimum-version command")
            minimum_os.append(packed_version(struct.unpack_from("<I", data, cursor + 8)[0]))
        elif command == LC_SYMTAB:
            if size < 24:
                raise ValueError("Truncated symbol-table command")
            symtab = struct.unpack_from("<IIII", data, cursor + 8)
        elif command == LC_CODE_SIGNATURE:
            signed = True
        cursor += size
    if cursor != command_end:
        raise ValueError("Mach-O load-command size does not match header")
    if minimum_os != [EXPECTED_MIN_OS]:
        raise ValueError(f"Expected minimum macOS {EXPECTED_MIN_OS}, got {minimum_os}")
    if install_id is None:
        raise ValueError("Mach-O install identity is missing")
    for dependency in dependencies:
        if not dependency.startswith(("/usr/lib/", "/System/Library/")):
            raise ValueError(f"Non-system dependency: {dependency}")
    if symtab is None:
        raise ValueError("Mach-O symbol table is missing")

    symoff, nsyms, stroff, strsize = symtab
    if symoff + nsyms * 16 > len(data) or stroff + strsize > len(data):
        raise ValueError("Mach-O symbol or string table exceeds slice bounds")
    symbols: set[str] = set()
    string_limit = stroff + strsize
    for index in range(nsyms):
        string_index = struct.unpack_from("<I", data, symoff + index * 16)[0]
        if string_index == 0 or string_index >= strsize:
            continue
        symbols.add(c_string(data, stroff + string_index, string_limit))
    if "_limboai_init" not in symbols:
        raise ValueError("Exported symbol _limboai_init is missing")

    return {
        "architecture": CPU_NAMES[expected_cpu],
        "cpu_subtype": subtype,
        "flags": f"0x{flags:08X}",
        "minimum_macos": minimum_os[0],
        "dependencies": sorted(dependencies),
        "install_id": install_id,
        "export": "_limboai_init",
        "signed": signed,
        "sha256": sha256(data),
        "bytes": len(data),
    }


def audit_library(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"Truncated universal binary: {path}")
    magic, count = struct.unpack_from(">II", data, 0)
    if magic != FAT_MAGIC:
        raise ValueError(f"Not a universal Mach-O binary: {path}")
    if count != len(EXPECTED_ARCHES):
        raise ValueError(f"Expected two Mach-O slices, got {count}")
    header_end = 8 + count * 20
    if header_end > len(data):
        raise ValueError("Truncated universal Mach-O header")

    slices: list[dict[str, object]] = []
    ranges: list[tuple[int, int]] = []
    for index in range(count):
        cpu, _subtype, offset, size, alignment = struct.unpack_from(
            ">IIIII", data, 8 + index * 20
        )
        if cpu not in CPU_NAMES:
            raise ValueError(f"Unexpected universal CPU type 0x{cpu:08X}")
        if alignment > 30 or offset % (1 << alignment) != 0:
            raise ValueError(f"Invalid slice alignment for {CPU_NAMES[cpu]}")
        if offset < header_end or offset + size > len(data):
            raise ValueError(f"Slice bounds are invalid for {CPU_NAMES[cpu]}")
        ranges.append((offset, offset + size))
        slices.append(audit_thin(data[offset : offset + size], cpu))
    ranges.sort()
    for left, right in zip(ranges, ranges[1:]):
        if left[1] > right[0]:
            raise ValueError("Universal Mach-O slices overlap")
    architectures = {item["architecture"] for item in slices}
    if architectures != EXPECTED_ARCHES:
        raise ValueError(f"Unexpected architecture set: {sorted(architectures)}")
    expected_install_id = "@rpath/" + path.name
    install_ids = {item["install_id"] for item in slices}
    if install_ids != {expected_install_id}:
        raise ValueError(
            f"Expected install identity {expected_install_id!r}, got {sorted(install_ids)}"
        )

    hits = [marker.decode("ascii", errors="replace") for marker in FORBIDDEN if marker in data]
    if hits:
        raise ValueError(f"Forbidden embedded strings: {hits}")
    return {
        "path": str(path.resolve()),
        "sha256": sha256(data),
        "bytes": len(data),
        "architectures": sorted(architectures),
        "forbidden_strings": 0,
        "slices": sorted(slices, key=lambda item: str(item["architecture"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", type=Path, nargs="+")
    args = parser.parse_args()
    reports = [audit_library(path.resolve(strict=True)) for path in args.library]
    print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
