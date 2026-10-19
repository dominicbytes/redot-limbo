"""Strict editor-import gate with a temporary pinned-engine shutdown exception."""

import json
from pathlib import Path
import re

FAILURE_PATTERN = re.compile(
    r"(?:\bERROR:|\bWARNING:|\bFATAL:|crash|segmentation|cannot load|failed|leaked)",
    re.IGNORECASE,
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TEMPORARY = json.loads(Path(__file__).with_name("temporary_redot_263_import.json").read_text())


def diagnostics(output):
    return [line for line in ANSI.sub("", output).splitlines() if FAILURE_PATTERN.search(line)]


def completed_import(project, output):
    cache = project / ".godot"
    extensions = cache / "extension_list.cfg"
    classes = cache / "global_script_class_cache.cfg"
    if not extensions.is_file() or not classes.is_file():
        return False
    if "res://addons/limboai/bin/limboai.gdextension" not in extensions.read_text():
        return False
    icons = list((project / "addons/limboai/icons").glob("*.svg"))
    if not icons:
        return False
    for icon in icons:
        sidecar = icon.with_suffix(".svg.import")
        if not sidecar.is_file():
            return False
        remap = re.search(r'^path="res://([^"\n]+)"$', sidecar.read_text(), re.MULTILINE)
        if remap is None:
            return False
        imported = project / remap[1]
        if not imported.is_file() or imported.stat().st_size == 0:
            return False
    clean = ANSI.sub("", output)
    return bool(re.search(r"\[ DONE \].*(?:reimport|loading_editor_layout)", clean))


def assess_import(code, output, timed_out, project, require_editor_regression=False):
    suspicious = diagnostics(output)
    version = re.search(r"^Redot Engine(?: LTS)? v(\S+)", output, re.MULTILINE)
    pinned = version is not None and version[1] == TEMPORARY["engine_version"]
    allowed = TEMPORARY["diagnostics"]
    crash = code in TEMPORARY["crash_exit_codes"] and TEMPORARY["crash_marker"] in suspicious
    # Preserve exact diagnostic lines, their counts, and the actual process exit.
    eligible = pinned and not timed_out and completed_import(project, output)
    tolerated = [line for line in suspicious if eligible and
                 (line in allowed or (crash and line == TEMPORARY["crash_marker"]))]
    unexpected = [line for line in suspicious if line not in tolerated]
    duplicate = any(suspicious.count(line) > 1 for line in tolerated)
    regression = None
    if require_editor_regression:
        records = [line.removeprefix("LIMBOAI_EDITOR_RESULT ") for line in output.splitlines()
                   if line.startswith("LIMBOAI_EDITOR_RESULT ")]
        if len(records) == 1:
            try:
                regression = json.loads(records[0])
            except ValueError:
                pass
    regression_ok = not require_editor_regression or (isinstance(regression, dict)
        and regression.get("passed") is True
        and type(regression.get("checks")) is int and regression["checks"] > 0
        and regression.get("failures") == [])
    passed = not timed_out and not unexpected and not duplicate and regression_ok and (
        code == 0 or (eligible and crash))
    return {"passed": passed, "temporary_tolerance": bool(tolerated) or (eligible and crash),
            "tolerated_diagnostics": tolerated, "unexpected_diagnostics": unexpected,
            "editor_regression": regression}
