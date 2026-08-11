# Implementation plan: Redot LimboAI

- Plan date: 2026-08-10
- Project: `plugins/redot-limboai`
- Target: Redot 26.2 LTS (`26.2.stable.official.4f5b14aba`; Godot/GDExtension lineage `4.5.2 stable`)
- Local research snapshot: `limbonaut/limboai@a6f5c7fc11ff80d512dd75c82cfa85724fd8a742` on `master`
- Selected feature baseline: `v1.8.0@3fbd85118b924d50c10a495ad5c7175028649d77`
- Status: v1.8 integration complete; final package/evidence reconciliation in progress, with v1.6 retained only as the compatibility checkpoint
- Scope authority: [preflight report](preflight-report.md) and [porting specification](../../../redot_plugin_porting_codex_spec.md), section 10

## Approved v1.8 scope amendment

On 2026-08-11, the owner explicitly directed that the complete LimboAI 1.8
feature set be ported to Redot and that it build on the existing 1.6 port. This
supersedes the earlier 1.6-only baseline and out-of-scope decision. Redot stays
locked to 26.2 and its Godot/GDExtension 4.5.2 lineage, so upstream 4.6/4.7
assumptions are compatibility work rather than grounds for omitting 1.8
features. Every affected build, runtime, editor, migration, package, and
platform gate is reopened; prior 1.6 evidence remains historical evidence only.

## Planning state

The user's instruction to plan from the preflight materials is treated as confirmation of the preflight destination and its `ADAPT` direction. The recommendations are planning inputs, not unearned compatibility claims.

### Decisions so far

- Deliver a GDExtension first. A Redot engine-module edition is deferred until the extension passes parity and a module-only benefit is proven.
- Preserve LimboAI class names, methods, signals, settings, resource types, serialized identifiers, and GDScript extension points wherever Redot permits.
- Use the complete `v1.8.0` feature baseline. Preserve its public behavior and editor surface while adapting only proven Godot 4.6/4.7 engine dependencies at narrow compatibility boundaries for Redot 26.2.
- Ship the core addon separately from the CC BY 4.0 logo/demo package.
- The first release targets single-precision Windows x86-64, Linux x86-64, and macOS universal. Other platforms remain later gates.
- Upstream C++ GDExtension code is a scope-authorized exception to the workspace's typed-GDScript baseline. New downstream gameplay fixtures and extension examples use typed GDScript. No C# or .NET lane is included.

### Not yet specified

- The exact source patch, until the generated API/compile report proves a mismatch.
- A release date and signing/notarization identity. Source publication to `dominicbytes/redot-limbo` is authorized; a tag or release is not.
- Later-platform and module support after the desktop GDExtension release.

### Active frontier

Integrate `v1.8.0` into the existing Redot branch, preserve the accepted Redot API/binding contract and downstream validation infrastructure, then use compile/load/runtime/editor failures to identify the smallest required 4.6/4.7 compatibility delta.

## 1. Destination

Deliver an installable Redot 26.2 LimboAI addon that lets a developer create, save, migrate, run, and visually debug behavior trees and hierarchical state machines using the familiar LimboAI editor, resources, blackboards, nodes, and custom typed-GDScript tasks/states.

The first release is complete only when:

- a full upstream source baseline, dependency revision, source license, logo license, demo-asset license, Redot engine identity, API source, and Redot C++ binding are pinned by full hashes;
- the core GDExtension builds reproducibly for Windows x86-64, Linux x86-64, and macOS universal without writing generated output into the source tree;
- `BehaviorTree`, `BTPlayer`, built-in tasks, blackboards, subtrees, `LimboState`, `LimboHSM`, `BTState`, custom GDScript tasks/states, editor tools, runtime debugger, `BehaviorTreeView`, and performance monitors pass their named tests;
- a fixture authored in the selected Godot baseline loads, runs, saves, and reloads in Redot without missing classes, identifier rewrites, or semantic corruption;
- repeated editor enable/disable and reopen cycles create no duplicate dock, inspector, debugger, class, setting, or performance-monitor registrations;
- a game export containing custom GDScript tasks and states loads the release library and executes a real behavior-tree/HSM scenario outside the editor;
- clean-install archives, manifests, native dependency reports, notices, checksums, limitations, migration notes, and an upstream-sync report pass; and
- no crash, timeout, failed native load, parse/resource error, unexplained warning, or unsupported parity claim remains.

The release is gate-driven. No calendar commitment is inferred.

## 2. Audience and constraints

| Area | Confirmed constraint |
| --- | --- |
| User | Redot 26.2 game developers who need visual behavior trees, blackboards, HSMs, runtime inspection, and GDScript customization. |
| Primary development host | Windows x86-64. |
| Required release hosts | Windows x86-64, Linux x86-64, and macOS universal. |
| Input and UI | Keyboard and mouse in the Redot editor; normal game input is owned by each user's project, not LimboAI. |
| Runtime and language | Existing C++ GDExtension plus typed-GDScript fixture/custom-task coverage. No C#, .NET, or new runtime language. |
| Engine | Exact Redot editor `26.2.stable.official.4f5b14aba`, engine commit `4f5b14abade2239104847d03d8f9056e4467cfcd`, single precision. |
| Binding | Redot C++ branch `26.2`, candidate commit `598ec78e86b2c240a023f6de13daba70f7de8610`; it must be revalidated and locked in this repository. |
| Build | SCons, a pinned binding checkout, and external build/deploy roots. The current automatic `godot-cpp` clone is not sufficient release provenance. |
| Sessions | Editor authoring may be long-lived; runtime fixtures are bounded, deterministic runs. |
| Performance | Freeze same-machine selected-Godot baselines before port changes. Do not claim a numeric parity result without the baseline and exact scenario. |
| Accessibility | Preserve Redot theme, scale, keyboard focus, and non-color status cues; verify 100% and 150% editor scale and a 1280x720 minimum viewport. |
| Team and budget | Owner: DominicBytes. Planning and implementation agent: Codex. No budget or staffing expansion was supplied. |
| Schedule | Gate-driven; no date promised. GitHub publication and macOS evidence may require external authorization/runners. |

## 3. Design pillars

