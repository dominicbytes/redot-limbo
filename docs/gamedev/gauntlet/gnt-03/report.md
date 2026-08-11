# GNT-03 — HSM, migration, and editor experience

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Automated result

Typed-GDScript states, setup/enter/update/exit order, event transitions,
transition cargo, `BTState` consumption, re-entry, resource save/reload,
editor-class registration, and clean bounded shutdown pass in the final 1.8
fixture. Cargo value `25` is observed by the destination state's `_enter` and
is cleared afterward.

The complete upstream 1.8 editor work is included: foldable task palette,
dedicated favorites, modern layout, probability overlays, status-highlight
fixes, blackboard runtime inspection, ownership safety, and the editor-close
fix. Headless Redot initialization passes with the narrow theme-setting
fallback; no 1.7/1.8 editor feature was intentionally removed.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| HSM lifecycle | PASS for the named deterministic trace and transition cargo. |
| BT/HSM composition | PASS for the fixture's `BTState` scenario. |
| Migration/serialization | PASS for the named round trip and five adapted demo animation libraries; the complete malformed/external-resource matrix is absent. |
| Editor UX and undo | BLOCKED: no visible task-palette/search/edit/undo session. |
| Accessibility/scaling | BLOCKED: no 100%/150% and 1280x720 capture session. |
| Registration lifecycle | BLOCKED: no five visible enable/disable and five reopen cycles with counts. |
| Unlensed read | Headless evidence cannot substitute for the frozen visible-editor protocol. |

This gate remains fail-closed until an authorized interactive editor session
produces the checklist, counts, timings, logs, and captures.
