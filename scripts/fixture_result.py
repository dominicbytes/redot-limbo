"""Shared complete-result contract for fixture execution and comparison."""

import json
import math
from pathlib import Path


CASE_INVENTORY = json.loads(Path(__file__).with_name("fixture_cases.json").read_text())
CASE_MINIMUM_TYPES = {entry["name"]: entry["minimum_variant_type_count"]
                      for entry in CASE_INVENTORY if isinstance(entry, dict)}
EXPECTED_CASE_NAMES = frozenset(entry if isinstance(entry, str) else entry["name"]
                                for entry in CASE_INVENTORY)


def skipped_case_names(result):
    count = result["variant_type_count"]
    return {name for name, minimum in CASE_MINIMUM_TYPES.items() if count < minimum}


def validate_result(result):
    if not isinstance(result, dict):
        raise ValueError("fixture result must be a JSON object")
    if result.get("schema_version") != 1 or result.get("passed") is not True:
        raise ValueError("fixture result is not a successful schema 1 document")
    if result.get("failures") != []:
        raise ValueError("fixture result has missing or nonempty failures")
    engine = result.get("engine")
    if not isinstance(engine, dict) or not isinstance(engine.get("string"), str) or not engine["string"]:
        raise ValueError("fixture engine metadata is missing")
    delta = result.get("fixed_delta")
    if type(delta) not in (int, float) or not math.isfinite(delta) or delta <= 0:
        raise ValueError("fixed delta must be a finite positive number")
    count = result.get("variant_type_count")
    if type(count) is not int or count not in (39, 40):
        raise ValueError("unsupported or missing runtime Variant type count")
    cases = result.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("semantic cases are missing")
    names = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("name"), str):
            raise ValueError("invalid semantic case")
        names.append(case["name"])
        if case.get("passed") is not True or not isinstance(case.get("details"), dict):
            raise ValueError("incomplete or failed semantic case")
        skipped = case["details"].get("skipped", False)
        required_skip = case["name"] in skipped_case_names(result)
        if skipped is not required_skip:
            raise ValueError("incorrect engine-conditional case status")
        if required_skip and case["details"] != {"skipped": True, "reason": "requires_variant_type_count_40"}:
            raise ValueError("missing conditional skip record")
    if len(set(names)) != len(names):
        raise ValueError("duplicate semantic case names")
    missing = EXPECTED_CASE_NAMES - set(names)
    extra = set(names) - EXPECTED_CASE_NAMES
    if missing or extra:
        raise ValueError(f"case inventory mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
    return result
