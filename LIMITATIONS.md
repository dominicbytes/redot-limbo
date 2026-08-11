# Limitations

- This downstream starts from LimboAI 1.6.0. Later feature work is not silently
  included; isolated fixes and their dispositions are listed in
  `reports/api-diffs/limboai-newest-vs-selected.md`.
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
- macOS signing and notarization depend on the eventual distribution channel
  and owner credentials. Unsigned local evidence is not a public distribution
  claim.
- Headless automation does not prove editor layout, keyboard focus, 150% scale,
  or repeated visible-editor lifecycle behavior. Those checks remain blocked
  until the recorded GNT-03 session is completed.
- The cross-platform 200-agent sample detects major regressions but is not a
  universal performance guarantee. Hardware, behavior complexity, and game
  code remain material.