1. **Compatibility before novelty.** A migrated LimboAI project should replace the package and rebuild, not rewrite AI gameplay code or resources.
2. **Evidence before patches.** Select the source and freeze the API/resource/editor oracles before changing engine-facing code.
3. **Smallest reviewable delta.** Keep upstream architecture and isolate Redot differences in existing build and compatibility boundaries unless a failing test proves otherwise.
4. **One end-to-end slice first.** Prove editor creation, resource persistence, runtime execution, and live debugging with one deterministic tree before expanding feature coverage.
5. **Fail-closed release claims.** A missing platform, unproven license, API ambiguity, crash, warning, or manual editor gate blocks the associated claim.
6. **Maintainable downstream.** Preserve upstream history, separate adaptation commits, and make every upstream update produce a dependency/license/API/resource/test impact report.

## 4. Plugin behavior and rules

### 4.1 Installation and lifecycle

- The core package installs under `addons/limboai/` with its `.gdextension` manifest, native libraries, icons, source license, version, and compatibility documentation.
- Redot loads the extension at scene initialization; runtime classes retain upstream names.
- Editor initialization registers the existing LimboAI editor plugin, inspector plugins, debugger plugin, settings, icons, and monitors. It does not introduce a GDScript `plugin.cfg` shim.
- Disable/enable, project close/reopen, and extension shutdown remove every registration created during initialization. Five consecutive cycles must not duplicate state or leak editor objects.

### 4.2 Behavior-tree workflow

1. Create or load a `BehaviorTree` resource.
2. Compose supported composite, decorator, condition, action, comment, and utility tasks.
3. Configure a `BlackboardPlan`, variables, scopes, parameters, and subtrees.
4. Assign the tree to `BTPlayer` or compose it through `BTState`.
5. Run the scene and observe deterministic `FRESH`, `RUNNING`, `SUCCESS`, and `FAILURE` behavior as defined by the selected upstream baseline.
6. Inspect the live instance in the runtime debugger or a `BehaviorTreeView`.

Save, reload, duplicate, rename, reorder, and subtree reuse must preserve task order, types, exported values, resource paths, and ownership. Recursive or invalid subtrees must fail clearly without stack overflow, editor crash, or silent corruption.

### 4.3 Blackboard rules

- Default values, scene/player overrides, types, scopes, parameters, node-path resolution, and intentional cross-agent sharing match the selected baseline.
- Missing variables, type mismatches, invalid properties, and invalid node paths emit bounded, actionable failures and never mutate unrelated entries.
- A resource round trip must preserve every supported Variant type and identifier used by the selected baseline.

### 4.4 Custom GDScript extension points

- Typed GDScript action, condition, decorator, and composite tasks can extend the supported native bases without engine-specific rewrites.
- Typed GDScript `LimboState` subclasses receive the expected lifecycle callbacks and can participate in nested HSMs and event transitions.
- Exported properties, hints, documentation, editor palette discovery, inspector controls, reload, and game export all work.
- Script parse failure or an invalid base class is reported without taking down the editor plugin.

### 4.5 HSM rules

- `LimboState` and `LimboHSM` support nested machines, initial states, event-based transitions, reentry policy, callback delegation, and invalid-transition handling as defined by the selected baseline.
- `BTState` starts, updates, and stops its tree consistently with state entry, update, and exit.
- Simultaneous transition requests use the selected upstream ordering; the oracle must record the exact winner and callbacks before the Redot port is evaluated.

### 4.6 Failure and recovery

- Missing native libraries, symbols, scripts, resources, or editor dependencies fail with a clear load error and a non-passing test result.
- Invalid trees/resources remain inspectable when Redot permits and are never silently rewritten into a different valid structure.
- An interrupted save, editor restart, or failed task script reload leaves the last valid resource reopenable.
- A timeout, crash, parse/load error, unexplained warning, semantic mismatch, or registration leak is a failed gate.

### 4.7 Content boundary

- The core archive contains only the addon, native desktop libraries, source license/notices, version, installation, compatibility, limitations, and migration documentation.
- The logo and demo/tutorial are separate CC BY 4.0 artifacts with their own attribution. They are not required to install the core addon.
- Build caches, binding checkouts, API scratch files, fixture outputs, logs, test-only binaries, credentials, and local paths never enter a release archive.

## 5. Presentation

- Preserve the upstream behavior-tree workspace, task palette, tree search, blackboard editor, inspector controls, debugger tab, toolbar actions, icons, and status visualization unless a Redot API difference forces an adaptation.
- Follow Redot's active editor theme and scale. Do not hard-code colors when a theme token exists, and do not rely on color alone to communicate running/success/failure.
- Keep the upstream icon set and attribution. No new Blender, Blockbench, GPT Image, animation, VFX, music, or sound pipeline is required.
- Canonical editor captures use the selected upstream Godot baseline and Redot 26.2 at 1920x1080, 100% scale, default dark theme; accessibility captures add 1280x720 at 150% scale.
- Visual comparison uses layout bounds, clipping, focus order, labels, icons, task-state cues, selection, and debugger timing. Raw pixel equality is not the sole oracle.

## 6. Technical design

### 6.1 Current architecture observed

- The local nested repository is a shallow `master` checkout at `a6f5c7fc11ff80d512dd75c82cfa85724fd8a742`; `limboai_version.py` identifies it as `1.8.0` and `deps.env` targets Godot/godot-cpp 4.6.
- `SConstruct` builds the GDExtension, auto-clones `godot-cpp` when absent, generates version/doc data, updates the manifest icons, and deploys into `demo/addons/limboai/`.
- `SCsub` is the optional engine-module lane. The 53 C++ `TEST_CASE` declarations are exercised by the module-oriented upstream test workflow, not by the packaged GDExtension.
- `register_types.cpp` registers runtime/resource classes at scene initialization and the editor, inspector, debugger, and tree UI types at editor initialization.
- Runtime/data areas are `bt/`, `blackboard/`, `hsm/`, and `util/`; Redot/Godot adaptation is already concentrated in `compat/` and build/registration files.
- Editor areas are `editor/`, `editor/debugger/`, and 91 XML class documents. The demo contains 27 GDScript files and representative `.tres`/`.tscn` content.
- `gdextension/limboai.gdextension` declares desktop, mobile, and Web library paths plus icons. No native library is currently deployed in the local demo.

### 6.2 Target architecture

