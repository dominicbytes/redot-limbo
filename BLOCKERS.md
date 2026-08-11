# Blockers and release gates

Resolved preflight blockers remain visible in Git history. The Redot binary is
installed, its official API dump is reproducible, and the source/dependency
locks are complete.

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
- Required evidence: 100%/150% UI profiles, task authoring and undo/redo,
  debugger selection, focus/readability, and five enable/disable plus five
  reopen cycles with registration counts and captures.
- Release impact: blocks GNT-03, full editor/debugger parity, and public release.

## BLOCK-PERF-BASELINE: Full five-run oracle performance matrix absent

- Owner: Codex / authorized test host
- State: open gate
- Existing evidence: deterministic 32-agent isolation and four final
  200-agent Windows/Linux samples pass, but the plan's warmup plus five
  comparable runs and
  debugger/editor p95 measurements are not complete.
- Release impact: blocks GNT-02/GNT-03 performance claims.

## BLOCK-PUBLICATION: Repository and release authorization absent

- Owner: DominicBytes
- State: blocked by explicit authorization
- Required decision: choose/authorize the downstream GitHub repository,
  signing/notarization channel, push, tag, and public release.
- Release impact: blocks publication only. No source push, tag, release, signing,
  or notarization operation is authorized by this implementation task.
