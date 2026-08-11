# GNT-01 — Vertical slice

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Frozen scenario

Load the extension, create/save/reload a small `BehaviorTree`, execute it
through direct ticks and `BTPlayer`, mutate a blackboard deterministically,
and inspect the running instance in the editor debugger.

## Evidence

- Class registration, resource save/reload, `RUNNING, RUNNING, SUCCESS`
  traces, blackboard inheritance/linking, and `BTPlayer` pass in the final 1.8
  fixture.
- The expanded 13-case matrix includes scoped runtime blackboard inspection
  introduced in 1.7 and retained in 1.8.
- Final and archive-extracted Windows/Linux editor/release runs pass with zero
  suspicious lines.
- The historical v1.6 Godot/Redot comparison has zero normalized differences;
  it is not used to claim an oracle for the 1.8-only cases.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Semantic fidelity | PASS for the automated tree, blackboard, cargo, and tick traces. |
| Serialization | PASS for the named resource fingerprint and custom script path. |
| Runtime regression | PASS for final and packaged Windows/Linux editor/release runs. |
| Debugger usability | BLOCKED: no visible live-debugger capture or two-frame timing measurement. |
| Unlensed read | The automated vertical slice is implemented; the missing visual step remains release-relevant. |

The automated portion passes, but visible live inspection remains part of the
frozen gate and is not silently inferred from headless initialization.
