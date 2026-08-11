# GNT-02 — Behavior trees and blackboards

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Automated result

The complete 1.8 source passes blackboard scope/linking and runtime inspection,
deep-clone isolation, sequence/selector/parallel/invert/wait semantics,
`BTPlayer`, 32 isolated agents, custom condition/action/decorator/composite
scripts, runtime `BehaviorTreeView`, and a 200-agent sample. Final and packaged
Windows/Linux editor/release profiles pass all 13 cases with zero suspicious
log lines.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Task semantics | PASS for the named representative task cases. |
| Data isolation | PASS for clone, parent/child/link, runtime-inspection, and 32-agent cases. |
| Extension points | PASS for all four typed-GDScript task categories. |
| Coverage | BLOCKED: the full upstream native-test mapping, interruption/subtree recursion matrix, and malformed-script matrix remain incomplete. |
| Performance | BLOCKED: direct, archive, and packed 200-agent smoke samples exist, not the frozen warmup plus five comparable runs. |
| Unlensed read | Representative parity is real, but full task-family/performance parity would be an overclaim. |

No automated regression was found. The gate remains blocked on the explicitly
larger coverage and controlled-performance matrices.