- Retain the upstream directory structure, C++ class graph, initialization levels, and manifest. Do not wrap the product in a second editor plugin or event bus.
- Preserve the `godot-cpp/` build slot for the first experiment, but populate it with the exact Redot C++ revision and pass the accepted custom/source-backed API. Patch `SConstruct` only if the no-source-change route cannot express the pinned dependency and external output requirements.
- Place proven engine-facing differences in the existing `compat/` layer or the narrow registration/build call site. Direct feature rewrites require a failing oracle case and an ADR.
- Keep `demo/` as upstream demonstration content. Add one smaller deterministic Redot fixture for automated comparison and clean-install/export tests.
- Use typed GDScript fixture tasks/states to prove downstream extension points. Do not recreate native behavior in GDScript.
- Keep API dumps, binding checkouts, builds, logs, captures, and packages outside the nested source repository or under explicitly ignored evidence paths.

### 6.3 Data and compatibility contracts

- Public names and signatures come from the selected upstream class docs/source and the accepted Redot API/binding evidence.
- Serialized-resource identity includes resource type, script/base class, property names/types, task order, subresource identity, external paths, node paths, blackboard keys/types/defaults, and subtree/HSM references.
- A canonical semantic fingerprint script normalizes non-semantic ordering/formatting and compares the model before and after Godot-to-Redot load/save. Raw file hashes alone are insufficient because lawful serialization formatting may differ.
- Fixture expectations are machine-readable JSON: engine/source hashes, setup, inputs, tick/status sequence, transitions, callbacks, blackboard snapshots, resource fingerprint, editor registration counts, logs, captures, and cleanup state.
- Runtime fixtures are independent; no catch-all mutable global singleton is introduced.

### 6.4 Expected additions and touch points

Paths are created only when their first named task starts.

```text
reports/api-diffs/limboai-newest-vs-selected.md
reports/api-diffs/limboai-redot-contract.md
reports/licenses/limboai-package-audit.md
reports/upstream-sync/<from>-to-<to>.md
reports/test-results/<milestone>/
tests/fixture/project.godot
tests/fixture/test_runner.gd
tests/fixture/tasks/record_ticks.gd
tests/fixture/states/record_state.gd
tests/fixture/fixtures/
tests/migration-fixtures/godot-4.5.2/
scripts/run_fixture.py
scripts/compare_resource_fingerprint.py
scripts/verify_registration.py
scripts/package_release.py
docs/gamedev/gauntlet/
```

Expected existing-file touch points are `deps.env`, `SConstruct`, `gdextension/limboai.gdextension`, only proven files under `compat/`, `register_types.cpp` only if registration evidence requires it, `.github/workflows/`, `.gitignore`, `README.md`, `UPSTREAM_LOCK.md`, `DECISIONS.md`, `BLOCKERS.md`, and `TODO.md`.

Generated outputs use `plugins/build/redot-limboai/` and `plugins/dist/redot-limboai/`, not the nested source tree.

### 6.5 Verified Redot constraints

- `.codex/redot.env` resolves the installed console launcher and editor. The launcher reports `26.2.stable.official.4f5b14aba`; hashes are `5633D02A28A73514084DF6A60FFE01FABDBBB9AC5E28FDFD590ED47277F51989` (console launcher) and `10DFBEFC273536F0C65903D6429E531C30133820BF0FA842F2D6E6FB81DB1D42` (editor).
- The official engine is single precision and identifies the Godot API lineage as 4.5.2.
- On 2026-08-10, `--headless --dump-extension-api` reproducibly crashed with signal 11, exit `-1073741819`, and produced no file. The old blocker reason "`REDOT_BIN` is empty" is superseded; the API-generation defect remains.
- A source-backed Redot C++ API candidate has SHA-256 `453A0CC128BB58333A001F7F43573A5961D973FB7B151AF43139869F22D5915C`; the interface header has SHA-256 `4CD695E86B92E2BF4E60BBE19CE137FAF41205DA1CF94F29E069AFEC0F7BF320`.
- A second local `extension_api.json` has SHA-256 `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577` and declares the correct product/lineage, but its provenance must be reconciled before use.
- The first compatibility milestone must accept a documented source-backed API exception only after engine-source comparison, binding generation, compile, native load, class registration, and runtime behavior agree. API metadata alone is not proof.

## 7. Preflight research brief

Detailed research is in [preflight-report.md](preflight-report.md). No new external research is commissioned by this plan; implementation closes the following evidence questions.

| Question | Influenced decision | Required evidence | Stopping rule |
| --- | --- | --- | --- |
| Which upstream source is the release baseline? | Version, omissions, patch history. | Full history/tags; newest stable no-change attempt; newest `1.6.x` attempt; selected Godot run; release notes and source diff. | One full commit is selected, reproducible, and justified; `limboai-newest-vs-selected.md` lists every later feature/fix disposition. |
| Which Redot API artifact is authoritative when the official dumper crashes? | Binding generation and compatibility claim. | Exact binaries/hashes, crash reproduction, engine source, Redot C++ 26.2 API/interface, both local API files, compile/load/runtime results. | An accepted ADR identifies one binding input, rejects/labels the other, and all contract/build/load probes agree. |
| What is the smallest Redot patch? | Files and maintenance burden. | Generated class/method/enum report, compiler diagnostics, editor API audit, failing fixture cases. | Every changed source line traces to a named mismatch or failing case; no speculative adapter remains. |
| Are serialized resources migration-safe? | Public compatibility and release claim. | Godot-authored BT/blackboard/subtree/HSM fixtures, normalized fingerprints, Redot save/reload, runtime traces. | Every supported fixture has exact semantic equality or an approved migration rule, script/manual path, and regression case. |
| Does the defining editor/debugger experience survive? | Editor release gate. | Canonical upstream and Redot captures, lifecycle counts, focus/layout checks, live debugger timing, logs. | The editor Gauntlet passes at both UI profiles with no duplicate registration or unexplained warning. |
| What may be redistributed? | Core/demo package split. | Source/logo/demo licenses, asset inventory, native dependency audit, archive inventory. | Every shipped file maps to a license/notice and approved package; unclassified assets are excluded. |

Evidence must be primary/local where possible, tied to exact hashes, and stop once the named decision is resolved. The research excludes a new AI framework, a UI redesign, module-first delivery, current-master parity claims, and unaudited binary reuse.

