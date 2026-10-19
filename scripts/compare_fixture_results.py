#!/usr/bin/env python3
"""Compare normalized semantic output from two LimboAI fixture runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from fixture_result import validate_result


def load_result(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("passed") is not True:
        raise ValueError("input run did not pass")
    return validate_result(document.get("result", document))


def normalized_cases(result: dict) -> list[dict]:
    normalized = []
    for case in validate_result(result)["cases"]:
        case_copy = json.loads(json.dumps(case))
        if case_copy.get("name") == "runtime_view_and_performance":
            case_copy.get("details", {}).pop("elapsed_usec", None)
        if case_copy.get("name") == "resource_roundtrip":
            case_copy.get("details", {}).pop("raw_sha256", None)
        normalized.append(case_copy)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    differences = []
    left, right = {}, {}
    left_cases, right_cases = [], []
    for label, path in (("left", args.left), ("right", args.right)):
        try:
            result = load_result(path)
        except (OSError, ValueError) as error:
            differences.append(f"{label}: invalid input ({type(error).__name__})")
        else:
            if label == "left":
                left, left_cases = result, normalized_cases(result)
            else:
                right, right_cases = result, normalized_cases(result)
    if left_cases != right_cases:
        differences.append("normalized case results differ")
    if left.get("fixed_delta") != right.get("fixed_delta"):
        differences.append("fixed delta differs")
    comparison = {
        "schema_version": 1,
        "passed": not differences,
        "left": str(args.left.resolve()),
        "right": str(args.right.resolve()),
        "left_engine": left.get("engine"),
        "right_engine": right.get("engine"),
        "differences": differences,
        "normalized_cases": left_cases if not differences else {
            "left": left_cases,
            "right": right_cases,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": comparison["passed"], "output": str(args.output)}))
    return 0 if comparison["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
