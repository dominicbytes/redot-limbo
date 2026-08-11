# Preflight report: LimboAI

## Research scope and date

- Research date: 2026-08-09
- Current execution priority: 5
- Original specification priority: 4
- Target: Redot 26.2 LTS; the program spec identifies Godot API lineage 4.5.2.
- Local source snapshot: GitHub branch master, commit a6f5c7fc11ff80d512dd75c82cfa85724fd8a742
- Original compatibility candidate: v1.6.0, tag 91b22a187f7cd701e25eedd6dcff34179795e687
- Owner-selected feature baseline: v1.8.0, tag 3fbd85118b924d50c10a495ad5c7175028649d77
- Disposition: ADAPT

## Owner-approved scope override

On 2026-08-11, after reviewing the omitted 1.7/1.8 features, the owner
explicitly directed a complete LimboAI 1.8 port that builds on the verified 1.6
Redot work. This overrides the preflight recommendation to stop at the newest
unchanged 4.5-compatible source. The original findings remain valid risk
evidence: v1.8 assumes Godot 4.6 and includes 4.7 compatibility work, so those
dependencies must now be adapted and verified against Redot 26.2 rather than
used to reduce feature scope.

Port behavior trees, blackboards, hierarchical state machines, editor tools, runtime debugger, resources, and GDScript extension points.

## Research questions

1. Which stable release still supports the Godot 4.5 API lineage?
2. What differs between GDExtension and module editions?
3. Which source/demo assets carry separate attribution?
4. Can resource and serialized identifiers remain stable?

## Recommended references

- [Repository](https://github.com/limbonaut/limboai) — Source and support matrix.
- [v1.6.0 tag](https://github.com/limbonaut/limboai/releases/tag/v1.6.0) — 4.5-compatible baseline candidate.
- [README](https://github.com/limbonaut/limboai/blob/master/README.md) — Feature and version matrix.
- [MIT-style license](https://github.com/limbonaut/limboai/blob/master/LICENSE.md) — Source license.
- [Logo license](https://github.com/limbonaut/limboai/blob/master/LOGO_LICENSE.md) — Logo attribution/rights.
- [Stable docs](https://limboai.readthedocs.io/en/stable/) — Supported API and workflows.
- [Latest docs](https://limboai.readthedocs.io/en/latest/) — Newer feature comparison only.
- [Getting LimboAI](https://limboai.readthedocs.io/en/stable/getting-started/getting-limboai.html) — Extension/module installation.
- [Behavior trees](https://limboai.readthedocs.io/en/stable/behavior-trees/introduction.html) — Feature scope.
- [Custom tasks](https://limboai.readthedocs.io/en/stable/behavior-trees/custom-tasks.html) — GDScript extension points.
- [Blackboards](https://limboai.readthedocs.io/en/stable/behavior-trees/using-blackboard.html) — Resource/inspector behavior.
- [HSM](https://limboai.readthedocs.io/en/stable/hierarchical-state-machines/create-hsm.html) — State-machine scope.
- [C# use](https://limboai.readthedocs.io/en/stable/getting-started/c-sharp.html) — Compatibility lane to verify or omit.

## Findings and intended use

- Current master README states that 1.8.x and 1.7.x require Godot 4.6+, while 1.6.x GDExtension releases support 4.4, 4.5, and 4.6. That makes v1.6.0 the strongest release candidate for Redot’s 4.5.2 lineage.
- LimboAI offers a GDExtension and a module; the GDExtension is more convenient but feature-limited. The first Redot delivery should use GDExtension and document any omissions.
- The feature surface includes BehaviorTree/BTPlayer, composite/decorator/action/condition tasks, blackboards, subtrees, debugger/view, LimboState/LimboHSM, BTState integration, and custom GDScript tasks/states.
- The source license is MIT-style, while the demo logo/assets have separate attribution requirements.

## Redot adaptation notes

- Check out v1.6.0 or a verified 4.5-compatible commit, then compare current-master bug fixes for backport candidates.
- Build GDExtension against the exact Redot API first; audit editor docks, inspector plugins, debugger, class docs, and resource registration.
- Create migration fixtures for behavior trees, blackboards, subtrees, custom tasks, HSM scenes, and serialized resources.
- Ship demo/tutorial assets separately if their CC BY or other terms should not be included in the core addon.

## License and attribution obligations

- Retain source license and contributor notices.
- Preserve logo/demo asset attribution from LICENSE_ASSETS.md and LOGO_LICENSE.md.
- Do not imply latest-master feature parity when the 1.6 baseline is selected.

## Rejected or unresolved candidates

- Current master as an automatic baseline: README says it targets Godot 4.6.
- Latest 1.8.x/1.7.x for Redot 4.5.2: direct version evidence rejects them.
- Module-first delivery: unnecessary custom-engine coupling before extension parity.

## Adversarial evidence audit

This is a labeled SELF_REVIEW pass; no independent reviewer was available. Material findings are retained rather than averaged away.

| ID | Lens | Challenged claim | Evidence | Missing proof | Decision impact | Verdict |
|---|---|---|---|---|---|---|
| AUD-LIMBO-01 | identity and provenance | v1.6.0 is a compatible stable candidate. | Upstream support table and tag SHA identify it. | Need inspect exact v1.6.0 source/API and tests. | Determines baseline. | PASS |
| AUD-LIMBO-02 | feature and reference fit | The 1.6 feature set covers the requested AI systems. | README/docs list BT, HSM, blackboards, debugger, and GDScript hooks. | Later-master features may be omitted. | Record parity matrix. | PASS |
| AUD-LIMBO-03 | Redot/API/plugin compatibility | GDExtension will load and editor tooling will work in Redot. | No exact Redot API dump/editor run is available. | Native and editor proof missing. | Blocks implementation claim. | BLOCKED |
| AUD-LIMBO-04 | license and asset rights | Core addon and demo can be redistributed together. | Source license and separate asset/license files exist. | Every demo asset still needs a selected-package audit. | Separate package or notices. | BLOCKED |

## Open risks

- Editor API and resource serialization differences can be more fragile than runtime code.
- Current documentation and master move faster than the target API.
- GitHub downstream fork is not yet created.

## Concrete changes to the implementation plan

- Keep LimboAI fifth in the current execution order after the earlier C++/editor gates.
- Use v1.6.0 as the candidate and publish a later-feature omissions table.
- Make resource round-trip, debugger, and custom GDScript fixtures acceptance gates.

## Preflight gate

ADAPT: the owner-selected v1.8 baseline is identified; its complete Redot
extension/editor/runtime compatibility matrix is reopened and must pass before
the port is called complete.

The source-of-truth workbook in this folder records the evaluated sources, decisions, and risks. No third-party code was executed merely to evaluate it.