## 8. Preflight findings

| Evidence | State | Plan consequence |
| --- | --- | --- |
| Upstream 1.7.x/1.8.x target Godot 4.6+, while Redot 26.2 exposes the 4.5.2 lineage. | OBSERVED in the 2026-08-09 preflight. | Owner-authorized scope override: port the full v1.8.0 feature baseline and treat 4.6/4.7 assumptions as explicit compatibility work. |
| Candidate `v1.6.0` resolves to `91b22a187f7cd701e25eedd6dcff34179795e687`. | OBSERVED metadata; local object BLOCKED. | Fetch full tags and verify the object before it can become the implementation baseline. |
| The local source is shallow `master` at `a6f5c7fc11ff80d512dd75c82cfa85724fd8a742`, identifies as 1.8.0, and targets Godot 4.6. | OBSERVED. | Preserve it as research/latest comparison only; do not port this snapshot by default. |
| No binding checkout or deployed GDExtension exists locally. | OBSERVED. | The first build tasks must create external, pinned dependency and deploy roots. |
| The source exposes behavior trees, blackboards, HSMs, editor tools, debugger, runtime view, performance monitors, 53 native tests, 91 class docs, and GDScript demo extensions. | OBSERVED. | Scope and test mapping are concrete; module-only native tests need GDExtension-equivalent fixture coverage. |
| Runtime classes register at scene initialization; editor types/plugins register at editor initialization. | OBSERVED. | Registration/lifecycle is a high-risk oracle, not a generic `plugin.cfg` task. |
| The installed Redot binary is now available and verified, but its API dump crashes. | OBSERVED on 2026-08-10. | Replace the stale empty-variable blocker with the API-source exception gate. |
| Source is MIT; the logo and demo graphics are CC BY 4.0. | OBSERVED. | Retain source notices and publish core/demo separately with explicit attribution. |
| Upstream GDExtension CI covers desktop plus later platforms; unit tests are compiled in an engine-module job. | OBSERVED. | Reuse/adapt the desktop CI shape; defer later targets and translate critical native behavior to the extension fixture. |
| Public downstream fork `dominicbytes/redot-limbo` exists and source updates are authorized. | RESOLVED for source publication. | Push only verified source; tags, releases, signing, and notarization remain separately gated. |

Adopt the upstream data model, editor experience, docs, and test semantics. Adapt binding/build inputs, narrow engine-facing compatibility points, deterministic fixtures, packaging, CI, and attribution. Reject a source-only copy without history, an unpinned master port, a new GDScript reimplementation, and a module-first release.

## 9. Milestones

| ID | Sequence | Runnable, observable outcome | Dependencies | Acceptance and evidence | Status |
| --- | ---: | --- | --- | --- | --- |
| MS-005 | 1 | **Upstream and rights lock.** The selected unmodified baseline builds and its demo/tests run under its supported Godot version. | Full fetch/tags; selected Godot binary/toolchain. | Full commit/dependencies/licenses in `UPSTREAM_LOCK.md`; baseline-delta report; source and asset inventory. | Complete for exact v1.8 tag and rights lock |
| MS-015 | 2 | **Redot contract and load.** Exact Redot bindings build the selected source or expose a source-level blocker; a minimal Redot project loads the extension and registers core/editor classes. | MS-005; API-exception ADR; Redot C++ lock. | Contract report; external debug build; bounded editor/runtime initialization; clean logs. | Complete for Windows/Linux; macOS structural only |
| MS-025 | 3 | **First end-to-end vertical slice.** A developer creates/saves a small tree, runs it through `BTPlayer`, observes deterministic state/blackboard output, and inspects it live. | MS-015; GNT-01 oracle frozen. | Minimum fixture/capture harness; semantic fingerprints and tick traces; editor/debugger captures; GNT-01 PASS. | Automated slice complete; visible debugger gate open |
| MS-035 | 4 | **Behavior-tree and blackboard parity.** Built-in task families, interruption, blackboards, subtrees, multi-agent behavior, custom GDScript task categories, and runtime view pass. | MS-025. | Machine-readable scenario matrix; upstream native-test mapping; resource and extension-point reports; GNT-02 PASS. | Representative runtime matrix complete; full/performance gates open |
| MS-045 | 5 | **HSM, migration, and editor parity.** Nested HSMs, events, callbacks, `BTState`, custom states, migrated resources, editor lifecycle, debugger, monitors, and accessibility pass. | MS-035. | Migration matrix; editor checklist/captures; lifecycle counts; performance sample; GNT-03 PASS. | HSM cargo/runtime complete; visible editor gate open |
| MS-055 | 6 | **Desktop release candidate.** Windows/Linux/macOS packages build, audit, install, export, and document the exact supported scope. | MS-045; hosted macOS runner; publication authorization for release step. | Platform binaries/dependencies; clean-install/export logs; notices/checksums; upstream-sync report; GNT-04 PASS. | Local desktop builds pass; final package/native macOS gates open |

## 10. Task breakdown

### MS-005 - Upstream and rights lock

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-001 | Reconcile the shallow research checkout and planning records. | Current local source and preflight. | Git refs/remotes; `BLOCKERS.md`, `TODO.md`, `DECISIONS.md`; source-of-truth workbook. | Full status is recorded without deleting local planning files; stale empty-`REDOT_BIN` wording is superseded by the reproducible dump crash; no port source changes occur. |
| LIM-002 | Fetch full history/tags and select the baseline by the mandated procedure. | Network access; immutable upstream. | Git refs; external baseline worktree; `reports/api-diffs/limboai-newest-vs-selected.md`. | Attempt newest stable unchanged; if it uses unavailable 4.6+ API, test newest `1.6.x`; selected full SHA builds/runs under its supported Godot; all omitted later features/fixes are Adopt/Backport/Defer/Reject with evidence. |
| LIM-003 | Complete provenance, dependency, and rights locks. | LIM-002. | `UPSTREAM_LOCK.md`; `LICENSE.md`; `LOGO_LICENSE.md`; `demo/LICENSE_ASSETS.md`; workflow action/dependency pins; license report. | Source, binding, tools/actions, demo/logo assets, release targets, fetch date, and licenses have full versions/hashes; no unclassified file is approved for packaging. |

