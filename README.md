# Redot LimboAI

Redot LimboAI is a downstream GDExtension port of LimboAI 1.8.0 for Redot
26.2. It provides behavior trees, blackboards, hierarchical state machines,
the behavior-tree editor and debugger, runtime tree views, and typed-GDScript
extension points while preserving the upstream public class and resource names.

The downstream version is `1.8.0+redot.26.2.1`. The source baseline is upstream
commit `3fbd85118b924d50c10a495ad5c7175028649d77`; the exact engine, API,
binding, toolchain, and license hashes are recorded in `UPSTREAM_LOCK.md`.
Upstream 1.8 targets Godot 4.6 and includes 4.7 build compatibility; this
downstream adapts that feature set to Redot 26.2's 4.5.2 API lineage.

## Install

Use the core archive produced by `scripts/package_release.py`:

1. Extract `addons/limboai` into the root of a Redot 26.2 project.
2. Open the project with Redot 26.2 and allow the initial import to finish.
3. Confirm that `BehaviorTree`, `BTPlayer`, `LimboHSM`, and `LimboState` appear
   in the class reference or node/resource selectors.
4. Read `MIGRATION.md` before replacing an existing LimboAI installation.

The core archive is independent of the separately licensed demo and logo. It
contains editor and template-release libraries for Windows x86-64, Linux
x86-64, and macOS universal when the complete desktop gate has passed.
The provided Linux binaries are built on Ubuntu 24.04 and require glibc 2.38
or newer.

## Build from source

The build intentionally does not clone a mutable dependency. Populate
`godot-cpp/` with the exact Redot binding commit in `deps.env`, replace its
`gdextension/extension_api.json` with the verified Redot 26.2 API dump, and
verify the hashes before invoking SCons 4.10.1.

```text
scons --project=<external-project> platform=<windows|linux|macos> target=editor
scons --project=<external-project> platform=<windows|linux|macos> target=template_release
```

Use `arch=x86_64` on Windows and Linux. On a native macOS builder, use
`arch=universal macos_deployment_target=11.0`. Generated libraries and evidence
belong outside this source tree.
The build fails closed when the binding commit, API, interface header, or
selected profile differs from the lock.

## Verification

The deterministic GDExtension fixture covers class registration, blackboards,
resource round trips, core task semantics, cloning, `BTPlayer`, multiple
agents, all four custom-task categories, HSM/`BTState`, `BehaviorTreeView`, and
the 1.8 blackboard runtime-inspection and HSM transition-cargo APIs, plus a
200-agent runtime sample. Run the Python harness tests with:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Platform builds, binary audits, native Redot fixture runs, and clean package
checks are automated by `.github/workflows/redot-desktop.yml`. Interactive
editor, accessibility, and lifecycle checks remain explicit release gates;
they are never inferred from a headless run.

## Scope

This release contains the complete LimboAI 1.8 feature baseline as a desktop,
single-precision GDExtension. It does not include a Redot engine-module build,
C#/.NET support, or mobile/Web binaries. See `COMPATIBILITY.md` and
`LIMITATIONS.md` for the precise contract.

The adopted 1.8 editor surface includes the foldable task palette, a dedicated
favorites section, modern flat-button layout, probability overlays, status
highlight fixes, and debugger-backed blackboard runtime inspection. HSM event
cargo is included and exercised by the deterministic runtime fixture.

## Upstream and licenses

LimboAI was created by Serhii Snitsaruk and contributors. Source code is
distributed under the MIT-style terms in `LICENSE.md`. The upstream logo and
demo graphics are CC BY 4.0 and are intentionally excluded from the core
archive; their notices travel with the separate demo package. Bundled demo
fonts retain the SIL Open Font License 1.1. See `THIRD_PARTY_NOTICES.md` and
`demo/THIRD_PARTY_FONTS.md`.

Upstream project: https://github.com/limbonaut/limboai
