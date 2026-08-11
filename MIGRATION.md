# Migration to Redot LimboAI

## From LimboAI 1.6.x on Godot

1. Commit or back up the project, including all `.tres`, `.tscn`, and custom
   task/state scripts.
2. Close the editor and remove the previous `addons/limboai` directory.
3. Install the complete Redot LimboAI core package. Do not mix libraries or a
   manifest from another build.
4. Open the project in Redot 26.2 and wait for import to finish.
5. Resolve script parse errors before resaving resources. Custom scripts should
   continue to extend the same `BTAction`, `BTCondition`, `BTDecorator`,
   `BTComposite`, or `LimboState` base class.
6. Open representative behavior trees and HSM scenes, run them, and inspect
   the debugger before committing Redot-generated metadata.
7. Export a test build and confirm that the template-release library loads.

The port preserves 1.6.0 resource identities and does not perform an automatic
format rewrite. The oracle fixture verifies save/load behavior, task order,
blackboard values, custom scripts, and BT/HSM composition for its named cases.
That evidence is not a substitute for backing up project-specific content.

## From LimboAI 1.7, 1.8, or current master

Downgrade migration is unsupported. Those versions target newer APIs and may
contain classes or serialized properties absent from 1.6.0. Migrate through an
owner-reviewed content conversion only after comparing the exact resources;
do not let Redot resave unknown fields destructively.

## Troubleshooting

- A missing class usually means the wrong platform library, an incomplete
  addon directory, or a binding/API mismatch. Reinstall the whole core archive.
- A failed native load is a hard error. Record the full Redot log and compare
  the engine and artifact hashes with `UPSTREAM_LOCK.md`.
- Do not copy `.godot`, build caches, API dumps, or fixture output between
  projects.