### MS-015 - Redot contract and load

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-004 | Freeze the exact Redot/API/binding contract and resolve the dump exception. | LIM-003; installed Redot and source evidence. | Shared API evidence; external `redot-cpp`; `DECISIONS.md`; `reports/api-diffs/limboai-redot-contract.md`; `UPSTREAM_LOCK.md`. | Binary/version/hash and crash reproduction are recorded; the `453A...` and `177E...` API artifacts are compared; one binding input is accepted by ADR; engine source, interface, precision, class/method/enum surface, and redot-cpp SHA have no unexplained row. |
| LIM-005 | Attempt an unmodified selected-source GDExtension build against the accepted Redot binding. | LIM-004; SCons/compiler. | External build root; pinned `godot-cpp/` slot; unchanged `SConstruct`; build log. | Debug/editor library compiles with recorded command; output stays external; compiler warnings are zero or narrowly explained; failure records the first unavailable API and smallest next experiment. |
| LIM-006 | Apply only the proven Redot build/compatibility delta and load it. | LIM-005 failure or successful no-change proof. | `deps.env`, `SConstruct`, manifest, existing `compat/` or narrow registration files, minimal fixture. | Diff maps every line to the contract/build report; Redot loads the library, core/editor classes and icons register once, shutdown is clean, and a bounded editor plus runtime initialization emits no unexplained warning/error. |

### MS-025 - First end-to-end vertical slice

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-007 | Add the minimum deterministic comparison and capture harness. | LIM-006; GNT-01 references fixed. | `tests/fixture/`, typed `record_ticks.gd`, `scripts/run_fixture.py`, result schema, log scanner, capture instructions. | One command creates an isolated run, records exact hashes/seed/profile, enforces wall-clock timeout, returns nonzero/machine-readable failure, scans logs, and writes evidence outside source. |
| LIM-008 | Prove one tree from editor/resource to runtime result. | LIM-007. | Small `BehaviorTree`, `BlackboardPlan`, `BTPlayer` scene, expected JSON. | In the selected Godot baseline and Redot: create/save/reload the tree; custom task returns `RUNNING` twice then `SUCCESS`; final blackboard `ticks` is `3`; semantic fingerprints agree; a duplicate and rename retain identity. |
| LIM-009 | Prove live editor/debugger observation and lifecycle for the slice. | LIM-008. | Manual checklist; canonical captures; registration report. | Tree edits, undo/redo, save, play, agent selection, live task-state update, and stop all work; enable/disable twice and reopen once produce one dock/debugger/monitor set; GNT-01 passes. |

### MS-035 - Behavior-tree and blackboard parity

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-010 | Map and prove built-in task semantics. | MS-025. | Upstream 53-test inventory; fixture cases; source changes only on failure. | Success/failure/running, empty composites, ordering, random seeds, decorators, limits/delays, animation/property/call tasks, interruption, abort/restart, disabled roots, and error paths match selected baseline traces. |
| LIM-011 | Prove blackboards, parameters, scopes, subtrees, and multi-agent isolation. | LIM-010. | Resource fixtures and result snapshots. | Supported defaults/types/overrides/scopes/node references persist; shared entries share only when configured; 32 simultaneous agents remain isolated otherwise; subtree reuse passes; direct/indirect recursion fails safely. |
| LIM-012 | Prove all custom typed-GDScript task categories and inspector behavior. | LIM-011. | Typed action/condition/decorator/composite scripts; palette/inspector cases; export fixture. | Scripts parse, appear where expected, expose typed properties/hints, run, reload, and survive editor restart; invalid base/parse cases fail safely; no downstream API rewrite is needed. |
| LIM-013 | Prove `BehaviorTreeView`, debugger data, and performance monitors in runtime scope. | LIM-012. | Runtime UI scene; monitor/lifecycle assertions; performance capture. | View follows the target instance; debugger data reflects task state within two processed frames; monitors register/clean up once; fixed 200-agent scenario meets GNT-02 performance tolerances. |

### MS-045 - HSM, migration, and editor parity

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-014 | Prove nested HSM behavior and typed-GDScript states. | MS-035. | HSM scenes, `record_state.gd`, event/callback traces. | Initial/nested states, valid/invalid events, reentry, callback order, transition contention, secondary state-machine child behavior selected for the baseline, and restart all match the oracle. |
| LIM-015 | Prove `BTState` composition and failure recovery. | LIM-014. | BT/HSM combined fixtures. | Enter starts one tree, update advances once per expected tick, exit aborts/cleans it, reentry resets per upstream, tree failure does not corrupt HSM state, and invalid configuration is actionable. |
| LIM-016 | Build and pass the Godot-to-Redot migration matrix. | LIM-015. | `tests/migration-fixtures/godot-4.5.2/`; fingerprint tool; migration report. | BTs, blackboards, subtrees, custom tasks, HSM scenes, external/subresources, renamed paths, and malformed fixtures load as expected; save/reload has semantic equality; every intentional difference has migration instructions and regression coverage. |
| LIM-017 | Close editor lifecycle, UX, accessibility, and performance parity. | LIM-016; visible editor. | Editor checklist/captures, lifecycle counters, timing/memory results. | Five enable/disable and five reopen cycles are clean; task palette/search/edit/undo/inspector/debugger work at both UI profiles; no clipping/focus trap/color-only state; GNT-03 passes. |

### MS-055 - Desktop release candidate

| Task | Outcome and trace | Dependencies | Expected files/systems | Acceptance checks and verification |
| --- | --- | --- | --- | --- |
| LIM-018 | Build and audit the desktop editor/template matrix. | MS-045; platform toolchains. | Adapted CI; external Windows/Linux/macOS builds; manifest; dependency reports. | Same locks produce Windows x86-64, Linux x86-64, and macOS universal editor and template-release libraries; architectures, manifest paths, dependencies, symbols, path leakage, and warnings pass. |
| LIM-019 | Prove clean install and game export. | LIM-018; export presets/templates. | Clean fixture project; debug/release exports; logs and inventories. | Core archive installs into an empty Redot project; editor authoring works; exported game loads only required runtime libraries and executes custom task/state scenarios; no editor-only/test/demo file leaks. |
| LIM-020 | Build deterministic core and demo packages with complete documentation. | LIM-019; rights lock. | `scripts/package_release.py`; README; compatibility/limitations/migration docs; licenses/notices; checksums. | Version is `<selected-upstream>+redot.26.2.1`; two reproducible runs match; core/demo split and CC BY attribution are correct; archive inventory has no unapproved file. |
| LIM-021 | Validate upstream maintenance and publish only with authorization. | LIM-020; owner-approved repository; GNT-04. | Workflow, upstream-sync report, source branch/tag, release artifacts. | One dry-run upstream sync reports code/dependency/license/API/resource/test impact; all control files/workbook agree; source and artifact hashes match; GNT-04 passes before public release. |

