# Blockers and release gates

The complete upstream LimboAI 1.8 source is now integrated and the local
desktop build/runtime gates pass where executable on the Windows host. The
remaining items limit release claims; they do not mean 1.8 features were
omitted.

## BLOCK-MAC-NATIVE: Native macOS result not yet executed

- Owner: repository owner / hosted workflow
- State: blocked outside the local Windows host
- Available path: `.github/workflows/redot-desktop.yml` has a pinned `macos-14`
  build, binary audit, editor fixture, and template-release fixture.
- Local evidence: both cross-built universal frameworks pass architecture,
  macOS 11.0, dependency, install-identity, export, and path-leakage audits.
- Release impact: blocks a native macOS runtime claim and GNT-04 PASS.

## BLOCK-EDITOR-GAUNTLET: Visible editor session not performed

- Owner: repository owner or authorized interactive tester
- State: blocked outside headless automation
- Required evidence: 100%/150% UI profiles, task-palette/favorites authoring,
  probability/status rendering, undo/redo, debugger blackboard selection,
  focus/readability, and five enable/disable plus five reopen cycles.
- Release impact: blocks GNT-03, full editor/debugger parity, and public release.

## BLOCK-PERF-BASELINE: Full five-run performance matrix absent

- Owner: Codex / authorized test host
- State: open gate
- Existing evidence: deterministic 32-agent isolation and 200-agent smoke
  samples pass, but the plan's controlled warmup plus five comparable runs and
  debugger/editor p95 measurements are not complete.
- Release impact: blocks broad performance claims.

## BLOCK-RELEASE: Public release authority is intentionally narrower

- Owner: DominicBytes
- State: source publication authorized; release publication blocked
- Authorized: push the completed Redot port to `dominicbytes/redot-limbo` and
  identify it as the Redot port.
- Not authorized: create or push a version tag, GitHub release, signed binary,
  notarized artifact, or distribution-channel publication.
- Release impact: source may be pushed, but no release claim or release object
  may be created in this task.
