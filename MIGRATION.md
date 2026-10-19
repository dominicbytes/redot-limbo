# Migration to Redot LimboAI

## From upstream LimboAI 1.8.0 on Godot

1. Commit or back up the project, including all `.tres`, `.tscn`, and custom
   task/state scripts.
2. Close the editor and remove the previous `addons/limboai` directory.
3. Install the complete Redot LimboAI core package. Do not mix libraries or a
   manifest from another build.
4. Open the project in a supported Redot 26.2 or 26.3 runtime and wait for import to finish.
5. Resolve script parse errors before resaving resources. Custom scripts keep
   the upstream 1.8.0 `BTAction`, `BTCondition`, `BTDecorator`, `BTComposite`, and
   `LimboState` base classes.
6. Open representative behavior trees and HSM scenes, run them, and inspect
   blackboards and the debugger before committing Redot-generated metadata.
7. Export a test build and confirm that the template-release library loads.

The port preserves the upstream 1.8.0 public identities. It does not perform an
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
the exact resources and use a project-specific conversion before resaving them.

## Troubleshooting

- A missing class usually means the wrong platform library, an incomplete
  addon directory, or a binding/API mismatch. Reinstall the whole core archive.
- A failed native load is a hard error. Record the full Redot log and compare
  the engine and artifact hashes with `UPSTREAM_LOCK.md`.
- If a migrated animation does not play, verify that its `AnimationPlayer`
  library dictionary survived serialization before resaving the scene.
- Do not copy `.godot`, build caches, API dumps, or fixture output between
  projects.

## From Redot 26.2 to 26.3

Use `26.3.stable.official.85e520394` with the complete addon, including the
patched libraries. The package version remains `1.8.0+redot.26.2.1`; the build
ABI still comes from 26.2. Existing behavior trees and HSM/blackboard resources
retain their public identities. Back up the project before allowing the new
engine to import or resave it, then run representative trees and exported-game
checks with the release library.

Struct is available only on 26.3. New BBVariant/plan defaults can be empty
Struct values; define custom fields in 26.3 scripts. Keep Struct resources and
syntax out of any project that must still open on 26.2. See `LIMITATIONS.md`
for the temporary headless-editor shutdown issue and its exact import-only CI
gate. A runtime error or unexpected warning remains a failure on either engine.

## From Redot 26.3 back to 26.2

Back up the project and convert or remove every Struct value and declaration
on 26.3 before opening it on 26.2, including parameters bound to blackboard
variables. A saved Struct value fails the 26.2 text parser with an unexpected
`Struct` identifier and does not load. A bound-mode, type-only BBVariant can
load with `type = 39` because it contains no Struct syntax. Its declaration is
preserved with an unsupported-type error; switching to saved-value mode leaves
its native value editor unavailable rather than converting the declaration to
Nil. Neither outcome provides downgrade conversion. Do not resave failed or
unsupported resources on 26.2; restore the backup or finish conversion on 26.3.