## 11. QA strategy

### 11.1 Test layers

| Layer | Purpose | Required evidence |
| --- | --- | --- |
| Provenance/static | Detect shallow/unpinned source, dirty generated output, formatting, stale manifests, and notice drift. | Git status/diff checks, full lock validator, pre-commit/native format checks, archive inventory. |
| API/build | Detect Redot binding, class, method, enum, editor API, manifest, precision, and initialization mismatches. | Exact contract report, compiler logs, load/register/shutdown results. |
| Resource | Detect serialization or migration corruption. | Godot-authored fixtures, normalized fingerprints, load/save/reload results, path/subresource checks. |
| Runtime | Prove task status, blackboard, subtree, multi-agent, HSM, custom-script, view, and monitor behavior. | Deterministic JSON traces, fixed seeds, bounded Redot runs, upstream-test mapping. |
| Interactive editor | Prove task authoring, inspectors, undo/redo, dock/search, live debugger, lifecycle, focus, and scaling. | Structured checklist, counts, canonical captures, clean logs. |
| Performance | Detect material runtime/debugger regression and leaks. | Same-machine baseline, warmup plus five runs, frame-time/memory/registration results. |
| Export/package | Prove native layouts, runtime loading, clean install, licenses, and absence of editor/test leakage. | Platform dependency reports, exports, archive manifests, checksums, GNT-04. |

### 11.2 Canonical scenario matrix

The deterministic fixture covers:

- a single end-to-end tree with a typed GDScript task returning `RUNNING`, `RUNNING`, `SUCCESS` and final `ticks = 3`;
- success/failure/running and empty composite/decorator cases from the upstream native tests;
- fixed-seed random tasks, abort/interruption/restart, disabled roots, time/run limits, and animation/property/call failures;
- every supported blackboard value family, default/override/scope/parameter/node reference, explicit sharing, and isolation across 32 agents;
- local/external subtrees, rename/move, missing subtree, direct recursion, and indirect recursion;
- typed GDScript action, condition, decorator, composite, and state scripts, including invalid base and parse failure;
- nested HSM, valid/invalid events, reentry, competing transitions, lifecycle callback order, and `BTState` composition;
- live debugger selection, `BehaviorTreeView`, performance monitor registration/cleanup, repeated editor lifecycle, and project reopen;
- selected-Godot-authored `.tres`/`.tscn` resources loaded and resaved by Redot; and
- clean addon install plus exported debug/release game execution.

Each result records source/engine/API/binding hashes, platform/architecture/precision, seed, viewport/theme/scale when relevant, setup, inputs, status/transition/callback trace, blackboard snapshot, resource fingerprint, elapsed time, memory, log path, capture path, and cleanup result.

### 11.3 Execution policy

- Resolve Redot from `.codex/redot.env` or `REDOT_BIN`, then run `"<REDOT_BIN>" --version` before engine work.
- Validate build/parse/load failures first, then resource errors, runtime behavior, editor behavior, warnings, performance, and packaging.
- Never use `-d` in automation. Headless editor initialization uses `--quit-after 5` or longer; runtime scenarios use an explicit quit condition plus a wall-clock timeout.
- Use the project `redot-project-tools` static checker and bounded runner for the fixture, and scan combined logs for `ERROR:`, `SCRIPT ERROR:`, `FATAL:`, `CRASH`, segmentation faults, unhandled exceptions, failed loads, missing symbols, and `WARNING:`.
- Every allowed warning has an exact narrow match, explanation, owner, and expiry. An unexplained warning fails.
- Repeat a failed deterministic case once from a fresh isolated root. A second identical failure is product/test work, not a flaky pass.
- Review source diffs, generated resources, native dependencies, and archive inventories at every milestone boundary.

### 11.4 Adversarial Gauntlet gates

#### GNT-01 - Source, API, build, registration, and first vertical slice

- **Frozen references:** local latest comparison `a6f5c7fc11ff80d512dd75c82cfa85724fd8a742` (`OBSERVED`); candidate `v1.6.0@91b22a187f7cd701e25eedd6dcff34179795e687` (`OBSERVED` metadata, checkout `BLOCKED`); selected Godot 4.5.2 binary and unmodified run (`BLOCKED`); Redot editor/launcher and hashes above (`OBSERVED`); official dump crash with no output (`OBSERVED`); source-backed API `453A...` and interface `4CD...` (`OBSERVED`); local API `177E...` (provenance `BLOCKED`).
- **Scenario:** on Windows x86-64 single precision, build and run the selected source unchanged under its supported Godot; build the same source against the accepted Redot binding in an external directory; load a clean fixture in a bounded Redot editor/runtime run; create/save/reload the three-tick tree; run it; select it in the debugger; stop and unload. Canonical editor profile is 1920x1080, 100%, default dark theme.
- **Measures and tolerances:** selected source/dependency/API hashes exact; all required runtime/editor classes present; one dock/debugger/monitor registration; no missing symbol or source-tree output; semantic resource fingerprint exact; status trace exactly `RUNNING`, `RUNNING`, `SUCCESS`; `ticks` exactly `3`; debugger reflects each transition within two processed frames; zero crash/error/unexplained warning.
- **Allowed differences:** Redot branding/version strings, platform library names, lawful serializer formatting ignored by the semantic fingerprint, and theme rendering. No missing public class, renamed identifier, or silent resource rewrite is allowed.
- **Critics:** provenance/supply-chain lens, C++ API/ABI lens, resource-identity lens, editor-lifecycle lens, and one unlensed read-only critic.
- **Retest/capture:** rebuild from a clean external root; regenerate the fixture; run Godot then Redot with the same seed; recapture logs, result JSON, semantic fingerprints, registration report, and canonical screenshots under `docs/gamedev/gauntlet/gnt-01/`.
- **Verdict:** `PASS` only when all measures pass. `FAIL` for a mismatch, warning, crash, timeout, or unexplained patch. `BLOCKED` while the source/API oracle is incomplete. Failure blocks every port source change beyond the smallest experiment. Round cap: 3.

