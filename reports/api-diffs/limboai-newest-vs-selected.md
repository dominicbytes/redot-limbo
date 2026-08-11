# LimboAI v1.8.0 versus selected v1.6.0

Date: 2026-08-10
Selected: `v1.6.0` / `91b22a187f7cd701e25eedd6dcff34179795e687`
Newest evaluated: `v1.8.0` / `3fbd85118b924d50c10a495ad5c7175028649d77`

`v1.8.0` is not a viable Redot 26.2 baseline because it advances the binding
and project content to Godot 4.6 and then adds 4.7 compatibility work. The
selected 1.6 source builds unchanged on the 4.5.2 lineage. The 48 later
non-merge commits are dispositioned below; merge commits add no independent
change beyond these rows.

## Backport or adopt

| Upstream commit | Disposition | Downstream evidence |
| --- | --- | --- |
| `5c80b25` BTCallMethod argument lifetime | Backport | Cherry-picked as `5567065`; runtime fixture passes. |
| `b06f54e` blackboard self-parent guard | Backport | Cherry-picked as `7a9ca78`; blackboard contract passes. |
| `d352989` macOS command shortcuts | Backport | Cherry-picked as `f1fb3f8`; native UI verification remains GNT-03. |
| `7665282` clone deep copy | Backport | Cherry-picked as `175fdde`; clone regression passes. |
| `e1e31cd` inspector refresh after duplication | Backport | Cherry-picked as `9a296cb`; visible editor retest remains GNT-03. |
| `8501131` debugger message unregistration | Backport | Cherry-picked as `ea1c2d8`; headless shutdown is clean. |
| `567d783` missing plan-editor hints | Backport with guard | The three 4.5 hints are enabled only for module builds or GDExtension API 4.5+. Five repeated Redot runs pass, and the guarded code compiles against the selected 4.4 Godot oracle. |
| `91545e3`, `215e4fa`, `ea90b0c` later tests | Adopt test intent | Blackboard-plan and deep-clone behavior are represented in the extension fixture. |
| `3adc3d9` versioned documentation URL | Adopt pattern | Downstream `doc_branch` is `v1.6.0`. |
| `78ef8c3` pin CI actions | Adopt pattern | New Redot workflow pins checkout/upload/download actions by full SHA. |

## Rejected

| Upstream commit | Disposition | Reason |
| --- | --- | --- |
| `9a3a2d4` editor-close crash fix | Reject | The commit responds to Godot `658a237` (floating debugger-dock lifecycle), which is absent from the selected 4.5 lineage. Immediate shutdown was also found to race unchanged v1.6, so it is not valid evidence for importing this 4.6-only ownership change. |

## Deferred: 4.6/4.7 baseline, release, and build work

These commits are deliberately not mixed into a 4.5.2-lineage port:

`a2aa156` README 4.6 support; `33be10a` API 4.6; `a6394cb` demo 4.6
formats; `bd207b5` 1.7-dev version; `6339b7b` 1.7 support docs; `e7b056e`
1.7.0 version; `e2be164` 1.7.1 version; `ec3497e` Godot 4.7 build deps;
`5e9fa65` reusable 4.7 workflow ref resolution; `060d1a5` later artifact
version labeling; and `3fbd851` 1.8.0 version.

## Deferred: later editor and debugger features

These changes form the 1.7 editor experience or rely on its surrounding UI;
none is required by a failing 1.6 oracle:

`6185835` FoldableContainer task palette; `a0eba33` favorite relocation;
`84a72cb` classic-layout removal; `7b42767` modern flat buttons; `46c143c`
GDExtension tooltip removal; `c6e8165` module tooltip fix; `8598130` status
highlight gaps; `ef43b55` probability pill sizing; `ab999dc` probability
overlay; `9880722` probability popup placement; `bdf179d` change-type popup
placement; `7204573` change-type filter focus; `7896201` external-editor
double-click behavior; `68814e1` blackboard runtime inspector; and `50cfbd4`
Input header in the later blackboard plan editor.

## Deferred: later behavior and 4.6/4.7 compile safety

- `7eaca38`: transition-event cargo is a new HSM feature, not a 1.6 repair.
- `7687192`, `c1baa45`, `d739460`, `8ac5462`, `91d02b2`, `5decbe6`,
  `6bde12f`, and `7b3c628`: later missing-header, 4.6/4.7 binding, and
  dev-build compatibility changes are unnecessary in the locked Redot build.
- `1277ce5`: broader `Ref` ownership refactor is deferred because the selected
  baseline and memory-sensitive fixture pass; taking it independently would
  exceed the smallest-proven-delta rule.

Deferred does not mean rejected permanently. A future baseline update must
re-evaluate these commits as one coherent upstream move and rerun every gate.
