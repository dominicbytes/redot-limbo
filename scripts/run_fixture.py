#!/usr/bin/env python3
"""Run the deterministic LimboAI GDExtension fixture in an isolated directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


FAILURE_PATTERN = re.compile(
    r"(?:\bERROR:|\bWARNING:|\bFATAL:|crash|segmentation|cannot load|failed|leaked)",
    re.IGNORECASE,
)
EDITOR_SETTLE_FRAMES = 120


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def copy_fixture(source_root: Path, project_root: Path) -> None:
    shutil.copytree(source_root / "tests" / "fixture", project_root, dirs_exist_ok=True)


def copy_addon(addon_project: Path, project_root: Path) -> None:
    source = addon_project / "addons" / "limboai"
    if not source.is_dir():
        raise FileNotFoundError(f"Built addon not found: {source}")
    shutil.copytree(source, project_root / "addons" / "limboai", dirs_exist_ok=True)


def force_release_library(project_root: Path, platform: str) -> Path:
    manifest = project_root / "addons" / "limboai" / "bin" / "limboai.gdextension"
    text = manifest.read_text(encoding="utf-8")
    keys = {
        "windows": ("windows.debug.x86_64", "windows.release.x86_64"),
        "linux": ("linux.debug.x86_64", "linux.release.x86_64"),
        "macos": ("macos.debug", "macos.release"),
    }
    debug_key, release_key = keys[platform]
    release_match = re.search(
        rf'^{re.escape(release_key)} = "([^"]+)"$', text, re.MULTILINE
    )
    if release_match is None:
        raise RuntimeError(f"{platform} release library is not declared in {manifest}")
    release_resource_path = release_match.group(1)
    replacement = f'{debug_key} = "{release_resource_path}"'
    updated, count = re.subn(
        rf'^{re.escape(debug_key)} = "[^"]+"$',
        replacement,
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError(
            f"{platform} debug library is not declared exactly once in {manifest}"
        )
    manifest.write_text(updated, encoding="utf-8")
    library_path = project_root / release_resource_path.removeprefix("res://")
    library = library_path / library_path.stem if library_path.is_dir() else library_path
    if not library.is_file():
        raise FileNotFoundError(f"{platform} release library not found: {library}")
    return library


def find_result(state_root: Path) -> Path:
    matches = list(state_root.rglob("fixture-result.json"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one fixture-result.json under {state_root}, found {len(matches)}")
    return matches[0]


def run_command(
    command: list[str], project_root: Path, environment: dict[str, str], timeout: int
) -> tuple[int, str, bool, float]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=project_root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return completed.returncode, completed.stdout, False, time.monotonic() - started
    except subprocess.TimeoutExpired as error:
        output_text = error.stdout or ""
        if isinstance(output_text, bytes):
            output_text = output_text.decode("utf-8", errors="replace")
        return 124, output_text, True, time.monotonic() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--addon-project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    release_group = parser.add_mutually_exclusive_group()
    release_group.add_argument(
        "--force-windows-release-library",
        action="store_true",
        help="Load the Windows template_release DLL in the runtime fixture.",
    )
    release_group.add_argument(
        "--force-linux-release-library",
        action="store_true",
        help="Load the Linux template_release shared library in the runtime fixture.",
    )
    release_group.add_argument(
        "--force-macos-release-library",
        action="store_true",
        help="Load the macOS template_release framework in the runtime fixture.",
    )
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1]
    engine = args.engine.resolve(strict=True)
    addon_project = args.addon_project.resolve(strict=True)
    output = args.output.resolve()
    allowed_output_root = (source_root.parent / "build" / "redot-limboai").resolve()
    try:
        output.relative_to(allowed_output_root)
    except ValueError:
        parser.error(f"--output must be inside {allowed_output_root}")
    if output == allowed_output_root:
        parser.error("--output must name a run directory, not the shared build root")
    project_root = output / "project"
    state_root = output / "state"
    import_log_path = output / "editor-import.log"
    log_path = output / "fixture.log"
    summary_path = output / "run-summary.json"

    if output.exists():
        shutil.rmtree(output)
    project_root.mkdir(parents=True)
    (state_root / "Roaming").mkdir(parents=True)
    (state_root / "Local").mkdir(parents=True)
    copy_fixture(source_root, project_root)
    copy_addon(addon_project, project_root)
    selected_library = None
    forced_release_platform = None
    if args.force_windows_release_library:
        forced_release_platform = "windows"
    elif args.force_linux_release_library:
        forced_release_platform = "linux"
    elif args.force_macos_release_library:
        forced_release_platform = "macos"
    if forced_release_platform is not None:
        selected_library = force_release_library(project_root, forced_release_platform)
        fixture_project = project_root / "project.godot"
        project_text = fixture_project.read_text(encoding="utf-8")
        expected_setting = "expect_editor_classes=true"
        if expected_setting not in project_text:
            raise RuntimeError(f"Fixture editor-class setting is missing in {fixture_project}")
        fixture_project.write_text(
            project_text.replace(expected_setting, "expect_editor_classes=false", 1),
            encoding="utf-8",
        )
        extension_cache = project_root / ".godot" / "extension_list.cfg"
        extension_cache.parent.mkdir(parents=True)
        extension_cache.write_text(
            "res://addons/limboai/bin/limboai.gdextension\n", encoding="utf-8"
        )

    import_command = [
        str(engine),
        "--headless",
        "--editor",
        "--path",
        str(project_root),
        "--quit-after",
        # Give editor plugins time to reach a stable ready state before teardown.
        str(EDITOR_SETTLE_FRAMES),
    ]
    fixture_command = [
        str(engine),
        "--headless",
        "--path",
        str(project_root),
        "--script",
        "res://test_runner.gd",
        "--quit-after",
        "120",
    ]
    environment = os.environ.copy()
    environment["APPDATA"] = str(state_root / "Roaming")
    environment["LOCALAPPDATA"] = str(state_root / "Local")
    if forced_release_platform is not None:
        import_return_code, import_output, import_timed_out, import_duration = (
            0,
            "Editor import skipped for the forced template_release library smoke test.\n",
            False,
            0.0,
        )
    else:
        import_return_code, import_output, import_timed_out, import_duration = run_command(
            import_command, project_root, environment, args.timeout
        )
    import_log_path.write_text(import_output, encoding="utf-8")
    if import_return_code == 0 and not import_timed_out:
        return_code, output_text, timed_out, duration = run_command(
            fixture_command, project_root, environment, args.timeout
        )
    else:
        return_code, output_text, timed_out, duration = (
            import_return_code,
            "Fixture execution skipped because editor import failed.\n",
            import_timed_out,
            0.0,
        )
    log_path.write_text(output_text, encoding="utf-8")

    result_path = None
    result = None
    try:
        result_path = find_result(state_root)
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RuntimeError) as error:
        result_error = str(error)
    else:
        result_error = None

    suspicious_lines = [
        line
        for line in (import_output + "\n" + output_text).splitlines()
        if FAILURE_PATTERN.search(line)
    ]
    passed = (
        not import_timed_out
        and import_return_code == 0
        and not timed_out
        and return_code == 0
        and result is not None
        and result.get("passed") is True
        and not suspicious_lines
    )
    summary = {
        "schema_version": 1,
        "label": args.label,
        "passed": passed,
        "import_command": import_command,
        "import_skipped": forced_release_platform is not None,
        "fixture_command": fixture_command,
        "import_return_code": import_return_code,
        "import_timed_out": import_timed_out,
        "import_duration_seconds": round(import_duration, 6),
        "return_code": return_code,
        "timed_out": timed_out,
        "duration_seconds": round(duration, 6),
        "engine": {"path": str(engine), "sha256": sha256(engine)},
        "addon_project": str(addon_project),
        "addon_manifest_sha256": sha256(
            addon_project / "addons" / "limboai" / "bin" / "limboai.gdextension"
        ),
        "selected_library": str(selected_library) if selected_library else None,
        "selected_library_sha256": sha256(selected_library) if selected_library else None,
        "forced_release_platform": forced_release_platform,
        "result_path": str(result_path) if result_path else None,
        "result_error": result_error,
        "result": result,
        "suspicious_log_lines": suspicious_lines,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": passed,
        "label": args.label,
        "summary": str(summary_path),
        "import_log": str(import_log_path),
        "log": str(log_path),
        "return_code": return_code,
        "suspicious_log_lines": len(suspicious_lines),
    }))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