#### GNT-02 - Behavior-tree, blackboard, GDScript, and performance identity

- **Frozen references:** selected-source 53 native tests and class docs (`BLOCKED` until checkout); selected-Godot fixture results/resources (`BLOCKED`); fixed fixture scripts/data/seed and exact hashes from GNT-01 (`BLOCKED` until created).
- **Scenario:** run the canonical BT/blackboard/subtree/custom-task matrix on selected Godot and Redot; then run 200 identical agents for 600 physics frames after 120 warmup frames, five fresh runs per engine, with debugger closed and then one agent inspected.
- **Measures and tolerances:** exact task status/order/abort traces; exact blackboard snapshots; semantic fingerprints exact; no cross-agent mutation outside explicit shared scope; recursion fails without crash; custom scripts require no downstream rewrite; median non-debug frame time no worse than 1.20x baseline and p95 no worse than 1.25x; stable-phase memory growth no more than 5%; debugger-open overhead is reported and may not create unbounded growth.
- **Allowed differences:** timing within the stated bands, engine allocator totals, file formatting, and theme visuals. Functional traces and data identities have zero tolerance unless an approved upstream/Redot difference has migration guidance.
- **Critics:** behavior-semantics lens, data-isolation lens, GDScript extension/API lens, performance/leak lens, and one unlensed read-only critic.
- **Retest/capture:** clean fixture root, fixed seed, identical build class, five runs, result/fingerprint/performance JSON, memory sample, and log scan under `docs/gamedev/gauntlet/gnt-02/`.
- **Verdict:** `PASS` for complete functional identity and performance bands; `FAIL` for any deterministic semantic mismatch, leak, or unexplained warning; `BLOCKED` if the baseline or required platform profile cannot run. Failure blocks the behavior-parity claim. Round cap: 3.

#### GNT-03 - Editor, debugger, migration, and accessibility identity

- **Frozen references:** selected upstream editor/debugger captures generated before port changes (`BLOCKED`); current upstream documentation images (`OBSERVED`, contextual only); selected-Godot migration resources/fingerprints (`BLOCKED`); Redot editor profile and upstream icon/license files (`OBSERVED`).
- **Scenario:** at 1920x1080/100% and 1280x720/150%, create/edit/reorder/search a tree, edit a blackboard, use undo/redo, save/reopen, run two agents, switch debugger target, inspect state changes, stop, then perform five disable/enable and five full reopen cycles. Load/save the complete migration fixture set.
- **Measures and tolerances:** no clipped essential control, focus trap, inaccessible command, or color-only status; task/state names and icons recognizable; selected task and live state remain legible; debugger update within two processed frames; exactly one registration of each dock/inspector/debugger/monitor after every cycle; semantic fingerprints exact; editor interaction p95 no worse than 1.25x the selected-Godot baseline for the same 100-task tree.
- **Allowed differences:** Redot chrome/theme metrics, font rasterization, minor spacing, and intentional branding. Raw pixel equality is not used; missing controls, obscured content, broken focus order, or duplicate registrations are not allowed.
- **Critics:** editor UX/readability lens, lifecycle/undo lens, accessibility/scaling lens, migration/serialization lens, and one unlensed read-only critic.
- **Retest/capture:** repeat both profiles from clean editor settings; save checklists, registration counts, timing JSON, semantic fingerprints, logs, and canonical PNGs under `docs/gamedev/gauntlet/gnt-03/`.
- **Verdict:** `PASS` only with both profiles, all cycles, migration identity, and clean logs. `FAIL` for lifecycle, migration, accessibility, or deterministic UX defects. `BLOCKED` without visible-editor evidence. Failure blocks editor/debugger/migration claims and release. Round cap: 3.

#### GNT-04 - Desktop package, clean install, export, and rights

- **Frozen references:** selected upstream/source/dependency lock (`BLOCKED` until MS-005); Redot Windows/Linux/macOS release identities and required layouts from the porting specification (`OBSERVED`); `.gdextension` manifest (`OBSERVED`, selected-baseline version pending); MIT source license and CC BY 4.0 logo/demo licenses (`OBSERVED`); hosted macOS artifact (`BLOCKED`).
- **Scenario:** build editor and template-release libraries from clean checkouts for all three desktop targets, inspect binaries, create separate core and demo archives twice, install core into an empty Redot project, execute the vertical slice in editor and an exported game, and inspect every archive/export file.
- **Measures and tolerances:** exact architecture and manifest-path match; only approved dynamic dependencies; no absolute build paths, debug runtime, test marker, credential, cache, or unclassified asset; every shipped file maps to a license/notice; two package runs have identical inventory/checksums; clean editor and exported runtime pass; source/version/checksum metadata exact.
- **Allowed differences:** platform extensions, codesigning/notarization metadata, and platform system libraries documented in the audit. Missing binaries/notices, extra editor files in runtime export, or partial desktop packaging are not allowed.
- **Critics:** clean-install lens, native binary/dependency lens, license/attribution lens, export-isolation lens, and one unlensed read-only critic.
- **Retest/capture:** rerun platform CI from locked commits, download fresh artifacts, package twice, scan/install/export, and save inventories, hashes, logs, dependency reports, and captures under `docs/gamedev/gauntlet/gnt-04/`.
- **Verdict:** `PASS` only for the complete desktop matrix and both archives. `FAIL` for any incorrect/missing/extra file or runtime defect. `BLOCKED` while macOS, signing required by the chosen channel, or owner publication authorization is absent. Failure blocks public release. Round cap: 2.

## 12. Risks and open questions

