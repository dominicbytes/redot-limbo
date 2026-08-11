# LimboAI v1.8.0 adopted baseline and Redot delta

Date: 2026-08-11

- Previous compatibility checkpoint: `v1.6.0@91b22a187f7cd701e25eedd6dcff34179795e687`
- Selected feature baseline: `v1.8.0@3fbd85118b924d50c10a495ad5c7175028649d77`
- Range: 56 commits, including 48 non-merge commits
- Result: all upstream source changes in the immutable 1.8 tag are adopted

The earlier 1.6 port established that Redot 26.2 exposes a usable 4.5.2-lineage
GDExtension contract. The owner then selected the full 1.8 feature baseline.
This update merges the exact upstream tag and adapts only failures demonstrated
by Redot compilation, editor initialization, or demo execution.

## Adopted upstream 1.7 feature work

| Area | Adopted commits and behavior | Redot evidence |
| --- | --- | --- |
| Task palette and favorites | `6185835`, `a0eba33`, `84a72cb`, `7b42767`, `46c143c`, `c6e8165` | Source retained; Redot editor initializes. The missing Godot 4.6 theme-setting lookup has a Redot fallback. |
| Task-tree visuals and popups | `8598130`, `ef43b55`, `ab999dc`, `9880722`, `bdf179d`, `7204573`, `7896201` | Source retained; editor classes load. Visible UX remains an explicit gauntlet. |
| HSM transition cargo | `7eaca38` | A dedicated fixture dispatches cargo `25`, observes it in the entered state, and verifies it is cleared afterward. |
| Runtime blackboard inspection | `68814e1` | A dedicated fixture enumerates scoped dynamic properties, reads parent/local values, and edits the parent through the inspection path. |
| Plan editor and documentation | `567d783`, `3adc3d9`, `50cfbd4`, `6339b7b` | Source retained; 4.5 property hints stay guarded and downstream docs target `v1.8.0`. |
| Runtime and editor fixes | `5c80b25`, `b06f54e`, `d352989`, `7665282`, `e1e31cd` | Source retained; clone, blackboard, runtime, and editor initialization checks pass. |
| Upstream tests/versioning | `91545e3`, `215e4fa`, `ea90b0c`, `bd207b5`, `e7b056e`, `e2be164` | Test intent is represented by the GDExtension fixture; final downstream version is `1.8.0+redot.26.2.1`. |

## Adopted upstream 1.8 safety and build work

The complete source retains `7687192`, `c1baa45`, `d739460`, `8ac5462`,
`1277ce5`, `91d02b2`, `9a3a2d4`, `5decbe6`, `6bde12f`, `8501131`, and
`7b3c628`, including the broader `Ref` ownership safety work, missing headers,
editor shutdown fix, GDExtension compile fixes, debugger unregistration, and
dev-build error macros. The 4.6/4.7 baseline/build commits `a2aa156`, `33be10a`,
`a6394cb`, `ec3497e`, `5e9fa65`, `060d1a5`, `78ef8c3`, and the final
`3fbd851` version commit are also present. Redot-specific dependency and CI
locks replace upstream engine-selection behavior without removing LimboAI
features.

## Downstream deviations from the exact tag

| File/area | Redot adaptation | Reason |
| --- | --- | --- |
| `editor/limbo_ai_editor_plugin.cpp` | Construct five stored editor-plugin references as explicit `Ref<T>` values. | The locked Redot C++ binding rejects ambiguous raw-pointer assignment. |
| `editor/task_palette.cpp` | Use the upstream Modern-style check when available; otherwise use flat buttons. | Redot 26.2 uses the modern editor but lacks Godot 4.6's `interface/theme/style` setting. |
| Five demo `.tscn` files | Serialize `AnimationPlayer.libraries` as an equivalent dictionary. | Redot 26.2 loads the 4.6 shorthand without attaching the library, causing missing-animation runtime errors. |
| `util/limbo_utility.cpp` | Retain API-version guards around three property-hint families. | Keeps the source valid for the locked 4.5-lineage binding and historical 4.4 checkpoint. |
| Build/manifest/version files | Fail-closed Redot binding validation, desktop-only mappings, deterministic paths, and downstream version metadata. | Required for reproducible Redot artifacts; no runtime feature is removed. |
| Tests, reports, and package scripts | Add Redot fixture, binary audits, rights separation, deterministic packaging, and evidence. | Downstream verification and distribution infrastructure. |

No upstream 1.7 or 1.8 feature commit is deferred or rejected in the selected
baseline. Changes after `v1.8.0` remain outside this immutable port scope.
