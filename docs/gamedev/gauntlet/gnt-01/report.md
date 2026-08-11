# GNT-01 — Vertical slice

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Frozen scenario

Load the extension, create/save/reload a small `BehaviorTree`, execute it
through direct ticks and `BTPlayer`, mutate a blackboard deterministically,
and inspect the running instance in the editor debugger. Godot 4.5.2 is the
semantic oracle; Redot 26.2 is the target.

## Evidence

- Class registration, resource save/reload, `RUNNING, RUNNING, SUCCESS`
  traces, blackboard inheritance/linking, and `BTPlayer` pass in both engines.
- The normalized Godot/Redot comparison has zero differences across 11 cases.
- Final Windows and Linux editor/release runs pass with zero suspicious lines.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Semantic fidelity | PASS for the automated tree, blackboard, and tick trace. |
| Serialization | PASS for the named resource fingerprint and custom script path. |
| Runtime regression | PASS for final Windows/Linux editor and release runs. |
| Debugger usability | BLOCKED: no visible live-debugger capture or two-frame timing measurement. |
| Unlensed read | The automated vertical slice is implemented; the missing visual step remains release-relevant. |

The automated portion passes, but the frozen scenario includes visible live
inspection. Missing interactive evidence blocks an overall PASS rather than
being silently waived.
