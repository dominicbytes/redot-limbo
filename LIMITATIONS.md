# Limitations

- This downstream contains the complete immutable LimboAI `v1.8.0` baseline,
  not post-1.8 current-master changes. Its narrow Redot adaptations are listed
  in `COMPATIBILITY.md`.
- Delivery is GDExtension-only. The optional upstream engine-module lane and
  its module-only test runner are not shipped.
- Only the pinned Redot 26.2 and 26.3 single-precision desktop runtimes are in scope.
- The provided Linux x86-64 libraries are built on Ubuntu 24.04 and require
  glibc 2.38 or newer. Older distributions need a source rebuild on an older
  compatible sysroot; no musl build is included.
- C#/.NET examples and support are out of scope. Custom tasks and states are
  verified through typed GDScript.
- The logo and demo/tutorial assets are not in the core archive. Install the
  separate demo package only when its CC BY 4.0 and OFL notices are acceptable.
- macOS Developer ID signing and notarization depend on the distribution
  channel and signing credentials. Cross-built slice signatures are not
  Developer ID signatures and do not establish a notarized distribution.
- Headless automation proves editor initialization and source/runtime behavior,
  but not task-palette layout, keyboard focus, 150% scaling, or repeated visible
  editor lifecycle behavior. These require separate interactive validation.
- Headless fixtures cover representative task and resource behavior, not every
  upstream module-only test, interruption/subtree recursion case, malformed
  script, or external-resource migration. Constructing `BehaviorTreeView` does
  not verify populated tree visualization; sequential instance checks do not
  establish simultaneous-instance isolation.
- CI tests built libraries before packaging and compares assembled archives.
  It does not execute extracted packages or native exported games. Native
  Windows/macOS exports and visible clean-install authoring need separate
  validation. A universal macOS archive contains two architectures; execution
  on one host does not exercise both slices.
- The 200-agent sample detects major regressions but is not a universal
  performance guarantee. Hardware, behavior complexity, and game code remain
  material. Controlled repeated runs and debugger/editor latency measurements
  are needed for broader performance comparisons.

## Redot 26.3 editor shutdown (temporary)

The pinned official 26.3 engine can emit seven shutdown leak diagnostics during
headless editor import, and on Windows can instead exit with `0xC0000005` after
import completes. The same issue occurs without this extension. The narrow
allowlist is `scripts/temporary_redot_263_import.json`; remove it and its gate
when a fixed 26.3 engine is pinned. It accepts only anchored full-line matches
for those same seven
categories: any decimal allocation count in the six RID lines, with exact
severity, type and suffix, and the exact ObjectDB line. Duplicate categories
are rejected even when their counts differ. It also accepts the exact shutdown
crash marker with that Windows access-violation exit. Fresh expected extension/class caches, all imported SVG textures, and an
import completion marker must exist before any tolerance applies. Editor
regression runs additionally require the script's reported successful result,
a positive check total and no failures.

This exception applies only to the exact pinned 26.3 editor-import process.
Unexpected diagnostics, incomplete import, timeouts, other exits, 26.2
diagnostics, and all runtime diagnostics fail. The runtime fixture that follows
must pass cleanly. A tolerated import is recorded as such with its actual exit;
the actual diagnostic lines, categories and allocation counts are also retained.
It is not evidence of a leak-free or crash-free editor lifecycle.

## Struct authoring

26.3 offers Struct in BBVariant and blackboard type menus and creates an empty
Struct through the engine constructor interface. The native Struct inspector
can edit fields of an existing value. Defining a custom layout and field names
requires 26.3 script; selecting the type does not invent a schema. Struct values
and syntax cannot be brought back to 26.2. No typed Struct C++ wrapper or other
26.3-only API is added to the locked binding.

On downgrade to 26.2, saved Struct syntax fails resource parsing. A type-only
bound-mode parameter can load, but its unsupported `type = 39` declaration is
preserved with an error and no saved-value editor. It is not converted to Nil.
Back up and convert or remove every Struct declaration on 26.3 before downgrade;
do not resave failed or unsupported resources on 26.2. See `MIGRATION.md`.
