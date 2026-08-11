# Migration to Redot LimboAI

## From upstream LimboAI 1.8.x on Godot

1. Commit or back up the project, including all `.tres`, `.tscn`, and custom
   task/state scripts.
2. Close the editor and remove the previous `addons/limboai` directory.
3. Install the complete Redot LimboAI core package. Do not mix libraries or a
   manifest from another build.
4. Open the project in Redot 26.2 and wait for import to finish.
5. Resolve script parse errors before resaving resources. Custom scripts keep
   the upstream 1.8 `BTAction`, `BTCondition`, `BTDecorator`, `BTComposite`, and
   `LimboState` base classes.
6. Open representative behavior trees and HSM scenes, run them, and inspect
   blackboards and the debugger before committing Redot-generated metadata.
7. Export a test build and confirm that the template-release library loads.

The port preserves the upstream 1.8 public identities. It does not perform an
automatic project rewrite, and the deterministic fixture is not a substitute
for backing up project-specific content.

## From LimboAI 1.6.x or 1.7.x

Treat this as both an upstream LimboAI upgrade and an engine migration. Review
the upstream 1.7/1.8 changes, especially the modern task palette, debugger
blackboard inspection, HSM event cargo, editor ownership fixes, and upgraded
demo serialization. Validate copied project resources before allowing Redot to
resave them. The port includes those features; no downgrade conversion is
required.

## From versions newer than 1.8.0 or current master

Automatic downgrade migration is unsupported. Later source may contain
classes or serialized properties absent from the immutable 1.8.0 tag. Compare
the exact resources and use an owner-reviewed conversion before resaving them.

## Troubleshooting

- A missing class usually means the wrong platform library, an incomplete
  addon directory, or a binding/API mismatch. Reinstall the whole core archive.
- A failed native load is a hard error. Record the full Redot log and compare
  the engine and artifact hashes with `UPSTREAM_LOCK.md`.
- If a migrated animation does not play, verify that its `AnimationPlayer`
  library dictionary survived serialization before resaving the scene.
- Do not copy `.godot`, build caches, API dumps, or fixture output between
  projects.