| ID | Risk or open question | Impact | Mitigation / owner | Blocking state and deadline |
| --- | --- | --- | --- | --- |
| RSK-001 | Can the complete `v1.8.0` feature/editor surface be adapted to Redot's 4.5.2 lineage without semantic loss? | Compile, editor, serialization, or runtime failures. | Integrate one coherent v1.8 baseline and adapt only proven engine-facing differences. Owner: Codex. | Mitigated locally: full source builds, demo runs, and 13-case fixtures pass; visible editor/native macOS gates remain. |
| RSK-002 | Editor APIs or resource serialization differ despite API lineage. | Data loss, editor crash, or migration failure. | GNT-01/GNT-03 contract, lifecycle, and semantic fingerprint gates. Owner: Codex. | Mitigated by round-trip/runtime proof; visible editor gate remains. |
| RSK-003 | Demo/logo files are packaged without complete CC BY attribution. | Legal/release failure. | Separate core/demo packages and file-level license inventory. Owner: Codex. | Resolved for the final local archives. |
| RSK-004 | Official Redot API dumping crashes and local API files disagree. | Binding provenance or ABI uncertainty. | Reconcile engine source, Redot C++ API/interface, both artifacts, compile/load/runtime proof, and an accepted ADR. Owner: Codex. | Resolved by accepted API provenance and compile/load/runtime proof. |
| RSK-005 | Upstream native tests are module-oriented while first delivery is GDExtension. | Important semantics may be untested. | Run native tests on selected upstream baseline; map every case; reproduce critical behavior in deterministic extension fixtures. Owner: Codex. | Open; blocks behavior parity. |
| RSK-006 | Windows/Linux/macOS toolchains or native outputs diverge. | Incomplete desktop release. | Same source/API locks, clean platform CI, manifest and dependency audit. Owner: Codex. | Blocked on native macOS runtime; all six local structures pass. |
| RSK-007 | Complete 1.8 feature parity is now required. | A partial backport would not satisfy the authorized product scope. | Merge the full tag, adapt its engine dependencies, and add direct regression coverage. Owner: Codex. | In progress; blocks source publication. |
| RSK-008 | Tags, releases, signing, and notarization remain unauthorized. | Source may be published but no release may be claimed. | Push only the verified branch and request separate release authorization. Owner: DominicBytes. | Source publication resolved; release blocked. |
| RSK-009 | Editor debugger or 200-agent runtime performance regresses. | Poor usability or scalability. | Freeze same-machine baseline and enforce GNT-02/GNT-03 tolerances. Owner: Codex. | Open; blocks relevant parity/release claim. |

No design fog blocks MS-005. The exact source patch and later lanes are deliberately evidence-dependent rather than silently assumed.

### 12.1 v1.8 scope-amendment tasks

| Task | Outcome | Acceptance check |
| --- | --- | --- |
| LIM-022 | Replace the 1.6 feature baseline with exact upstream `v1.8.0` while retaining downstream Redot build/test/package infrastructure. | A source inventory accounts for all 48 non-merge upstream commits; omitted or altered upstream lines map only to a documented Redot incompatibility. |
| LIM-023 | Compile and load the complete v1.8 runtime and editor source against the locked Redot 26.2 binding. | Windows editor and template-release builds complete without unexplained warnings; bounded Redot editor/runtime initialization registers the expected classes and exits cleanly. |
| LIM-024 | Prove the later feature surface, including HSM transition cargo, the reworked task palette/layout, probability/status overlays, and runtime blackboard inspection. | Direct deterministic tests pass for runtime semantics; the visible-editor protocol names and exercises every later editor feature at both required UI profiles. |
| LIM-025 | Rerun the complete BT, blackboard, subtree, custom GDScript, HSM/BTState, resource round-trip, multi-agent, view, monitor, and migration matrix. | All deterministic cases pass with zero suspicious log lines and exact documented semantic results. |
| LIM-026 | Rebuild and audit the desktop/package matrix with `1.8.0+redot.26.2.1` metadata. | Required platform structures, clean installs, deterministic archives, rights inventory, and package/version checks pass; externally blocked native/interactive gates remain explicit. |
| LIM-027 | Publish the verified source update to `dominicbytes/redot-limbo`. | The fork default branch resolves to the tested commit and is clean; no tag, GitHub release, signing, or notarization action occurs. |

## 13. Release plan

- **Version:** `<selected-upstream-version>+redot.26.2.1`; preserve the upstream version and identify the Redot target/revision.
- **Branches:** retain full upstream history; use `upstream/<version>`, `port/redot-26.2`, and `release/<version>+redot.26.2.1` when the owner authorizes the downstream repository.
- **Core artifact:** `addons/limboai/`, Windows/Linux/macOS editor and template-release libraries, manifest/icons, source license/notices, version, installation, compatibility, limitations, migration, and checksums.
- **Demo artifact:** the demo/tutorial content, logo, CC BY 4.0 attribution, core dependency/version requirement, and its own checksums.
- **Source release:** the complete downstream history and exact build/test/package scripts; generated binaries remain release artifacts rather than source commits.
- **Evidence:** source/API/binding/dependency locks, baseline/contract/migration reports, platform build logs, deterministic test JSON, manual editor reports/captures, binary audits, archive inventories, export runs, and Gauntlet verdicts.
- **Distribution gates:** all desktop targets, clean install/export, licenses, docs, control files/workbook, upstream-sync dry run, and GNT-04 pass. A partial local matrix may be labeled test evidence, never a release.
- **Signing:** sign/notarize only when required by the chosen channel. Missing required credentials or hosted tooling is a blocker, not a skipped check.
- **Maintenance:** fetch but do not auto-merge upstream; generate code/dependency/license/API/resource/test impact; update one baseline at a time; rerun the complete claimed matrix.

## 14. Out of scope

- Features introduced after the immutable LimboAI `v1.8.0` tag or unrelated current-master changes.
- A Redot engine-module release until GDExtension parity passes and a required module-only capability is demonstrated.
- C#, .NET, GDExtension language bindings other than the existing C++ implementation, or another engine.
- A GDScript rewrite of native LimboAI systems, a second editor plugin wrapper, or a new AI/event architecture.
- New behavior-tree tasks, HSM features, blackboard semantics, editor redesign, icons, art, audio, or marketing assets.
- Redot engine patches unless an independently reproducible engine defect is proven and handled as a separate upstream issue/decision.
- Mobile, Web, server/headless release packages, double precision, Linux arm64/rv64, Android, or iOS before the desktop single-precision release and explicit scope expansion.
- Bundling the demo/logo into the core archive or shipping any asset whose rights are not classified.
- Creating/pushing a GitHub repository, branch, tag, release, or signing operation without explicit owner authorization.
