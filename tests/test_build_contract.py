import ast
import hashlib
import os
import runpy
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BuildContractTests(unittest.TestCase):
    def test_effective_inputs_reject_overridden_api_or_interface(self):
        tree = ast.parse((ROOT / "SConstruct").read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "verify_effective_binding_inputs")
        def reject(code):
            raise ValueError("rejected")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            api = root / "extension_api.json"
            header = root / "gdextension_interface.h"
            expected = hashlib.sha256(b"locked").hexdigest().upper()
            namespace = {"os": os, "Exit": reject, "read_dependency_lock": lambda key: expected,
                         "sha256_file": lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()}
            exec(compile(ast.Module(body=[function], type_ignores=[]), "SConstruct", "exec"), namespace)
            check = namespace[function.name]
            for override in ("custom_api_file", "gdextension_dir"):
                for changed in (api, header):
                    with self.subTest(override=override, changed=changed.name):
                        api.write_bytes(b"locked")
                        header.write_bytes(b"locked")
                        env = {"gdextension_dir": str(root), "custom_api_file": str(api), "build_library": True}
                        check(env, "redot")
                        changed.write_bytes(b"different")
                        with self.assertRaisesRegex(ValueError, "rejected"):
                            check(env, "redot")

    def test_locked_profile_rejects_disabled_effective_binding_build(self):
        tree = ast.parse((ROOT / "SConstruct").read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "verify_effective_binding_inputs")
        def reject(code):
            raise ValueError("rejected")
        namespace = {"os": os, "Exit": reject, "read_dependency_lock": lambda key: "locked",
                     "sha256_file": lambda path: "locked"}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "SConstruct", "exec"), namespace)
        check = namespace[function.name]
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "custom.py"
            config.write_text("build_library = False\n")
            # SCons resolves BoolVariable command-line values to the same bool
            # as custom.py/profile values before returning the binding env.
            for source, resolved in (("command-line", {"build_library": False}),
                                     ("custom.py", runpy.run_path(str(config))),
                                     ("profile", runpy.run_path(str(config)))):
                with self.subTest(source=source):
                    with self.assertRaisesRegex(ValueError, "rejected"):
                        check(resolved, "redot")
                    check(resolved, "godot-oracle")
            check({"build_library": True}, "redot")
        # Reject after the binding has resolved all its option sources.
        source = (ROOT / "SConstruct").read_text()
        self.assertLess(source.index('env = SConscript("godot-cpp/SConstruct")'),
                        source.index('verify_effective_binding_inputs(env, binding_profile)'))

    def test_compiler_flags_follow_selected_compiler(self):
        tree = ast.parse((ROOT / "SConstruct").read_text())
        node = next(node for node in tree.body if isinstance(node, ast.If) and 'is_msvc' in ast.unparse(node.test))
        class Environment(dict):
            def Append(self, **kwargs):
                self.update(kwargs)
        for msvc in (False, True):
            env = Environment(is_msvc=msvc)
            exec(compile(ast.Module(body=[node], type_ignores=[]), "SConstruct", "exec"), {"env": env, "os": os})
            flag = env["CCFLAGS"][0]
            self.assertTrue(flag.startswith("/d1trimfile:" if msvc else "-ffile-prefix-map="))
            self.assertNotIn("/d1trimfile:", flag if not msvc else "")


if __name__ == "__main__":
    unittest.main()
