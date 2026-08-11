# Blockers and release gates

The complete upstream LimboAI 1.8 source is now integrated and the local
desktop build/runtime gates pass where executable on the Windows host. The
remaining items limit release claims; they do not mean 1.8 features were
omitted.

## CLOSED-MAC-NATIVE: Native macOS validation complete

- Owner: Codex / hosted workflow
- State: resolved by GitHub Actions run `31476931577` at source commit
  `147004846d91a0e6292dd9d2dc7536c02db14a00`.
- Evidence: both universal frameworks pass architecture, macOS 11.0,
  dependency, install-identity, export, and path-leakage audits. Native editor
  and forced template-release runs each pass all 13 fixture cases with zero
  suspicious lines.
- Release impact: no remaining native macOS runtime blocker; GNT-04 remains
  blocked by the separate visible-authoring and native-export gates.

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
