# GNT-03 — HSM, migration, and editor experience

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Automated result

Typed-GDScript states, setup/enter/update/exit order, event transitions,
`BTState` consumption, re-entry, resource save/reload, editor-class
registration, and clean bounded shutdown pass in the deterministic fixture.

The later upstream editor-close patch was excluded because its triggering
Godot debugger-dock lifecycle change is absent from the selected 4.5 lineage.
The retained 1.6 lifecycle passed repeated bounded Redot import/runtime runs.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| HSM lifecycle | PASS for the named deterministic trace. |
| BT/HSM composition | PASS for the fixture's `BTState` scenario. |
| Migration/serialization | PARTIAL: the named round trip passes; the complete external/subresource/rename/malformed matrix is absent. |
| Editor UX and undo | BLOCKED: no visible task-palette/search/edit/undo session. |
| Accessibility/scaling | BLOCKED: no 100%/150% and 1280x720 capture session. |
| Registration lifecycle | BLOCKED: no five visible enable/disable and five reopen cycles with counts. |
| Unlensed read | Headless evidence cannot substitute for the frozen visible-editor protocol. |

This gate remains fail-closed until an authorized interactive editor session
produces the checklist, counts, timings, logs, and captures.
