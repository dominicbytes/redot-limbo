# Architecture decisions

## ADR-0004: Select LimboAI 1.6.0

- Date: 2026-08-10
- Status: accepted
- Decision: base the port on full commit
  `91b22a187f7cd701e25eedd6dcff34179795e687`.
- Reason: it is the newest 1.6 release that builds and runs on the selected
  Godot/Redot 4.5.2 API lineage. LimboAI 1.8.0 requires 4.6.
- Consequence: 1.7/1.8 feature parity is not claimed; every later commit has an
  explicit disposition report.

## ADR-0005: Accept the official Redot API dump

- Date: 2026-08-10
- Status: accepted
- Decision: use the reproducible official engine dump with SHA-256
  `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577`
  in the pinned Redot C++ checkout.
- Evidence: two clean dumps matched; a recursive comparison against the
  binding's source-backed API found only official/custom build-label changes.
- Consequence: `SConstruct` fails closed on binding commit, API, and interface
  header mismatch and never auto-clones a mutable dependency.

## ADR-0006: Deliver GDExtension first

- Date: 2026-08-10
- Status: accepted
- Decision: ship the existing C++ GDExtension architecture for single-precision
  Windows x86-64, Linux x86-64, and macOS universal.
- Alternatives rejected: a GDScript rewrite, a second editor-plugin wrapper,
  module-first delivery, C#/.NET, and speculative later-platform scaffolding.

## ADR-0007: Backport only isolated proven fixes

- Date: 2026-08-10
- Status: accepted
- Backported: deep-copy clone semantics, `BTCallMethod` argument lifetime,
  blackboard self-parent rejection, macOS command shortcuts, inspector refresh
  after task duplication, and debugger message-capture unregistration.
- Rejected: upstream `9a3a2d4` editor-close lifecycle change targets Godot
  commit `658a237`, which is not present in the selected 4.5 lineage. The 1.6
  lifecycle is retained instead of importing a 4.6-only ownership change.
- Accepted with a 4.5 API guard: `567d783` adds the missing `GROUP_ENABLE`,
  `INPUT_NAME`, and `FILE_PATH` plan-editor hints. It passes five repeated
  Redot editor/runtime runs and still compiles against the 4.4 Godot oracle.
- A three-frame editor shutdown exposed an inherited initialization race in
  both unchanged v1.6 and the port. The deterministic harness now allows 120
  frames before shutdown; six repeated port runs complete without warnings.
- Consequence: broader 1.7/1.8 UI/features remain deferred unless a failing
  1.6 contract test proves they are necessary.

## ADR-0008: Split core from CC BY content

- Date: 2026-08-10
- Status: accepted
- Decision: the core ZIP contains the addon, six desktop libraries, non-logo
  icons, MIT notice, compatibility/migration documentation, version, and
  checksums. A separate demo ZIP contains the logo/tutorial, CC BY attribution,
  and OFL font notices.
- Consequence: the packaged core manifest omits the `LimboAI.svg` logo mapping;
  functionality and all other class icons remain intact.

## ADR-0009: Native CI is authoritative for macOS runtime

- Date: 2026-08-10
- Status: accepted
- Decision: local Zig thin/fat builds provide architecture and dependency
  evidence; the `macos-14` workflow must build universal frameworks and run
  editor/release fixtures using the official Redot app before release support
  is claimed.
- Consequence: a local cross-build cannot clear the native macOS runtime gate.
