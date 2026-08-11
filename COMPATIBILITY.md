# Compatibility

## Supported contract

| Component | Supported value |
| --- | --- |
| Redot | `26.2.stable.official.4f5b14aba` |
| API lineage | Godot 4.5.2-compatible GDExtension API |
| Precision | Single |
| LimboAI baseline | Complete upstream `v1.8.0` plus documented Redot adaptations |
| Windows | x86-64 editor and template-release libraries |
| Linux | x86-64 editor and template-release libraries; glibc 2.38 or newer |
| macOS | Universal x86-64 + arm64 editor and template-release frameworks |
| Language extension points | Typed GDScript |

Only artifacts built from the full hashes in `UPSTREAM_LOCK.md` belong to this
contract. A matching API surface is not sufficient on its own: the Redot
engine identity, Redot C++ binding revision, interface header, and generated
API JSON must all match.

## Compatibility promises

- Upstream 1.8.0 class names, methods, signals, settings, resource types,
  serialized identifiers, editor features, and GDScript base classes are
  preserved unless a documented Redot limitation says otherwise.
- The 1.8 blackboard runtime-inspection surface and HSM transition-event cargo
  execute under Redot and are covered by deterministic fixture cases.
- The upstream 1.8 task-palette, favorites, modern layout, probability/status
  rendering, debugger, and safety changes remain in the selected source.
- Representative behavior-tree and HSM resources save, reload, and execute in
  Redot with deterministic semantic fingerprints.
- Debug mappings load editor libraries; exported projects load only
  template-release libraries.

## Documented Redot adaptations

- Five editor plugin references use explicit `Ref<T>` construction required by
  the locked Redot C++ binding.
- Task-palette flat buttons fall back to Redot's modern style because Redot
  26.2 does not expose Godot 4.6's `interface/theme/style` setting.
- Five upstream 4.6 demo scenes serialize animation libraries using the
  equivalent 4.5-compatible dictionary form accepted by Redot 26.2.
- Three plan-editor property hints remain API-version guarded, and the build,
  manifest, version, dependency, audit, and package paths are Redot-specific.

## Not implied

- The binaries are not interchangeable with Godot engine binaries.
- Changes after upstream `v1.8.0` or current-master resources are not claimed
  compatible.
- Mobile, Web, server, double-precision, C#/.NET, or engine-module support is
  not part of this release.
- A platform is not release-supported until its native CI, binary audit,
  clean-install, and runtime/export evidence pass.
