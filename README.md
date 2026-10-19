# Redot LimboAI

Redot LimboAI is a downstream GDExtension port of LimboAI 1.8.0 for Redot
26.2 and 26.3. It provides behavior trees, blackboards, hierarchical state machines,
the behavior-tree editor and debugger, runtime tree views, and typed-GDScript
extension points while preserving the upstream public class and resource names.

The downstream version is `1.8.0+redot.26.2.1`. The source baseline is upstream
commit `3fbd85118b924d50c10a495ad5c7175028649d77`; the exact engine, API,
binding, toolchain, and license hashes are recorded in `UPSTREAM_LOCK.md`.
Upstream 1.8 targets Godot 4.6 and includes 4.7 build compatibility; this
downstream adapts that feature set to Redot 26.2's 4.5.2 API lineage.

## Install

Use the core archive produced by `scripts/package_release.py`:

1. Extract `addons/limboai` into the root of a supported Redot 26.2 or 26.3 project.
2. Open the project with the pinned Redot 26.2 or 26.3 runtime and allow the initial import to finish.
3. Confirm that `BehaviorTree`, `BTPlayer`, `LimboHSM`, and `LimboState` appear
   in the class reference or node/resource selectors.
4. Read `MIGRATION.md` before replacing an existing LimboAI installation.

The core archive is independent of the separately licensed demo and logo. It
contains editor and template-release libraries for Windows x86-64, Linux
x86-64, and macOS universal as desktop build targets.
The provided Linux binaries are built on Ubuntu 24.04 and require glibc 2.38
or newer.

## Build from source

The build intentionally does not clone a mutable dependency. Populate
`godot-cpp/` with the exact Redot binding commit in `deps.env`, replace its
`gdextension/extension_api.json` with the verified Redot 26.2 API dump, and
apply the reviewed binding patch before invoking SCons 4.10.1. Runtime 26.3
uses the same libraries; builds always use the locked 26.2 API.

```text
python scripts/prepare_binding.py --apply
scons --project=<external-project> platform=<windows|linux|macos> target=editor
scons --project=<external-project> platform=<windows|linux|macos> target=template_release
```

Use `arch=x86_64` on Windows and Linux. On a native macOS builder, use
`arch=universal macos_deployment_target=11.0`. Generated libraries and evidence
belong outside this source tree.
The build fails closed when the binding commit, patch/source hashes, effective API, interface header, or
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

Platform builds, binary audits, and headless fixtures on built libraries run in
`.github/workflows/redot-desktop.yml`; CI tests both pinned runtimes with both libraries, runs the editor regression,
and compares runtime semantics and assembled package bytes. See `LIMITATIONS.md`
for the temporary 26.3 editor-import shutdown exception.
Extracted-package execution, visible editor/accessibility/lifecycle checks, and
native game exports require separate validation.

## Scope

This source port contains the complete LimboAI 1.8 feature baseline as a desktop,
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
fonts retain SIL OFL 1.1; see `THIRD_PARTY_NOTICES.md`. Font notices are at
`demo/THIRD_PARTY_FONTS.md` in source or `THIRD_PARTY_FONTS.md` in the demo ZIP.

Upstream project: https://github.com/limbonaut/limboai

## Notes

I vibe coded this in GPT Sol 5.6. Use at your own risk. Actual programmers are welcome to submit PR's and feedback.

## About Dominic Bytes

Greetings! I am Dominic Bytes, the synth walker. I hail from the distant future. Where brains occupy robot bodies, time travel is a trip to the corner store, and the neon glow of our attire is powered by the light of our souls. Join me on a 1.21 gigawatt powered journey of chill vibes with gaming, anime, movies, and more!

- [Website](https://dominicbytes.carrd.co/)
- [X](https://x.com/DominicBytes)
- [Twitch](https://www.twitch.tv/dominicbytes)
- [YouTube](http://www.youtube.com/@DominicBytes)
- [Kick](https://kick.com/dominicbytes)
