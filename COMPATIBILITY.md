# Compatibility

## Supported contract

| Component | Supported value |
| --- | --- |
| Redot | `26.2.stable.official.4f5b14aba` |
| API lineage | Godot 4.5.2-compatible GDExtension API |
| Precision | Single |
| LimboAI baseline | `1.6.0` plus documented isolated fixes |
| Windows | x86-64 editor and template-release libraries |
| Linux | x86-64 editor and template-release libraries; glibc 2.38 or newer |
| macOS | Universal x86-64 + arm64 editor and template-release frameworks |
| Language extension points | Typed GDScript |

Only artifacts built from the full hashes in `UPSTREAM_LOCK.md` belong to this
contract. A matching API surface is not sufficient on its own: the Redot
engine identity, Redot C++ binding revision, interface header, and generated
API JSON must all match.

## Compatibility promises

- Upstream 1.6.0 class names, methods, signals, settings, resource types,
  serialized identifiers, and GDScript base classes are preserved unless a
  documented Redot limitation says otherwise.
- Godot-authored 1.6.0 behavior-tree resources used by the deterministic
  oracle load and execute in Redot with matching semantic fingerprints.
- Debug mappings load editor libraries; exported projects load only
  template-release libraries.

## Not implied

- The binaries are not interchangeable with Godot engine binaries.
- LimboAI 1.7, 1.8, or current-master resources are not claimed compatible.
- Mobile, Web, server, double-precision, C#/.NET, or engine-module support is
  not part of this release.
- A platform is not release-supported until its native CI, binary audit,
  clean-install, and runtime/export evidence pass.
