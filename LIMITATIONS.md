# Limitations

- This downstream contains the complete immutable LimboAI `v1.8.0` baseline,
  not post-1.8 current-master changes. Its narrow Redot adaptations are listed
  in `COMPATIBILITY.md` and the baseline-delta report.
- Delivery is GDExtension-first. The optional upstream engine-module lane and
  its module-only test runner are not shipped.
- Only Redot 26.2 single-precision desktop builds are in scope.
- The provided Linux x86-64 libraries are built on Ubuntu 24.04 and require
  glibc 2.38 or newer. Older distributions need a source rebuild on an older
  compatible sysroot; no musl build is included.
- C#/.NET examples and support are out of scope. Custom tasks and states are
  verified through typed GDScript.
- The logo and demo/tutorial assets are not in the core archive. Install the
  separate demo package only when its CC BY 4.0 and OFL notices are acceptable.
- macOS Developer ID signing and notarization depend on the eventual
  distribution channel and owner credentials. Cross-built slice signatures
  are not Developer ID signatures and are not a public distribution claim.
- Headless automation proves editor initialization and source/runtime behavior,
  but not task-palette layout, keyboard focus, 150% scaling, or repeated visible
  editor lifecycle behavior. Those checks remain a release gate.
- The 200-agent sample detects major regressions but is not a universal
  performance guarantee. Hardware, behavior complexity, and game code remain
  material.
