#!/usr/bin/env python3
"""Expose Zig's Darwin compiler as the narrow OSXCross commands SCons expects."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys


def without_arch_flag(arguments: list[str]) -> list[str]:
    filtered: list[str] = []
    index = 0
    while index < len(arguments):
        if arguments[index] == "-arch":
            index += 2
            continue
        filtered.append(arguments[index])
        index += 1
    return filtered


def with_zig_object_suffix(arguments: list[str]) -> list[str]:
    normalized: list[str] = []
    for argument in arguments:
        if not argument.endswith(".os") or not Path(argument).is_file():
            normalized.append(argument)
            continue
        source = Path(argument)
        alias = source.with_name(source.name + ".o")
        alias.unlink(missing_ok=True)
        try:
            os.link(source, alias)
        except OSError:
            shutil.copy2(source, alias)
        normalized.append(str(alias))
    return normalized


def main() -> None:
    tool_name = Path(sys.argv[0]).name
    zig_cache_dir = Path("/tmp/limboai-zig-cache")
    zig_cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("ZIG_GLOBAL_CACHE_DIR", str(zig_cache_dir / "global"))
    os.environ.setdefault("ZIG_LOCAL_CACHE_DIR", str(zig_cache_dir / "local"))
    os.environ.setdefault("XDG_CACHE_HOME", str(zig_cache_dir / "xdg"))
    if tool_name.startswith("arm64-apple-"):
        target = "aarch64-macos.11.0"
    elif tool_name.startswith("x86_64-apple-"):
        target = "x86_64-macos.11.0"
    else:
        raise SystemExit(f"Unsupported OSXCross wrapper name: {tool_name}")

    arguments = sys.argv[1:]
    if tool_name.endswith("clang++"):
        command = [
            "zig",
            "c++",
            "-target",
            target,
            "-Wno-character-conversion",
            "-Wno-nullability-completeness",
            *with_zig_object_suffix(without_arch_flag(arguments)),
        ]
    elif tool_name.endswith("clang") or tool_name.endswith("-as"):
        command = ["zig", "cc", "-target", target, *without_arch_flag(arguments)]
    elif tool_name.endswith("-ar"):
        command = ["zig", "ar", *arguments]
    elif tool_name.endswith("-ranlib"):
        command = ["zig", "ranlib", *arguments]
    else:
        raise SystemExit(f"Unsupported OSXCross tool: {tool_name}")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
