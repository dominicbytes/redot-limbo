import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fixture_result import validate_result
from test_run_fixture_script import successful_result
import compare_fixture_results as compare


class ConditionalCaseTests(unittest.TestCase):
    def test_skip_is_required_on_262_and_forbidden_on_263(self):
        result = successful_result()
        case = next(c for c in result["cases"] if c["name"] == "struct_263")
        result["variant_type_count"] = 39
        with self.assertRaisesRegex(ValueError, "conditional"):
            validate_result(result)
        case["details"] = {"skipped": True, "reason": "requires_variant_type_count_40"}
        validate_result(result)
        result["variant_type_count"] = 40
        with self.assertRaisesRegex(ValueError, "conditional"):
            validate_result(result)
        result["cases"][0]["details"] = {"skipped": True}
        with self.assertRaises(ValueError):
            validate_result(result)

    def test_comparison_records_conditional_difference_but_checks_shared_cases(self):
        import contextlib, io
        left, right = successful_result(), successful_result()
        left["variant_type_count"] = 39
        next(c for c in left["cases"] if c["name"] == "struct_263")["details"] = {
            "skipped": True, "reason": "requires_variant_type_count_40"}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            paths = [folder / name for name in ("left.json", "right.json", "comparison.json")]
            paths[0].write_text(json.dumps(left))
            for changed in (False, True):
                if changed:
                    right["cases"][0]["details"]["regression"] = True
                paths[1].write_text(json.dumps(right))
                with patch.object(sys, "argv", ["compare", str(paths[0]), str(paths[1]), "--output", str(paths[2])]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(compare.main(), int(changed))
                self.assertEqual(json.loads(paths[2].read_text())["engine_conditional_cases"], ["struct_263"])


if __name__ == "__main__":
    unittest.main()
