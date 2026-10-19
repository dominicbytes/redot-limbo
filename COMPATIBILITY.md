# Compatibility

## Source-port build contract

| Component | Locked input or build target |
| --- | --- |
| Build API engine | `26.2.stable.official.4f5b14aba` |
| Supported runtimes | `26.2.stable.official.4f5b14aba`, `26.3.stable.official.85e520394` |
| API lineage | Godot 4.5.2-compatible GDExtension API |
| Precision | Single |
| LimboAI baseline | Complete upstream `v1.8.0` plus documented Redot adaptations |
| Windows | x86-64 editor and template-release libraries |
| Linux | x86-64 editor and template-release libraries; glibc 2.38 or newer |
| macOS | Universal x86-64 + arm64 editor and template-release frameworks |
| Language extension points | Typed GDScript |

Only artifacts built from the full hashes in `UPSTREAM_LOCK.md` belong to this
contract. A matching API surface is not sufficient on its own: the Redot
build engine identity, Redot C++ binding revision, reviewed binding patch,
interface header, and generated API JSON must match the build lock. Runtime
identities are pinned separately; 26.3 uses the same 26.2-built libraries.

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

## Variant types on both runtimes

BBVariant and both blackboard editor type menus discover the running engine's
type count through `Variant::get_type_name`, stopping at its empty sentinel.
Both supported engine sources return an empty name outside the contiguous type
catalog, without logging an error. This queries the engine through the existing
GDExtension interface and does not guess a count from version strings or probe
conversion tables with an unsupported index. The GDScript `type_string` utility
has different validation and is not used for discovery.

26.2 retains its 39-entry catalog. 26.3 includes Struct (39), with an empty
Struct default constructed through `variant_construct`. The native 26.3
inspector supplies its Struct field editor; custom layouts and field names
still come from script. PackedVector4Array defaults are empty arrays on both
engines, and the array predicate ends at PackedVector4Array, excluding Struct.
The binding patch safely clears both PackedVector4Array and appended types.

## Not implied

- The binaries are not interchangeable with Godot engine binaries.
- Changes after upstream `v1.8.0` or current-master resources are not claimed
  compatible.
- Mobile, Web, server, double-precision, C#/.NET, or engine-module support is
  not part of this source port.
- A source version or workflow artifact does not establish a published binary
  release or validate every platform/architecture combination.

## Validation scope

Desktop CI builds and audits the listed editor and template-release targets,
runs the complete headless fixture with both libraries on both pinned runtimes,
runs the 23-check editor regression during editor import, compares shared
semantic cases across engines, and compares two
independently assembled core/demo archives. These are workflow checks, not a
claim that a particular hosted workflow run passed for this source revision.
The Struct case is explicitly skipped with a record on 26.2, and its separate
script text is parsed only on 26.3. Comparison validates each complete inventory
before excluding the engine-conditional difference; shared cases remain strict.

Extracted-distribution execution, visible editor authoring, accessibility,
repeated editor lifecycle checks, and native game exports require separate
validation. Package-byte equality does not establish clean-install execution;
forcing a template-release library in a fixture is not a native game export.
See `LIMITATIONS.md` for coverage and performance boundaries.
